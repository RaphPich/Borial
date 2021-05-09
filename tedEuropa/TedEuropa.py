import requests
from datetime import date
import json
import os
from bs4 import BeautifulSoup

"PC=[comp+or+core]"

class TedEuropa:
    def __init__(self,formData={'startDate':False,'keywords':False,'categorie':False}):
        self.url = "https://ted.europa.eu/"
        self.proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }

        self.countries= json.load(open("country.json","r"))

        self.data = self.createRequest(formData)
        self.annonces = []
        self.s = requests.Session()
        self.s.proxies.update(self.proxies)
        self.pages = False

    def cpvCode(self,s):
        import ast
        r = s.get("https://ted.europa.eu/TED/webapp/api/refData/_retrieveTree?field=CPV&languageCode=fr&hideAllCodes=false&filter=",proxies = self.proxies)
        return ast.literal_eval(r.text)

    def createRequest(self,formData):
        
        data = { "action": "search",
        "lgId": "fr",
        "quickSearchCriteria":"",
        "expertSearchCriteria.searchScope" : "CURRENTLY_ACTIVE",
        "expertSearchCriteria.query":""}

        if formData['startDate']:
            data['expertSearchCriteria.query'] = "PD=["+"".join(formData['startDate'].rsplit("/").reverse()) + "+<>+"
            if formData['endDate']:
                data['expertSearchCriteria.query']+= "".join(formData['endDate'].rsplit("/").reverse())
            else:
                from datetime import date
                data['expertSearchCriteria.query']+= date.today().strftime("%Y%m%d") + "]"
        else:
            import datetime
            dateNow=datetime.datetime.now() - datetime.timedelta(days=3*365)
            data['expertSearchCriteria.query'] = "PD=[{}+<>+{}]".format(dateNow.strftime("%Y%m%d"),datetime.datetime.now().strftime("%Y%m%d"))
        
        if formData['keywords']:
            if data["expertSearchCriteria.query"]!="":
                data['expertSearchCriteria.query'] += "+AND+"
            data['expertSearchCriteria.query']+= "("+"+AND+".join(["FT=[{}]".format(elem) for elem in formData['keywords'].rsplit(" ")])+")"
        
        if formData['categorie']:
            with open(os.path.dirname(os.path.abspath(__file__))+"/_retrieveTree.json",'r') as file:
                categories = json.load(file)
                for line in categories:
                    if line['text'] == formData['categorie']:
                        data['expertSearchCriteria.query']+= "+AND+PC=[{}]".format(line['code'])
        return data

    def scrapAllTed(self):
        with open(os.path.dirname(os.path.abspath(__file__))+"/_retrieveTree.json",'r') as file:
            categories = json.load(file)
        for k,line in enumerate(categories):
            if not "{}-data.json".format(line['code']) in os.listdir(os.path.dirname(os.path.abspath(__file__))+"/"):
                print("Doing {} {}/{}".format(line['text'],k,len(categories)))
                self.data['expertSearchCriteria.query'] = "PC=[{}]".format(line['code'])
                self.scrap()
                with open(os.path.dirname(os.path.abspath(__file__))+"/{}-data.json".format(line['code']),"w+") as file:
                    json.dump(self.annonces,file)  

    def scrapAnnonce(self,link):
        link = link.replace('TEXT','DATA')
        r = requests.get(self.url+link,proxies = self.proxies)
        soup = BeautifulSoup(r.text,'html.parser')
        soup = soup.find('table',{"class":"data"})
        annonceData={}
        for tr in soup.findAll('tr'):
            line = tr.findAll('td')
            if len(line)==2:
                annonceData[' '.join(line[0].text.split())] = ' '.join(line[1].text.split())
        return annonceData

    def pageNumbers(self,soup):
        nb = []
        try:
            soup = soup.find("div",{"class":"pagelinks"})
            for a in soup.findAll("a",href = True):
                nb.append(int(a['href'].rsplit("=")[-1]))
            return max(nb)
        except:
            return False

    def scrapPage(self,soup):
        soup = soup.find('tbody')
        for tr in soup.findAll('tr'):
            self.annonces.append({"nom" :tr.find("span",{"class":"bold"}).text,
                "pays":tr.find("td",{"class":None}).text,
                "Date de publication":tr.findAll("td",{"class":"nowrap"})[2].text.replace(" ","").replace("\n",""),
                "Date limite":tr.findAll("td",{"class":"nowrap"})[3].text.replace(" ","").replace("\n",""),
                "lien":self.url+tr.find("a",href=True)["href"],
                "description":self.scrapDescription(tr.find("a",href=True)["href"])})

    def scrapDescription(self,link):
        r = requests.get(self.url+link,proxies = self.proxies)
        soup = BeautifulSoup(r.text,'html.parser')
        return soup.find("div",{"class":"DocumentBody"}).text

    def scrap(self):
        r = self.s.post(self.url+"TED/search/expertSearch.do",data = self.data)
        soup = BeautifulSoup(r.text,'html.parser')
        self.scrapPage(soup)
        self.pages = self.pageNumbers(soup)

        if self.pages:
            for k in range(2,self.pages+1):
                r = self.s.get(self.url+"TED/search/searchResult.do?page={}".format(k))
                soup = BeautifulSoup(r.text,'html.parser')
                self.scrapPage(soup)

if __name__ == "__main__":
    #formData = {'keywords':"ordinateur","startDate":False}
        
    client = TedEuropa()
    client.scrapAllTed()
    #client.scrap()


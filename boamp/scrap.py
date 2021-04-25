import requests
from bs4 import BeautifulSoup
import csv
import queue
import sys
import json
import PyPDF2
import os

data = {"descripteur[]":"mc162",
        "datemiseenligne": 6}


class Boamp:
    def __init__(self,formData):

        self.url = "https://www.boamp.fr"

        self.proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
        self.data = {"estrecherchesimple" : "1",
            "typeavis" :  "5",
            "datemiseenligne": 6
        }
        if formData["keywords"]:
            self.data["fulltext"]=formData["keywords"]

        if formData['categorie']:
            with open(os.path.dirname(os.path.abspath(__file__))+"/categories.json") as file:
                self.categories = json.load(file)[formData['categorie']]['BOAMP']

        self.annonces = []
        self.s = requests.Session()
        self.s.proxies.update(self.proxies)
        self.pages = 0

    def scrapCategories(self):
        for categorie in self.categories:
            self.data["descripteur[]"] = categorie
            self.scrap()

    def scrap(self):
        r = self.s.post(self.url+"/avis/liste",data=self.data,verify=False)
        soup = BeautifulSoup(r.text,'html.parser')
        self.pages = self.nbPages(soup)
        self.getAnnonceBoamp(soup = soup)

        if self.pages>1:
            for k in range(2,self.pages+1):
                    self.getAnnonceBoamp(k=k)

    def nbPages(self,soup):
        pages = []
        newSoup = soup.find("ul",{"class":"pagination"})
        try:
            for elem in newSoup.findAll("a"):
                try:
                    pages.append(int(elem["title"].rsplit(" ")[-1]))
                except:
                    pass
            return max(pages)
        except:
            return 1

    def getAnnonceBoamp(self,k=None,soup=False):
        if not soup:
            r = self.s.get(self.url+"/avis/page?page="+str(k),verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
        soup = soup.find("form",{"id":"results"})
        for elem in soup.findAll("li"):
            try:
                self.annonces.append({"nom":elem.find("h3").text,
                                 "lien":self.url+elem.find("a")['href'],
                                 "Lieux":elem.find("p",{"class":"avis-geo"}).text.replace("Dépt. :",""),
                                 "Publication":elem.find("p",{"class":"date-publishing"}).text.rsplit(" ")[-1],
                                 "Reponse":elem.find("p",{"class":"date-response"}).text.rsplit(" ")[-1]})
            except Exception as e: 
                print(e)

    def getDescription(self,soup):
        try:
            link = requests.get(self.url+soup.find("a",{'class':"btn-avis-download"})["href"],proxies = self.proxies)
            with open('pdfFile/'+soup.find("a",{'class':"btn-avis-download"})["href"].rsplit("/")[-1]+'.pdf', 'wb') as f:
                f.write(link.content)
            soup = soup.find("div",{"class":"row row-detail-avis"})
            return soup.text
        except:
            return ""

    def scrapAll(self):
        for line in open(os.path.dirname(os.path.abspath(__file__))+"/description.txt").read():
            formData['categorie']


def scrapPdf():
    listPdf = os.listdir("pdfFile/")
    print(listPdf[0])
    pdfFileObj = open('pdfFile/'+listPdf[0], 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    print(pdfReader.numPages)
    pageObj = pdfReader.getPage(0)


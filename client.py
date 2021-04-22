#import tedEuropa as te
from boamp import Boamp
from tedEuropa import TedEuropa
from datetime import datetime
from flask import request

class Client:
	def __init__(self,request):

		self.formData = {"keywords":request.form['keywords'],
				"startDate":request.form['dateStart'],
				"endDate":request.form['dateEnd']
				"categorie":request.form['categorie']}

		for key,value in self.formData.items():
			if value == "":
				self.formData[key] = False

		self.proxies = {
		    'http': 'socks5://127.0.0.1:9050',
		    'https': 'socks5://127.0.0.1:9050'
		}

		self.boamp = Boamp(self.formData)
		self.tedEuropa = TedEuropa(self.formData)

	def scrap(self):

		start = datetime.now()
		self.tedEuropa.scrap()
		delta = datetime.now()-start 
		print("tedEuropa : {} seconds".format(delta.seconds))
		print(self.tedEuropa.annonces)
		
		start = datetime.now()
		self.boamp.scrap()
		delta = datetime.now()-start 
		print("Boamp : {} seconds".format(delta.seconds))
		print(self.boamp.annonces)
		
		#self.data = boamp.getAllAnnoncesBoamp(self.formData) 
		#self.data+=te.scrapTedEuropa(self.formData)

	def data(self):
		return self.tedEuropa.annonces +self.boamp.annonces
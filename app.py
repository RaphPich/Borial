from client import Client
import time
from flask import Flask, render_template, request
app = Flask(__name__)

proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}

"""
@app.route('/',methods = ['GET'])
def show_index_html():
	return render_template('index.html')
"""
@app.route('/',methods = ['GET','POST'])
def contact():
	if request.method == 'POST':
		client = Client(request)
		client.scrap()
		return render_template("result.html",result=client.data())
		#return "<br>".join([te.url+elem for elem in te.scrap.scrapTedEuropa(formData)]) + "<br>".join([boamp.url+elem["lien"] for elem in boamp.getAllAnnoncesBoamp(formData)])
	elif request.method == 'GET':
		return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True,port = 8000)

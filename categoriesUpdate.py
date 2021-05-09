import json
import pandas as pd

with open("boamp/categories.json",'r') as file:
	data=  json.load(file)
boampCategories = []

with open("descSave.txt",'r') as file:
	boampCategories = [{line.rsplit("/")[0]:line.rsplit("/")[1].rstrip()} for line in file]

df = pd.DataFrame(columns = [data.keys()])

if __name__ == "__main__":
	print(df)
	for line in boampCategories:
		print(line)
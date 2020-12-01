import csv
import logging

logging.basicConfig(filename='app.py', filemode='w')

path = '/Users/reidrelatores/PycharmProjects/zillow/'
filename = 'uszips.csv'

with open(filename, newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

zip_list = []
for i in data:
    k = []
    k.append(i[0])
    k.append(i[3])
    k.append(i[4])
    zip_list.append(k)

logging.error(zip_list)
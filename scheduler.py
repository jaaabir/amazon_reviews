from scraper import *
from selenium import webdriver
import pickle 
import luigi
import pandas as pd 
from time import time
from pgdb import Pgdb
import sys

# print(sys.path)
# sys.path.insert(0, )
class ScrapReviews(luigi.Task):

    def output(self):   
        return luigi.LocalTarget('amazon_reviews.pkl')
    
    def run(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        reviews = {}

        start = time()
        with webdriver.Chrome( executable_path = 'chromedriver.exe', options = options) as driver:
            cates = ['laptop']
            for cate in cates:
                prods = get_products(cate, driver)
                res = get_reviews(prods, cate, driver)
                reviews.update(res)
        
        end = time()
        print(f'Total time taken to scrap the data :====> {(end - start) / 60} mins')

        with open('amazon_reviews', 'wb') as file:
            pickle.dump(reviews, file)
        


class CleanFile(luigi.Task):

    def output(self):
        return luigi.LocalTarget('amazon_reviews_cleaned.pkl')

    def run(self):
        with open('amazon_reviews', 'rb') as file:
            reviews = pickle.load(file)
        
        cleaned_reviews = {}
        cleaned_reviews['product_name'] = []
        cleaned_reviews['product_category'] = []
        cleaned_reviews['review'] = []

        for pid in reviews.keys():
            rev = reviews[pid]['reviews']
            for r in rev:
                if r != '':
                    r = r.replace('\n',' ')
                    cleaned_reviews['product_name'].append(reviews[pid]['product_name'])
                    cleaned_reviews['product_category'].append(reviews[pid]['product_category'])
                    cleaned_reviews['review'].append(r)

        with open('amazon_reviews_cleaned', 'wb') as file:
            pickle.dump(cleaned_reviews, file)

class SaveTodb(luigi.Task):
        
    def run(self):
        # some db code 
        with open('amazon_reviews_cleaned', 'rb') as file:
            reviews = pickle.load(file)

        db = Pgdb(db = 'reviews', user = 'postgres', passwd = 'postgres123', table = 'details')
        # query = 'product_name varchar(300), product_category varchar(100), review varchar(10000)'
        # db.createTable('details', query)
        n = len(reviews['product_name'])
        for pid in range(n):
            pname = reviews['product_name'][pid]
            pcate = reviews['product_category'][pid]
            preview = reviews['review'][pid]
            # for r in preview:
            values = (pname, pcate, preview)
            db.insert(values)

        db.close()


class SaveToCsv(luigi.Task):
    
    def output(self):
        return luigi.LocalTarget('amazon_reviews.csv')

    def run(self):
        db = Pgdb(db = 'reviews', user = 'postgres', passwd = '******', table = 'details')
        values = db.fetchall()
        details = {
            'product_name' : [],
            'product_category' : [],
            'reviews' : []
        }

        for pname, pcate, rev in values:
            details['product_name'].append(pname)
            details['product_category'].append(pcate)
            details['reviews'].append(rev)
        
        db.close()

        df = pd.DataFrame(details)
        df.to_csv('amazon_reviews.csv', index= False)

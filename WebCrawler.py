import sys
import urllib
import re
import requests
import tldextract
import datetime
from bs4 import BeautifulSoup
from urlparse import urljoin

processors = {}

def process_url(url):
    extract = tldextract.extract(url)
    stamp = datetime.datetime.now()
    if extract.domain in processors:
        return {'status':True, 'date': stamp.strftime("%B %d, %Y, %H:%M:%S"), 'data': processors[extract.domain](url=url).crawl_procedure()}
    else:
        return {'status':False, 'Error':"URL not recognized" }
          
        
class Crawler(object):
    
    def __init__(self, url = None, domain = None):
        self.visited = []
        self.URLS = []
        self.url = url
        self.domain = domain
        
        self.request = requests.get(self.url)	
        self.soup = BeautifulSoup(self.request.text)
        
    def filter_product_urls(self, link):
        return None 
    def get_product(self):
        return None
    def get_image(self):
        return None
    def get_price(self):
        return None
    def get_description(self):
        return None                
           
    def crawl_procedure(self):
        self.products = {}
        self.URLS.append(self.url)
        while len(self.URLS) > 0:
            try:
                self.html = requests.get(self.URLS[0]).content
            except:
                print self.URLS[0]
            self.links = self.soup.find_all('a', {'href' : True})
            
            self.URLS.pop(0)
            print len(self.URLS)
            for self.link in self.links:
                self.link = self.link.get('href')
                self.product_link = self.filter_product_urls(self.link)
                if self.product_link and self.product_link not in self.visited:
                    self.URLS.append(self.product_link)
                    self.visited.append(self.product_link)
                    
                    self.request = requests.get(self.product_link)	
                    self.soup = BeautifulSoup(self.request.text)
                    
                    self.product = self.get_product(self.soup)
                    self.image = self.get_image(self.soup)
                    self.price = self.get_price(self.soup)
                    self.description = self.get_description(self.soup)
                    
                    self.products[self.product_link] = {'product':self.product, 'image':self.image, 'price':self.price, 'description': self.description}
        return self.products
        
             

class WhippingPost(Crawler): 
    
    def filter_product_urls(self, url):
        self.product_link = False
        self.absolute_link = urljoin('http://www.whippingpost.com/', url)
        self.possible_product_link = re.search(r'http://www.whippingpost.com/collections/all/products/\S+', self.absolute_link)
        if self.possible_product_link:
            self.product_link = self.possible_product_link.group()
        return self.product_link
        
    def get_product(self, link):
        result = link.find('meta', {'property':'og:title'})['content']
        return result if result else None
    def get_image(self, link):
        result = 'https:'+link.find('meta', {'property':'og:image'})['content']
        return result if result else None 
    def get_description(self, link):
        result = link.find('meta', {'property':'og:description'})['content']
        return result if result else None    
    def get_price(self, link):
        result = link.find('span', {'class':'current_price'}).text.strip()           
        return result if result else None
            
processors['whippingpost'] = WhippingPost

class Mango(Crawler):
    
    def filter_product_urls(self, url):
        self.product_link = False
        self.absolute_link = urljoin('http://shop.mango.com/', url)
        self.product_id = re.findall(r'http://shop.mango.com/\S+(id=\d{4,10})\S+', self.absolute_link)
        if self.product_id:
            self.url_len = self.absolute_link.find(self.product_id[0])+len(self.product_id[0])
            return self.absolute_link[:self.url_len]  
            
processors['mango'] = Mango
                    
                               
def main():
    url = str((sys.argv)[1])
    if url and len(sys.argv) == 2:
        print process_url(url)
    else:
        print "error"
 
if __name__ == '__main__':
    main()

 
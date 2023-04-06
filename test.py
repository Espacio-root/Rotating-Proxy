from checker_v2 import checker
from rotation import Rotation
import time

if __name__ == '__main__':
    
    # proxy_checker = checker()
    # proxy_checker.run()

    while True:
        sites = ['https://books.toscrape.com/', 'https://quotes.toscrape.com/', 'https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops']
        rotation = Rotation(proxy_file='valid_http_proxies.csv')
        
        print(rotation.get_proxy())
        time.sleep(1)
        


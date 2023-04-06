import threading
import time
import pandas as pd
import queue
import requests
import geoip2.database
import os

class checker:
    
    def __init__(self, website='http://ipinfo.io/json', initial_list='http_proxies.txt', valid_list='valid_http_proxies', min_latency=99999, include_latency=True, include_country=True, threads=100):
        self.que = queue.Queue()
        self.df = pd.DataFrame()
        self.website = website
        self.assets_dir = rf'{os.getcwd()}\assets'
        self.proxies_dir = rf'{os.getcwd()}\proxies'
        self.inititial_list = rf'{self.proxies_dir}\{initial_list}'
        self.valid_list = rf'{self.proxies_dir}\{valid_list}'
        self.min_latency = min_latency
        self.include_latency = include_latency
        self.include_country = include_country
        self.threads = threads
        self.reader = geoip2.database.Reader(rf'{self.assets_dir}\GeoLite2-Country.mmdb')
        self.proxy_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$'
        self.result = []
        self.counter = 1
        self.checked = 1
        
    def extract(self):
        
        with open(self.inititial_list, 'r') as fp:
            proxies = fp.read().split('\n')
            
        print(f'Total Proxies: {len(proxies)}')
        
        for proxy in proxies:
            self.que.put(proxy)
            
    def check_proxy(self):
        
        while not self.que.empty():
            proxy = self.que.get()
            
            try:
                start_time = time.time()
                res = requests.get(self.website, proxies={'http': proxy, 'https': proxy}, timeout=20)
                end_time = time.time()
            except:
                self.checked += 1
                continue
            
            if res.status_code == 200:
                try: country = self.reader.country(proxy.split(':')[0]).country.name
                except: print(f'Country unable to be deciphered for {proxy}')
                print(f'[{self.counter}/{self.checked}] {proxy}\t{end_time - start_time:.3f}\t{country}')
                self.result.append({'Proxy': proxy, 'Latency': round(end_time - start_time, 3), 'Country': country})
                self.counter += 1
                
            self.checked += 1

            
    def output(self, result):
        
        print(len(result))
        self.df = pd.DataFrame(result)
        self.df.set_index('Proxy', inplace=True)
        self.df['Latency'].fillna(1000, inplace=True)
        self.df['Country'].fillna('Unknown', inplace=True)
        self.df.sort_values(by='Latency', inplace=True)
        
        print(f'Total Proxies: {len(self.df)}')
        print(f'Average Latency: {self.df["Latency"].mean()}')
        
        if not self.include_latency: self.df.drop('Latency', axis=1, inplace=True)
        if not self.include_country: self.df.drop('Country', axis=1, inplace=True)
        
        self.df.to_csv(f'{self.valid_list}.csv', index=True)
        
    def run(self):

        self.extract()

        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.check_proxy)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
            
        self.output(self.result)



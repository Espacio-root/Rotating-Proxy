import pandas as pd
import os
import requests

class Rotation:

    def __init__(self, proxy_file='valid_http_proxies.csv', state_file='state.txt'):
        self.assets = rf'{os.getcwd()}\assets'
        self.proxies = rf'{os.getcwd()}\proxies'
        self.proxy_list = pd.read_csv(rf'{self.proxies}\{proxy_file}')['Proxy'].values.tolist()[:3]
        self.current_proxy = None
        self.current_index = 0
        self.max_retries = 5
        self.state_file = rf'{self.assets}\{state_file}'
        self.len = len(self.proxy_list)

        if state_file:
            try:
                with open(self.state_file, 'r') as f:
                    self.current_index = int(f.read().strip())
            except FileNotFoundError:
                pass
            
    def update_state_file(self, content):
        if self.state_file:
            try:
                with open(self.state_file, 'w') as f:
                    f.write(str(content))
            except FileNotFoundError:
                pass


    def get_proxy(self):
        
        try: self.current_proxy = self.proxy_list[self.current_index]
        except IndexError: 
            self.current_proxy = self.proxy_list[0] 
            self.update_state_file(str(0))
        self.current_index += 1
        self.current_index %= self.len

        self.update_state_file(self.current_index)

        return self.current_proxy
            
    
    def make_request(self, url):
        retries = 0
        while retries < self.max_retries:
            try:
                proxy = self.get_proxy()
                response = requests.get(url, proxies={'http': proxy, 'https': proxy}, timeout=10)
                return response
            except:
                retries += 1
                continue
        return None
    


    
    
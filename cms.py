import os
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from queue import Queue
from colorama import Fore, Style
from platform import system
import random

# Menonaktifkan peringatan SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Daftar User-Agent untuk digunakan secara acak
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; SM-A505G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
    # Anda dapat menambahkan lebih banyak User-Agent di sini
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

class CMSDetector:
    def __init__(self, num_threads):
        self.num_threads = num_threads
        self.headers = {
            'User-Agent': get_random_user_agent(),  # Menggunakan User-Agent acak
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.url_queue = Queue()
        self.results_folder = 'results'
        self.common_cms = ['wordpress', 'joomla', 'drupal', 'wix', 'shopify', 'magento', 'vbulletin', 'prestashop',
                           'cmsmadesimple', 'drupalcommerce', 'opencart', 'phpbb']

    def create_folder(self):
        if not os.path.exists(self.results_folder):
            os.makedirs(self.results_folder)

    def queue_urls(self, file_path):
        with open(file_path, 'r') as file:
            site_list = [line.strip() for line in file]
            for url in site_list:
                self.url_queue.put(url)

    def get_cms(self, url):
        try:
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url
            fatch = requests.get(url, headers=self.headers, verify=True, timeout=10)
        except requests.RequestException:
            print(f"[!] {Fore.CYAN} {url} {Style.RESET_ALL} => {Fore.RED} Invalid {Style.RESET_ALL}")
        else:
            if 'text/html' not in fatch.headers.get('content-type', ''):
                return
            html_content = fatch.text
            cms_headers = fatch.headers.get('X-Powered-By', '').lower()
            soup = BeautifulSoup(html_content, 'html.parser')
            meta_generator = soup.find('meta', {'name': 'generator'})
            cms_meta = meta_generator.get('content').lower() if meta_generator else ''

            detected_cms = [cms for cms in self.common_cms if cms in cms_headers or cms in cms_meta]
            if detected_cms:
                self.save_result(url, detected_cms[0])
                print(f"[+] {Fore.CYAN} {url} {Style.RESET_ALL} => {Fore.GREEN} {', '.join(detected_cms)} {Style.RESET_ALL}")
            else:
                print(f"[-] {Fore.CYAN} {url} {Style.RESET_ALL} => {Fore.RED} Not detected! {Style.RESET_ALL}")

    def save_result(self, url, cms):
        with open(f"results/{cms}_results.txt", 'a') as file:
            file.write(url + '\n')

    def process_sites(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            executor.map(self.get_cms, iter(self.url_queue.get, None))

    def main(self, file_path):
        self.create_folder()
        self.queue_urls(file_path)
        self.process_sites()

def banner():
    print(r"""
    
   ___ __  __ ___     _     _       _   _           
  / __|  \/  / __| __| |___| |_ ___| |_| |_ ___ _ _ 
 | (__| |\/| \__ \/ _` / -_)  _/ -_) / /  _/ _ \ '_|
  \___|_|  |_|___/\__,_\___|\__\___|_\_\\__\___/_|  
                                                    
                                                    
CMS Detector v2.0 - Now With Proxies and Enhanced Detection
Telegram: https://t.me/@RootLeakd
""")

def clear():
    if system() == 'Linux':
        os.system('clear')
    elif system() == 'Windows':
        os.system('cls')

if __name__ == "__main__":
    clear()  # Membersihkan layar terlebih dahulu
    banner()  # Menampilkan banner setelah layar dibersihkan
    file_path = input("Enter Your Site List: ")
    num_threads = int(input("Enter the number of threads: "))
    cms_detector = CMSDetector(num_threads)
    cms_detector.main(file_path)

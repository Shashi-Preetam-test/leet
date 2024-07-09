import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from subprocess import Popen
from pymongo import MongoClient

concurrent_windows = 10

chrome_options = Options()
options = [
    # "--headless",
    "--disable-gpu",
    "--window-size=0,0",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--remote-debugging-pipe"
]
for option in options:
    chrome_options.add_argument(option)

client = MongoClient("mongodb+srv://shashi:shashi123@leetcode-rankify.kno7lqv.mongodb.net/?retryWrites=true&w=majority&appName=LeetCode-Rankify")
db = client["LeetCode-Rankify"]

def getResults(contest_name):
    url = "https://leetcode.com/contest/" + contest_name + "/ranking"
    
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    driver.quit()
    
    pages = int(soup.find_all(class_ = "page-btn")[-1].get_text())
    
    idx = 1
    for i in range(1, 11):
        Popen(('python scraper-worker.py {} {} {}'.format(contest_name, idx, min(idx + pages // 10 + 1, pages))), shell=True)
        idx = idx + pages // 10 + 2
    

if len(sys.argv) != 2:
    url = "https://leetcode.com/contest/"
    
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    driver.quit()
    
    contest_name = soup.find(class_='group flex w-full items-center')['data-contest-title-slug']
    
else: 
    contest_name = sys.argv[1]

print(contest_name)
getResults(contest_name=contest_name)
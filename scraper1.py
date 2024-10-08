import os, sys
from selenium import webdriver
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
from pymongo import MongoClient

display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()

chrome_options = webdriver.ChromeOptions()    

options = [
  # Define window size here
   "--window-size=800,800",
    "--ignore-certificate-errors"
    "--headless",
    
    #"--disable-gpu",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)
    
mongodb_username = os.getenv('MONGODB_USERNAME')
mongodb_password = os.getenv('MONGODB_PASSWORD')
cluster_url = os.getenv('MONGODB_CLUSTER_URL')

client = MongoClient(f"mongodb+srv://{mongodb_username}:{mongodb_password}@{cluster_url}/?retryWrites=true&w=majority&appName=LeetCode-Rankify")
db = client["LeetCode-Rankify"]

def getResults(contest_name, pages):
    url = "https://leetcode.com/contest/{}/ranking/".format(contest_name)
    page = 1

    results = []

    while(page <= pages):
        driver = webdriver.Chrome(options=chrome_options)
            
        try:
            driver.get(url + str(page))
        except Exception as e:
            print("Couldn't fetch page {}.".format(page), e, "\nRetrying.")
            driver.quit()
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        if(len(soup.find_all('tr')) <= 1):
            print("Couldn't fetch page {}. Retying.".format(page))
            continue
      
        for row in soup.find_all('tr'):
            if row.find(class_="ranking-username") is None:
                continue

            user = dict()

            ptr = row.find('td')
            user["rank"] = int(ptr.get_text().strip())

            ptr = ptr.find_next('td')
            user["name"] = ptr.find('a')["title"]

            ptr = ptr.find_next('td')
            user["score"] = int(ptr.get_text().strip())

            ptr = ptr.find_next('td')
            user["finish_time"] = ptr.get_text().strip()
          
            results.append(user)
        
        driver.quit()

        print("Results fetched from page {}.".format(page))
        page += 1
    
    db[contest_name].insert_many(results)
    
    file = open(f'./contest_results/{contest_name}', 'w')
    file.write(results)
    
    print("Results fetched from pages {} to {}.".format(1, pages))


def startScrape(contest_name):
    url = "https://leetcode.com/contest/" + contest_name + "/ranking"

    while(True):
      driver = webdriver.Chrome(options=chrome_options)
      
      try:
          driver.get(url)
      except Exception as e:
          print("Couldn't fetch number of pages.", e, "\nRetrying.")
          driver.quit()
          continue
      
      soup = BeautifulSoup(driver.page_source, 'html.parser')
      
      driver.quit()
  
      if(len(soup.find_all(class_ = "page-btn")) == 0):
          print("Couldn't fetch number of pages. Retrying.")
          continue
        
      pages = int(soup.find_all(class_ = "page-btn")[-1].get_text())
  
      print("{} pages found.".format(pages))
      getResults(contest_name, pages)
      break

if len(sys.argv) != 2 or sys.argv[1] == "":
    url = "https://leetcode.com/contest/"
    
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    driver.quit()
    
    contest_name = soup.find(class_='group flex w-full items-center')['data-contest-title-slug']
    
else: 
    contest_name = sys.argv[1]

print(contest_name)
startScrape(contest_name=contest_name)

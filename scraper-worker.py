import sys, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pymongo import MongoClient

contest_name = sys.argv[1]
start_page = int(sys.argv[2])
end_page = int(sys.argv[3])

chrome_options = Options()
options = [
    # "--headless",
    # "--disable-gpu",
    # "--window-size=0,0",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    # "--disable-dev-shm-usage",
    # "--remote-debugging-pipe"
]
for option in options:
    chrome_options.add_argument(option)

url = "https://leetcode.com/contest/{}/ranking/".format(contest_name)
page = start_page

results = []

client = MongoClient("mongodb+srv://shashi:shashi123@leetcode-rankify.kno7lqv.mongodb.net/?retryWrites=true&w=majority&appName=LeetCode-Rankify")
db = client["LeetCode-Rankify"]

while(page <= end_page):
    driver = webdriver.Chrome(options=chrome_options)
        
    driver.get(url + str(page))

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    if soup.find('tr') is None:
        continue
        
    for row in soup.find_all('tr'):
        if row.find(class_="ranking-username") is None:
            continue

        user = dict()

        ptr = row.find('td')
        user["rank"] = ptr.get_text().strip()

        ptr = ptr.find_next('td')
        user["name"] = ptr.find('a')["title"]

        ptr = ptr.find_next('td')
        user["score"] = ptr.get_text().strip()

        ptr = ptr.find_next('td')
        user["finish_time"] = ptr.get_text().strip()

        file = open('{}.json'.format(contest_name), 'a')

        file.write(str(user))
        file.write('\n')
        
        file.close()
        results.append(user)
    
    driver.quit()

    time.sleep(1)

    print("Results fetched from page {}.".format(page))
    page += 1

print("Results fetched from pages {} to {}.".format(start_page, end_page))
db[contest_name].insert_many(results)

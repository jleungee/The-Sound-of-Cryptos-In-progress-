# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 09:35:37 2022

@author: jeffr
"""

# Codes for scraping crypto data from coingecko.com
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import regex as re
import numpy as np
from random import randint
from time import sleep


url,symbol = [],[]
for i in range(18): # Top 1735 cryptos have market cap > $1M
    if i == 0:
        # Cryptocurrency by Market Cap
        r = requests.get("https://www.coingecko.com/").text 
    else:
        r = requests.get(f"https://www.coingecko.com/?page={i}").text
    soup = BeautifulSoup(r,"html.parser")
    
    # From the above website, we get create the url for each cryptos historical
    # data in coingecko.com
    for j in soup.find_all("a",{"class":"d-lg-none font-bold tw-w-12"}):
        url.append(f"https://www.coingecko.com{j['href']}/historical_data/usd?start_date=2017-01-01&end_date=2022-01-27#panel")
        symbol.append(j.string.strip()) # as well as their tickers
    print("Got",i,"page(s)")
    
symbol = [i+"-USD" for i in crypto["Symbol"]] # add - USD after each ticker
faillist = []

# Scraping historical data
for i in range(len(url)): 
    # Sleep the program regularly to avoid being banned
    if i%10 == 0:
        sleep(randint(10,20))
    if i%25==0:
        sleep(randint(15,20))
    if i%50 == 0:
        sleep(randint(30,40))
    sleep(randint(5,10))
    print("Try",symbol[i],str(i+1)+"/"+str(len(url)))
    
    # Get historical data
    try:
        r = requests.get(url[i]).text
        soup = BeautifulSoup(r,"html.parser")
        rows = soup.find_all("tr")
        data = []
        for row in rows[1:]:
          date = row.find_all('th')
          date = [datetime.datetime.strptime(date[0].string,"%Y-%m-%d")]
          cols = row.find_all('td',{'class':'text-center'})
          cols = [float(re.sub(",","",i.string.strip()[1:])) if i.string != "\nN/A\n" else np.nan for i in cols]
          data.append(date+cols)
        df = pd.DataFrame(data,columns = [h.string.strip() for h in rows[0] if h != "\n"])
        
        
        # saving the data
        address = f"C:\\Users\\jeffr\\Desktop\\FINA 4392\\crypto\\{symbol[i]}.csv"
        df.to_csv(address)
        print("Succeed getting",symbol[i])
    
    # exception cases
    except:
        print("*****Fail to get "+symbol[i]+"*****")
        faillist.append(cryptolist[i])
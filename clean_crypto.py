# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 14:31:50 2022

@author: jeffr
"""

# Clean all crypto data and form them into a large dataframe
from os import listdir
from os.path import isfile, join
import pandas as pd
import datetime
import regex as re

def get_fixedday(start = datetime.datetime(2017,1,1),
                  end = datetime.datetime(2022,1,25)):
  date = [start + datetime.timedelta(i) for i in range((end-start).days)]
  year = [i.year for i in date]
  month = [i.month for i in date]
  week=[]
  c_week = [i.strftime("%V") for i in date]+["done"]
  count = 1
  for i in range(len(year)):
    week.append(count)
    if c_week[i+1] != c_week[i]:
      count += 1
  return pd.DataFrame({"Date":date,"year":year,"month":month,"week":week})


mypath = "C:\\Users\\jeffr\\Desktop\\FINA 4392\\crypto"

files = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]


for i in range(len(files)):
    symbol = files[i].split("\\")[-1][:-4]
    df = pd.read_csv(files[i]).iloc[:,1:]
    df.columns = ["Date"]+[symbol+"_"+re.sub("Market Cap","Mcap",i) for i in df.columns[1:]]
    df["Date"] = pd.to_datetime(df["Date"])
    if  i == 0:
        crypto = pd.merge(get_fixedday(),df,on="Date",how="left")
    else:
        crypto = pd.merge(crypto,df,on="Date",how="left")
    print("Merged "+str(i+1)+" dataframe")

# save all crypto data into csv
crypto.to_csv("C:\\Users\\jeffr\\Desktop\\FINA 4392\\cryptos\\crypto_hist.csv")
#df = pd.read_csv("C:\\Users\\jeffr\\Desktop\\FINA 4392\\cryptos\\crypto_hist.csv")
#smalldf = df[df[df["Date"]>="2018-01-01"].dropna(axis=1).columns]
#smalldf.to_csv("C:\\Users\\jeffr\\Desktop\\FINA 4392\\cryptos\\crypto_hist18.csv")
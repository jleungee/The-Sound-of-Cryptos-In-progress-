# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 03:08:05 2022

@author: Jeffrey
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 03:57:54 2022

@author: jeffr
"""

# import packages
import spotipy 
import time
import regex as re
from time import sleep
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import pandas as pd
import regex as re 
import datetime
from math import ceil
import requests
from os import listdir
from os.path import isfile, join


# setting up my Spotify developer credentials
def sp_setup(count=0):
    if count == 1:
        client_id = '626b2045073e42c1a89318d103e657a7'
        client_secret = 'e79214180b9b45c0ba2f11c7f9c09e18'
    elif count == 0:
        client_id = '868fd01f235b4e5ca119cc9cf93ef83c'
        client_secret = '225a84008acc4f92aeac510e01819b01'
    elif count == 2:
        client_id = 'de036863d78642539641fc14802416f1'
        client_secret = 'f869f6c89ee94f4781ae196661664318'
       
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    return sp

sp = sp_setup()
# Function for checking if there is any connection error
def check_connection():
    urlol = "https://www.spotify.com/us/"
    timeout = 5
    try:
        request = requests.get(urlol, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        return False


# Function for getting songs' info
def get_info(keywords, songs = 1, market = "us"):
    try:
        info_list = sp.search(q = keywords, type = 'track',limit=songs,market = market)
    except:
        while check_connection() == False:
            print("Internet Error! Rest 10s")
            sleep(10)
    try:
        names = info_list['tracks']['items'][0]['artists']
        artist = [names[h]['name'] for h in range(len(names))]
        album = info_list['tracks']['items'][0]['album']['name']
        song = info_list['tracks']['items'][0]['name']
        song_id = info_list['tracks']['items'][0]['id']
        date = info_list['tracks']['items'][0]['album']['release_date']
        # In millisecond
        duration = info_list['tracks']['items'][0]['duration_ms']
        # Spotify Popularity Index is a 0-to-100 score that ranks how popular 
        # an artist is relative to other artists on Spotify
        popularity = info_list['tracks']['items'][0]['popularity']
        summary = pd.DataFrame({"Artist":[artist],
                  "Album":[album],
                  "Song":[song],
                  "Song ID":[song_id],
                  "Date":[date],
                  "Duration":[duration],
                  "Popularity":[popularity]})
    except:        
        summary = pd.DataFrame({"Artist":[np.NaN],
              "Album":[np.NaN],
              "Song":[np.NaN],
              "Song ID":[np.NaN],
              "Date":[np.NaN],
              "Duration":[np.NaN],
              "Popularity":[np.NaN]})
    return summary


# Function for converting unicodes in a string to string
def unicode_converter(string):
    if type(string) != float:
        uni = re.findall("<U\+.*?>",string)
        uniclean = ["\\u"+i[3:-1]for i in uni]
        unilen = len(uni)
        start = 0
        for i in range(len(uni)):
            unichar = uniclean[i].replace("\\/", "/").encode().decode('unicode_escape')
            summ = start  
            search = re.search("<U\+.*?>",string[start:])
            if search != None:
                start,end = re.search("<U\+.*?>",string[start:]).span()
                start,end = start + summ, end+summ
                string = string[:start]+unichar+string[end:]

    return string



#############################################################################
# Codes for getting Chart Data

# For iterating within the files which contains chart data
mypath = "C:\\Users\\Jeffrey\\Desktop\\spotify\\transfered"
files = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
n_file = len(files)


fuck_time = time.time() # Calculate time

# For each chart data file,
for i in range(n_file):
    sp = sp_setup(count = i%3)
    print(files[i]) # print file name
    
    # Get individual chart data file
    song_chart = pd.read_csv(files[i], encoding = "ISO-8859-1").iloc[:,1:]
    iso = files[i][50:52]
    n = len(song_chart.index)
    song_chart["index"] = range(0,n)
    song_chart = song_chart.set_index("index")
    print("Got "+iso+" chart")
    
    # Create final spotify info save address
    sp_name = "C:\\Users\\Jeffrey\\Desktop\\spotify\\spotify_info\\"+"spotify_info_"+iso+".csv"
    
    
 
    # Search songs by song names and artist names and convert
    # potential unicodes
    song_chart["Song"] = song_chart["Song"].apply(unicode_converter)
    song_chart["Artist"] = song_chart["Artist"].apply(unicode_converter) 
    key_list = list(song_chart["Song"]+" "+song_chart["Artist"])
    keywords = list(set(key_list))
    n_all = len(keywords)
    print("Number of songs ",str(n_all),"Total rows: ",len(key_list))
    
    
    # Memoize spotify search result (to reduce api call)
    key_set = {keywords[0]:get_info(keywords = keywords[0],market=iso)}
    info = get_info(keywords[0]) # initialize info
    print("Started geting info")
    
    start_time = time.time() # Calculate search time
    
    # Actually searching, create a dictionary of songs and spotify information
    for i in range(1,n_all):       
        if keywords[i] not in key_set.keys():           
            try:
                info_temp = get_info(keywords = keywords[i],market=iso)
            
            except Exception as e: # Exception cases 
                print(e)
                while check_connection() == False:
                    print("Internet Error! Rest 10s")
                    sleep(10)
                sleep(10)
                info_temp = get_info(keywords = keywords[i],market=iso)          
            key_set[keywords[i]] = info_temp  
        print("Collected "+str(i+1)+" pieces of "+iso+" info out of "+str(n_all)+" pieces")
                   
   
    # Mapping songs and song info with the actual chart each day
    def merge_info(x):
        return key_set[x]
    info = pd.concat(list(map(merge_info,key_list)))
    print(info)    
    print('Took',time.time()-start_time,'seconds to run')
    
    
    # reindex the chart
    info["Index"]=range(len(key_list))
    info = info.set_index("Index")
    # save itermediate results and retrieve when needed
    info.to_csv("C:\\Users\\Jeffrey\\Desktop\\spotify\info\\"+iso+"_info.csv")
    #info = pd.read_csv("C:\\Users\\Jeffrey\\Desktop\\spotify\\info\\ar_info.csv")
    
    
    #  Get song audio features
    id = info["Song ID"]
    n_all = len(id)
    id0 = info[info["Song ID"].apply(type) != float]["Song ID"]
    id0_index = id0.index
    id0=list(id0)
    
    
    # Retrieve song valences by song id
    n = len(id0) 
    ndiv = 100 # 100 audio features at once if possible 
    for i in range(0,ceil(n/ndiv)):
        
        # Initializing audio features dataframe
        if i == 0 :
            af = pd.DataFrame(sp.audio_features(id0[:ndiv]))
        
        # Start searching
        else:
            try:
              af = pd.concat([af,
                              pd.DataFrame(sp.audio_features(id0[i*ndiv:min((i+1)*ndiv,n)]))])
            # Exception cases
            except:
                # Internet error
                while check_connection() == False:
                    print("Internet Error! Rest 10s")
                    sleep(10)
                
                # Error when a song id list return no result
                if check_connection() == True:
                    for j in range(i*100,i*100+100,50):
                        try:
                            print("Try exception af loop: " +str(50)+" of "+str(int(n/ndiv)+1)+" pieces" )
                            temp50 = sp.audio_features(id0[j:j+50])      
                            af = pd.concat([af, pd.DataFrame(temp50)])  
                        except:
                                for s in range(2):
                                    try:
                                        print("Exception af loop: " +str(25)+" of "+str(int(n/ndiv)+1)+" pieces" )
                                        temp25 = sp.audio_features(id0[j+s*25:j+(s+1)*25])
                                        af = pd.concat([af, pd.DataFrame(temp25)])
                                    
                                    except:
                                        for ss in range(25):
                                            print("Exception af loop: " +str(1)+" of "+str(int(n/ndiv)+1)+" pieces" )
                                            temp1 = sp.audio_features(id0[j+ss])
                                            try:
                                                af = pd.concat([af, pd.DataFrame(temp1)])
                                            except:
                                                af = pd.concat([af, pd.DataFrame(sp.audio_features(""))])
                      
        
                                    
        print("Collected "+str(i+1)+" pieces of "+iso+" af info out of "+str(int(n/ndiv)+1)+" pieces")


    # # Reindexing the audio feature dataframe

    af["Index"] = id0_index
    af = af.set_index("Index")
    af = af.reindex(range(0, n_all))
    
    
    # Daily Top 200 song data in US with valence
    spotify_info = pd.concat([song_chart,info,af],axis=1)
    spotify_info = spotify_info[["Song","Stream","start","Artist","Album",
                                  "Date","Duration","Popularity","danceability",
                                  "energy","key","loudness","mode","speechiness",
                                  "acousticness","instrumentalness","liveness",
                                  "valence","tempo","duration_ms","time_signature"]]
    
    # Saving the final spotify dataframe
    spotify_info.to_csv(sp_name)
    print("Saved spotify_info at "+sp_name)
    
    
    print('Took',time.time()-fuck_time,'seconds to run')
    sleep(300)
    
    
    
        
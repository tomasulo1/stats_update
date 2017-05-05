# -*- coding: utf-8 -*-
"""
Created on Thu May 28 18:06:46 2015

@author: kerpowski
"""

import csv
import requests

import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import date

    
def read_bstats(s, row):
    elements = row.find_all('td')
    
    s['ab'] = int(elements[3].text)
    s['h'] = int(elements[5].text)
    if s['ab'] == 0:
        s['ave'] = 0
    else:
        s['ave'] = round(s['h'] / s['ab'], 3)
    s['r'] = int(elements[10].text)
    s['ip'] = int(elements[11].text)
    s['hr'] = int(elements[9].text)
    s['sb'] = int(elements[19].text)
    return


def add_bstats(s1, s2):
    s3 = defaultdict(int)
    s3['ab'] = s1['ab'] + s2['ab']
    s3['h'] = s1['h'] + s2['h']
    if s3['ab'] == 0:
        s3['ave'] = 0
    else:
        s3['ave'] = round(s3['h'] / s3['ab'], 3)
    s3['r'] = s1['r'] + s2['r']
    s3['rbi'] = s1['rbi'] + s2['rbi']
    s3['hr'] = s1['hr'] + s2['hr']
    s3['sb'] = s1['sb'] + s2['sb']
    return s3

    
def read_pstats(s, row):
    elements = row.find_all('td')
    s['ip'] = float(elements[12].text)
    s['w']= int(elements[2].text)
    s['sv'] = int(elements[9].text)
    s['k'] = int(elements[23].text)
    s['era'] = float(elements[4].text)
    if s['ip'] == 0:
        s['whip'] = 0
    else:
        s['whip'] = (int(elements[14].text)+int(elements[18].text))/s['ip']
    return

def add_pstats(s1, s2):
    s3 = defaultdict(int)
    s3['ip'] = s1['ip'] + s2['ip']
    s3['w']= s1['w'] + s2['w']    
    s3['k'] = s1['k'] + s2['k']
    s3['sv'] = s1['sv'] + s2['sv']
    if s3['ip'] == 0:
        s3['era'] = 0
        s3['whip'] = 0
    else:
        s3['era'] = round((s1['ip']*s1['era'] + s2['ip']*s2['era'])/(s3['ip']), 3)
        s3['whip'] = round((s1['ip']*s1['whip'] + s2['ip']*s2['whip'])/(s3['ip']), 3)
    return s3


def calc_bvalue(stats):
    val = defaultdict(int)
    val['wAve'] = round((stats['ave'] - 0.267) * (stats['ab'] / 3), 3)
    val['wHr'] = round(2.6 * ((stats['hr'] * 13 / 200) ** 2), 3)
    val['wR'] = round(3 * ((stats['r'] * 13 / 865) ** 3), 3)
    val['wRbi'] = round(3 * ((stats['rbi'] * 13 / 805) ** 3), 3)
    val['wSb'] = round(2.5 * ((stats['sb'] * 13 / 115) ** 2), 3)
    val['total'] = round(val['wAve'] + val['wHr'] + val['wR'] + val['wRbi'] + val['wSb'], 3)
    return val


def calc_pvalue(stats):
    val = defaultdict(int)
    val['wW'] = round(2*((stats['w']10/95)**2), 3)
    if stats['sv'] < 10:
        val['wSV'] = 0
    elif stats['sv'] < 20:
        val['wSV'] = 10
    else:
        val['wSV'] = 20
    val['wK'] = round(2.6*((stats['k']*10/1230)**2), 3)
    val['wEra'] = round((3.65-stats['era'])*stats['ip']/20, 3)
    val['wWhip'] = round((1.21-stats['whip'])*stats['ip']/4, 3)
    val['total'] = round(val['wW'] + val['wSV'] + val['wK'] + val['wEra'] + val['wWhip'], 3)
    return val
    

def get_stats(url, team, tipe):
    #gets the ongoing stats for the current year
    #gets the projected rest of year stats.  uses the 'Depth Charts (R)' estimates
    try:
        r = requests.get(url)
    except:
        return [None, None]
    soup = BeautifulSoup(r.content)

    #get the standard chart
    stat_chart = soup.find(id="SeasonStats1_dgSeason1_ctl00")
    #print(stat_chart)
    #now need to grab 2 entries: current season and Depth Charts remaining projections
    i = 0
    if tipe == 1:
        cur = defaultdict(int)
        est = defaultdict(int)
    else:
        cur = defaultdict(int)
        est = defaultdict(int)
    rows = stat_chart.find_all('tr')
    for row in reversed(rows):
        try:
            year = row.find('td').get_text()
        except:
            continue
        try:
            entry = row.td.next_sibling.get_text()
        except:
            continue
        
        if year == '2017':
            #print(entry)
            if entry == team:
                i += 1
                if tipe == 1:
                    cur = read_bstats(row)
                else:
                    cur = read_pstats(row)
            if entry == "Depth Charts (R)":
                i += 1
                if tipe == 1:
                    est = read_bstats(row)
                else:
                    est = read_pstats(row)
        if i == 2:
            break
        
    return [cur, est]
        

#open for reading
batters = pd.read_csv('batters.csv')
pitchers = pd.read_csv('pitchers.csv')

calculated_batter = []
for i, player in batters.iterrows():
    [cur, est] = get_stats(player['Team'], player['Name'], 1)       
    total = add_bstats(cur, est)
    val = calc_bvalue(total)
    
    calculated_batter.append({**cur, **est, **total, **val})

calculated_batter_df = pd.DataFrame(calculated_batter)
final_batters = pd.concat([batters, calculated_batter_df], axis=1)


calculated_pitcher = []
for player in pitchers:
    [cur, est] = get_stats(player[2], player[1], 2)
    if(cur == None):
        print('Error reading pitcher page for '+player[0])
        break
    total = add_pstats(cur, est)
    val = calc_pvalue(total)
    
    calculated_pitcher.append({**cur, **est, **total, **val})
 
calculated_pitcher_df = pd.DataFrame(calculated_pitcher)
final_pitchers = pd.concat([pitchers, calculated_pitcher_df], axis=1)

final_batters.write_csv('batter_output.csv')
final_pitchers.write_csv('pitcher_output.csv')


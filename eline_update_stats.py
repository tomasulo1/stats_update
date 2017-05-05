# -*- coding: utf-8 -*-
"""
Created on Thu May 28 18:06:46 2015

@author: kerpowski
"""

import requests
import csv
from bs4 import BeautifulSoup
import numpy as np
from datetime import date

class bstats:
    def __init__(self):
        self.ab = 0
        self.h = 0
        self.ave = 0
        self.hr = 0
        self.r = 0
        self.rbi = 0
        self.sb = 0
    def __repr__(self):
        return str(self.ab)+","+str(self.h)+","+str(self.ave)+","+str(self.hr)+","+str(self.r)+","+str(self.rbi)+","+str(self.sb)+","
    pass
    
def read_bstats(s, row):
    elements = row.find_all('td')
    
    s.ab = int(elements[3].text)
    s.h = int(elements[5].text)
    if s.ab == 0:
        s.ave = 0
    else:
        s.ave = round(s.h / s.ab, 3)
    s.r = int(elements[10].text)
    s.rbi = int(elements[11].text)
    s.hr = int(elements[9].text)
    s.sb = int(elements[19].text)
    return

def add_bstats(s1, s2):
    s3 = bstats()
    s3.ab = s1.ab + s2.ab
    s3.h = s1.h + s2.h
    if s3.ab == 0:
        s3.ave = 0
    else:
        s3.ave = round(s3.h / s3.ab, 3)
    s3.r = s1.r + s2.r
    s3.rbi = s1.rbi + s2.rbi
    s3.hr = s1.hr + s2.hr
    s3.sb = s1.sb + s2.sb
    return s3

class pstats:
    def __init__(self):
        self.ip = 0
        self.w = 0
        self.sv = 0
        self.k = 0
        self.era = 0
        self.whip = 0
    def __repr__(self):
        return str(self.ip)+","+str(self.w)+","+str(self.sv)+","+str(self.k)+","+str(self.era)+","+str(self.whip)+","
    pass
    
def read_pstats(s, row):
    elements = row.find_all('td')
    s.ip = float(elements[12].text)
    s.w = int(elements[2].text)
    s.sv = int(elements[9].text)
    s.k = int(elements[23].text)
    s.era = float(elements[4].text)
    if s.ip == 0:
        s.whip = 0
    else:
        s.whip = (int(elements[14].text)+int(elements[18].text))/s.ip
    return

def add_pstats(s1, s2):
    s3 = pstats()
    s3.ip = s1.ip + s2.ip
    s3.w = s1.w + s2.w
    s3.k = s1.k + s2.k
    s3.sv = s1.sv + s2.sv
    if s3.ip == 0:
        s3.era = 0
        s3.whip = 0
    else:
        s3.era = round((s1.ip*s1.era + s2.ip*s2.era)/(s3.ip), 3)
        s3.whip = round((s1.ip*s1.whip + s2.ip*s2.whip)/(s3.ip), 3)
    return s3

class bvalue:
    def __repr__(self):
        return str(self.total)+","+str(self.wAve)+","+str(self.wHr)+","+str(self.wR)+","+str(self.wRbi)+","+str(self.wSb)+","
    pass

def calc_bvalue(stats):
    val = bvalue()
    val.wAve = round((stats.ave-.267)*(stats.ab/3), 3)
    val.wHr = round(2.6*((stats.hr*13/200)**2), 3)
    val.wR = round(3*((stats.r*13/865)**3), 3)
    val.wRbi = round(3*((stats.rbi*13/805)**3), 3)
    val.wSb = round(2.5*((stats.sb*13/115)**2), 3)
    val.total = round(val.wAve + val.wHr + val.wR + val.wRbi + val.wSb, 3)
    return val

class pvalue:
    def __repr__(self):
        return str(self.total)+","+str(self.wW)+","+str(self.wSV)+","+str(self.wK)+","+str(self.wEra)+","+str(self.wWhip)+","
    pass

def calc_pvalue(stats):
    val = pvalue()
    val.wW = round(2*((stats.w*10/95)**2), 3)
    if stats.sv < 10:
        val.wSV = 0
    elif stats.sv < 20:
        val.wSV = 10
    else:
        val.wSV = 20
    val.wK = round(2.6*((stats.k*10/1230)**2), 3)
    val.wEra = round((3.65-stats.era)*stats.ip/20, 3)
    val.wWhip = round((1.21-stats.whip)*stats.ip/4, 3)
    val.total = round(val.wW + val.wSV + val.wK + val.wEra + val.wWhip, 3)
    return val
    
#def calc_value():
#    return
#
#def team_result():
#   return
#
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
        cur = bstats()
        est = bstats()
    else:
        cur = pstats()
        est = pstats()
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
                    read_bstats(cur, row)
                else:
                    read_pstats(cur, row)
            if entry == "Depth Charts (R)":
                i += 1
                if tipe == 1:
                    read_bstats(est, row)
                else:
                    read_pstats(est, row)
        if i == 2:
            break
        
    return [cur, est]
        
#open for reading
file1 = open('batters.csv', 'r')
file2 = open('pitchers.csv', 'r')

reader1 = csv.DictReader(file1)
reader2 = csv.DictReader(file2)
fieldnames1 = reader1.fieldnames
fieldnames2 = reader2.fieldnames
table1 = list()
table2 = list()
for row in reader1:
    table1.append([row['Name'], row['Team'], row['url']])
for row in reader2:
    table2.append([row['Name'], row['Team'], row['url']])

file1.close()
file2.close()

#re-open for writing
file1 = open('batters.csv', 'w')
file2 = open('pitchers.csv', 'w')

#write out headers
for item in fieldnames1:
    file1.write(item+',')
file1.write('\n')
for item in fieldnames2:
    file2.write(item+',')
file2.write('\n')

for player in table1:
    [cur, est] = get_stats(player[2], player[1], 1)
    
    total = add_bstats(cur, est)
    val = calc_bvalue(total)
    
    file1.write(player[0])
    file1.write(',')
    file1.write(player[1])
    file1.write(',')
    file1.write(player[2])
    file1.write(',')
    file1.write(cur.__repr__())
    file1.write(est.__repr__())
    file1.write(total.__repr__())
    file1.write(val.__repr__())
    file1.write('\n')

for player in table2:
    [cur, est] = get_stats(player[2], player[1], 2)
    if(cur == None):
        print('Error reading pitcher page for '+player[0])
        break
    total = add_pstats(cur, est)
    val = calc_pvalue(total)
    
    file2.write(player[0])
    file2.write(',')
    file2.write(player[1])
    file2.write(',')
    file2.write(player[2])
    file2.write(',')
    file2.write(cur.__repr__())
    file2.write(est.__repr__())
    file2.write(total.__repr__())
    file2.write(val.__repr__())
    file2.write('\n')
file1.close()
file2.close()

# -*- coding: utf-8 -*-
"""
Created on Fri May 20 11:01:43 2022

@author: pierr
"""

from seq_scout import launch

def res_list(results) :
    res=[]
    for result in results:
        ligne=[]
        for itemset in result[1]:
            for item in set(itemset) :
                ligne.append(item)
        res.append(ligne)
    return res

def data_list(filename,serveur):
    data = []
    numechange=0
    with open(filename) as f:
        for line in f:
            l=[numechange]
            line_split=line.replace('\n','').split(',')
            if line_split[0]==serveur :
                for i in range(2,len(line_split)):
                    l.append(line_split[i])
                data.append(l)
                numechange+=1
    return data

def in_list(l,L):
    for e in l :
        if not(e in L) : return False
    return True

def cluster_list(res,data):
    clusters=[]
    for l in res :
        cluster=[]
        for L in data :
            if in_list(l,L) : cluster.append(L[0])
        clusters.append(cluster)
    return clusters


if __name__ == '__main__':
    res=res_list(launch())
    data = data_list('SeqScoutData.txt',serveur='FLORE')
    clusters = cluster_list(res,data)
    print(clusters)
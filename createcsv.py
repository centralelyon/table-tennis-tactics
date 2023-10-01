# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 16:24:16 2022

@author: pierr
"""

from match import *
import pysubgroup as ps
import unidecode 


#Imoprt des données
M=Match('Flore Boll corrige.csv')

ZONES = ['M1','M2','M3','D1','D2','D3','G1','G2','G3']
SERVICES= ['Latéral droit','Latéral gauche','Droit']
LATERALITES=['Coup droit','Revers']
COUPS = ['Controle','Attaque','Poussette']
JOUEURS=['FLORE','BOLL']

GROUPE_ZONE={'M1':'Centre_Court',
             'M2':'Centre_Court',
             'M3':'Centre_Long',
             'D1':'Cote_Court',
             'D2':'Cote_Court',
             'D3':'Cote_Long',
             'G1':'Cote_Court',
             'G2':'Cote_Court',
             'G3':'Cote_Long'}

ABR_COUPS={'Controle' : 'C',
           'Attaque' : 'A',
           'Poussette' : 'P'}

ABR_LAT={'Coup droit':'F',
         'Revers':'B'}

CONV_SERVICES={'Latéral droit':'Rss','Latéral gauche':'Lss','Droit':'Droit'}

valeurs=[]
nume=-1
for s in M.match :
    for e in s.set :
        numc=0
        nume+=1
        valeur=[]
        if e.serveur in JOUEURS :
            coups=e.echange
            if coups[1].isservice :
                time=coups[1].timepos
                n=1
            else :
                time=coups[0].timepos
                n=0
            valeur.append(str(nume))
            valeur.append(str(numc))
            valeur.append(str(time))
            valeurs.append(valeur)
            i=n+1
            while not(coups[i].isgagnant) :
                numc+=1
                time=coups[i].timepos
                valeur=[]
                valeur.append(str(nume))
                valeur.append(str(numc))
                valeur.append(str(time))
                valeurs.append(valeur)
                i+=1
            numc+=1
            time=coups[i].timepos
            valeur=[]
            valeur.append(str(nume))
            valeur.append(str(numc))
            valeur.append(str(time))
            valeurs.append(valeur)
            valeur=[]
            valeur.append(str(nume))
            valeur.append(str(numc+1))
            valeur.append(str(time+coups[i].duree))
            valeurs.append(valeur)
                    

f = open('videodata'+'.csv', 'w')
for valeur in valeurs:
    ligne = ','.join(valeur)+"\n"
    f.write(ligne)

f.close()
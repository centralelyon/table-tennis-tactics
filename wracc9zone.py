# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 10:52:24 2022

@author: pierr
"""

from match import *
from unidecode import unidecode
import itertools
from copy import *
from time import *

t0=time()

M=Match('Flore Boll corrige.csv')

serveur = ['FLORE','BOLL']
WINNER = 'FLORE'


LAT=['Coup droit','Revers']
SERV = ['Latéral droit','Latéral gauche']
COUP = ['Attaque','Controle','Poussette']
ZONE = ['M1','M2','M3','D1','D2','D3','G1','G2','G3']
JOUEURS=['FLORE','BOLL']
LOSER = JOUEURS[abs(JOUEURS.index(WINNER)-1)]

class Schema :
    
    def __init__(self,liste_coup,liste_zone):
        self.joueur=[]
        self.typeaction=[]
        self.lateralite=[]
        self.typecoup=[]
        self.zone=[]
        for c in liste_coup :
            self.joueur.append(c.joueur)
            if c.isservice : 
                self.typeaction.append(1)
                self.typecoup.append(c.typeservice)
            else : 
                self.typeaction.append(2)
                self.typecoup.append(c.typecoup)
            self.lateralite.append(c.lateralite)
        for z in liste_zone :
            self.zone.append(z)
        
        
    def create_ligne(self):
        ligne=''
        for i in range(len(self.joueur)) :
            ligne+=','+str(self.joueur[i])
            ligne+=','+str(self.lateralite[i])
            ligne+=','+str(self.typecoup[i])
            ligne+=','+str(self.zone[i])
        return ligne
    
    def generalize(self,nbcond,liste) :
        taille = len(liste)
        val = [self.lateralite[0],self.typecoup[0],self.zone[0],self.lateralite[1],self.typecoup[1],self.zone[1],self.lateralite[2],self.typecoup[2],self.zone[2]]
        n=len(val)
        list_indice = [k for k in range (n)]
        ldejavu=[]
        for i in range(nbcond+1):
            lindice = itertools.combinations(list_indice, i)
            for c in lindice :
                if est_valide(c,ldejavu) :
                    newval = deepcopy(val)
                    for e in c :
                        newval[e] = 'all'
                    schem = SchemaGen(self.joueur,newval[0],newval[1],newval[2],newval[3],newval[4],newval[5],newval[6],newval[7],newval[8])
                    cond=True
                    k=0
                    while cond and k<taille :
                        if schem.est_identique(liste[k]) :
                            cond=False
                            ldejavu.append(list(c))
                        k+=1
                    if cond : liste.append(schem)
        return liste
    
class SchemaGen() :
    
    def __init__(self, ljoueur,llat1,lcoup1,lzone1,llat2,lcoup2,lzone2,llat3,lcoup3,lzone3):
        self.joueur = ljoueur
        self.typecoup = [lcoup1,lcoup2,lcoup3]
        self.zone = [lzone1,lzone2,lzone3]
        self.lateralite=[llat1,llat2,llat3]
    
    def contient(self,schema) :
        #renvoie True si schema inclus dans self
        if not(schema.joueur[0]==self.joueur[0]) : return False
        if not(schema.typecoup[0]==self.typecoup[0]) and not(self.typecoup[0]=='all') : return False
        if not(schema.typecoup[1]==self.typecoup[1]) and not(self.typecoup[1]=='all') : return False
        if not(schema.typecoup[2]==self.typecoup[2]) and not(self.typecoup[2]=='all') : return False
        if not(schema.lateralite[0]==self.lateralite[0]) and not(self.lateralite[0]=='all') : return False
        if not(schema.lateralite[1]==self.lateralite[1]) and not(self.lateralite[1]=='all') : return False
        if not(schema.lateralite[2]==self.lateralite[2]) and not(self.lateralite[2]=='all') : return False
        if not(schema.zone[0]==self.zone[0]) and not(self.zone[0]=='all') and not(schema.zone[0]=='all') : return False
        if not(schema.zone[1]==self.zone[1]) and not(self.zone[1]=='all') and not(schema.zone[1]=='all') : return False
        if not(schema.zone[2]==self.zone[2]) and not(self.zone[2]=='all') and not(schema.zone[2]=='all') : return False
        return True
    
    def est_identique(self,schema) :
        if not(schema.joueur[0]==self.joueur[0]) : return False
        if not(schema.joueur[1]==self.joueur[1]) : return False
        if not(schema.typecoup[0]==self.typecoup[0]) : return False
        if not(schema.typecoup[1]==self.typecoup[1]) : return False
        if not(schema.typecoup[2]==self.typecoup[2]) : return False
        if not(schema.lateralite[0]==self.lateralite[0]) : return False
        if not(schema.lateralite[1]==self.lateralite[1]) : return False
        if not(schema.lateralite[2]==self.lateralite[2]) : return False
        if not(schema.zone[0]==self.zone[0]) : return False
        if not(schema.zone[1]==self.zone[1]) : return False
        if not(schema.zone[2]==self.zone[2]) : return False
        return True
    
    def create_ligne(self):
        ligne=''
        for i in range(len(self.joueur)) :
            ligne+=','+str(self.joueur[i])
            ligne+=','+str(self.lateralite[i])
            ligne+=','+str(self.typecoup[i])
            ligne+=','+str(self.zone[i])
        return ligne

def est_valide(c,l) :
    l1=[0,1,2]
    l2=[3,4,5]
    l3=[6,7,8]
    lcond = deepcopy(l)
    for e in c :
        if e in l1 : l1.remove(e)
        if e in l2 : l2.remove(e)
        if e in l3 : l3.remove(e)
        if not(len(lcond)==0) :
            for i in range(len(lcond)) :
                if e in lcond[i] : lcond[i].remove(e)
    cond = True 
    for l in lcond :
        if len(l) == 0 : 
            return False
    return not(len(l1)==0 or len(l2)==0 or len(l3)==0)

def create_all_schema(nbcond) :
    liste= []
    nbset = len(M.match)
    for j in range(nbset):
        s=M.match[j]
        for e in s.set :
            l=[]
            coups=e.echange
            if e.serveur in serveur and len(coups)>1 :                
                if len(coups)>1 and coups[1].isservice :
                    n=1
                else :
                    n=0
                if len(coups)>n+2 :
                    i=0
                    while not(coups[n+i+2].isgagnant) :
                        if coups[n+i].joueur == WINNER :
                            liste_coup=[coups[n+i]]
                            z=coups[n+i+1].zone
                            liste_zone=[z]
                            liste_coup.append(coups[n+i+1])
                            z=coups[n+i+2].zone
                            liste_zone.append(z)
                            liste_coup.append(coups[n+i+2])
                            z=coups[n+i+3].zone
                            liste_zone.append(z)
                            schema = Schema(liste_coup,liste_zone)
                            liste = schema.generalize(nbcond,liste)
                            print(len(liste))
                        i+=1
                    if coups[n+i].joueur == WINNER :
                        liste_coup=[coups[n+i]]
                        z=coups[n+i+1].zone
                        liste_zone=[z]
                        liste_coup.append(coups[n+i+1])
                        z=coups[n+i+2].zone
                        liste_zone.append(z)
                        liste_coup.append(coups[n+i+2])
                        z='all'
                        liste_zone.append(z)
                        schema = Schema(liste_coup,liste_zone)
                        liste = schema.generalize(nbcond,liste)
                        print(len(liste))
    return liste

def create_sg(seuil=0,nbmax=9,minsup=3):
    LISTE = create_all_schema(nbmax)
    print('1/3')
    
    D=0
    Dwin=0
    dictot={}
    dicwin={}
    for j in range(5):
        s=M.match[j]
        for e in s.set :
            l=[]
            if e.serveur in serveur :
                coups=e.echange
                D+=1
                if e.winner == WINNER : Dwin+=1
                
                if coups[1].isservice :
                    n=1
                else :
                    n=0
                if len(coups)>n+2 :
                    i=0
                    while not(coups[n+i+2].isgagnant) :
                        if coups[n+i].joueur == WINNER :
                            liste_coup=[coups[n+i]]
                            z=coups[n+i+1].zone
                            liste_zone=[z]
                            liste_coup.append(coups[n+i+1])
                            z=coups[n+i+2].zone
                            liste_zone.append(z)
                            liste_coup.append(coups[n+i+2])
                            z=coups[n+i+3].zone
                            liste_zone.append(z)
                            schema = Schema(liste_coup,liste_zone)
                            
                            for k in range(len(LISTE)) :
                                if LISTE[k].contient(schema) and not(k in l) :
                                    l.append(k)
                                    if k in dictot.keys() : dictot[k]+=1
                                    else : dictot[k]=1
                                    if not(k in dicwin.keys()) : dicwin[k]=0
                                    if e.winner == WINNER : dicwin[k]+=1
                        i+=1
                    if coups[n+i].joueur == WINNER :
                        liste_coup=[coups[n+i]]
                        z=coups[n+i+1].zone
                        liste_zone=[z]
                        liste_coup.append(coups[n+i+1])
                        z=coups[n+i+2].zone
                        liste_zone.append(z)
                        liste_coup.append(coups[n+i+2])
                        z='all'
                        liste_zone.append(z)
                        schema = Schema(liste_coup,liste_zone)
                        for k in range(len(LISTE)) :
                            if LISTE[k].contient(schema) and not(k in l) :
                                l.append(k)
                                if k in dictot.keys() : dictot[k]+=1
                                else : dictot[k]=1
                                if not(k in dicwin.keys()) : dicwin[k]=0
                                if e.winner == WINNER : dicwin[k]+=1
                        
    print('2/3')
    if seuil==0 :
        for i in range(len(LISTE)) :
            if i in dictot.keys() :
                if dictot[i]<3 : del dictot[i]
                else :
                    for j in range(len(LISTE)) :
                        if j in dictot.keys() and not(j==i) and LISTE[j].contient(LISTE[i]):
                            if dictot[i]/D*(dicwin[i]/dictot[i]-Dwin/D)==dictot[j]/D*(dicwin[j]/dictot[j]-Dwin/D) :
                                del dictot[j]

    else :
        for i in range(len(LISTE)) :
            if i in dictot.keys() :
                if dictot[i]<3 or dictot[i]/D*(dicwin[i]/dictot[i]-Dwin/D)<seuil : del dictot[i]
                else :
                    for j in range(len(LISTE)) :
                        if j in dictot.keys() and not(j==i) and LISTE[j].contient(LISTE[i]):
                            if dictot[i]/D*(dicwin[i]/dictot[i]-Dwin/D)>=dictot[j]/D*(dicwin[j]/dictot[j]-Dwin/D) :
                                del dictot[j]
    
    dicres={}
    for i in dictot.keys() :
        WRACC = dictot[i]/D*(dicwin[i]/dictot[i]-Dwin/D)
        ligne = str(dictot[i])+','+str(dicwin[i])+','+str(WRACC)+LISTE[i].create_ligne()+"\n"
        dicres[ligne]=WRACC
            
    print('3/3')       
    entete = ['Nombre_Apparition','Nombre_Gagné','WRACC','Joueur1','lat1','Coup1','Zone1','Joueur2','lat2','Coup2','Zone2','Joueur3','lat3','Coup3','Zone3']                
    f = open('WRACC_wFtest.csv', 'w')
    ligneEntete = ",".join(entete) + "\n"
    f.write(ligneEntete)
    for e in sorted(dicres.items(), key=lambda t: t[1], reverse = True) :
        f.write(unidecode(e[0]))
    f.close()
    
    print('Finis')
    
    return dictot,dicwin

tot,win=create_sg(seuil=0.01,nbmax=9,minsup=3)

tf=time()
print(tf-t0)
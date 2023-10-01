# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 16:48:07 2022

@author: pierr
"""

#Lecture des données et création de match 

import csv
import time

LATERALITES = ['Coup droit','Revers']
SERVICES = ['Lateral droit','Lateral gauche','Droit']
COUPS = ['Controle / Resistance','Attaque / Offensif','Poussette']
ZONES = ['M1','M2','M3','D1','D2','D3','G1','G2','G3','G21']
JOUEURS=['FLORE','BOLL']

class Coup :
    
    def __init__(self,numligne,numcoup,joueur,timepos,duree,isservice,isgagnant,lateralite,type_service,type_coup,zone):
        self.numligne=numligne  #int
        self.numcoup=numcoup   #int
        self.joueur=joueur   #int
        self.timepos=timepos   #int (seconde)
        self.duree=duree       #int (seconde)
        self.isservice = isservice   #bool
        self.isgagnant = isgagnant   #bool
        self.lateralite = lateralite  #0 ou 1
        self.typeservice=type_service   #0, 1 ou 2 
        self.typecoup=type_coup.split(' ')[0]    #0, 1 ou 2
        self.zone = zone
        
    def __repr__(self) :
        return str(self.numcoup)+', '+self.joueur+', '+self.typeservice+', '+self.typecoup+', '+self.zone+', '+str(self.isgagnant)
        
        
class Echange :
    
    def __init__(self,e,numechange,serveur,winner,score):
        # Un echange est une liste de coups
        self.echange=e   #Coup List
        self.numechange=numechange    #int
        self.serveur = serveur    #Joueur
        self.winner = winner    #Joueur
        self.score=score #int tuple (score pendant l'échange)
        
    def __repr__(self) :
        res=str(self.score)+'\n'
        for c in self.echange :
            res=res+'\n'+c.__repr__()
        return res

class Set : 
    
    def __init__(self,s,numset,scoreset):
        # Un set est une liste d'échanges
        self.set = s     #Echange List
        self.numset = numset       #int
        self.scoreset =scoreset #int tuple (score du set)
    
    def __repr__(self) :
        res=''
        for e in self.set :
            res=res+'\n'+e.__repr__()
        return res+'\n'+str(self.scoreset)

class Match :
    
    def __init__(self,file) :
        
        def convert_time(l) :
            lp=l.split(':')
            t=float(lp[0])*60+float(lp[1])
            return t
        
        #Un match est une liste de set
        # Ouvrir le fichier csv
        with open(file, 'r',encoding='latin-1') as f:
            # Créer un objet csv à partir du fichier
            obj = csv.reader(f)  
            numligne=1
            numcoup=1
            numechange=1
            numset=0
            self.match=[]
            e=[]
            score_actuel = [0,0]
            for ligne in obj :
                joueur=ligne[0].split(' ')[0]
                if joueur=='Nom' or joueur=='':
                    pass
                elif joueur=='SET':
                    if numset!=0 :
                        self.match.append(Set(s,numset,score_actuel))
                    s=[]
                    score_actuel=[0,0]
                    numset+=1
                else :
                    est_gagnant = ligne[7].split(' ')[0]=='Serveur'
                    est_service=((len(e)==0) or (ligne[8]!=''))
                    if est_service : serveur = joueur
                    if est_gagnant :
                        if ligne[7].split(' ')[2] =='+' :
                            winner = serveur
                        else :
                            if serveur==JOUEURS[0] : winner =JOUEURS[1]
                            if serveur==JOUEURS[1] : winner = JOUEURS[0]
                    e.append(Coup(numligne,numcoup,joueur,convert_time(ligne[1]),convert_time(ligne[2]),est_service,est_gagnant,ligne[4],ligne[8],ligne[9],ligne[10]))
                    if est_gagnant :
                        s.append(Echange(e,numechange,serveur,winner,score_actuel.copy()))
                        e=[]
                        if winner ==JOUEURS[0] : score_actuel[0]=score_actuel[0]+1
                        if winner ==JOUEURS[1] : score_actuel[1]=score_actuel[1]+1
                        numechange+=1
                    numcoup+=1
                numligne+=1
            self.match.append(Set(s,numset,score_actuel))
        
    def __repr__(self) :
        res=''
        for s in self.match :
            res=res+'\n'+s.__repr__()
        return res
    
    def service_manquant(self) :
        l=[]
        for s in self.match :
            for e in s.set :
                for c in e.echange :
                    if c.isservice and c.typeservice=='' :
                        l.append(c.numligne)
        return l
    
    def coup_manquant(self) :
        l=[]
        for s in self.match :
            for e in s.set :
                for c in e.echange :
                    if not(c.isservice) and c.typecoup=='' :
                        l.append(c.numligne)
        return l
    
    def zone_manquant(self) :
        l=[]
        for s in self.match :
            for e in s.set :
                for c in e.echange :
                    if not(c.isservice) and c.zone=='' :
                        l.append(c.numligne)
        return l
    
    def zone_non_necessaire(self) :
        l=[]
        for s in self.match :
            for e in s.set :
                for c in e.echange :
                    if c.isservice and c.zone!='' :
                        l.append(c.numligne)
        return l
    
    def alternance(self) :
        l=[]
        for s in self.match :
            for e in s.set :
                j1 = e.echange[0].joueur
                begin=1
                if len(e.echange)>0 and e.echange[1].isservice :
                    begin+=1
                for i in range(begin,len(e.echange)-1) :
                    c=e.echange[i]
                    j2=c.joueur
                    if j1==j2:
                        l.append(c.numligne)
                    j1=j2
        return l
    
        
    

if __name__ == "__main__" :
    M=Match('Flore Boll corrige.csv')
    #M=Match('Flore Boll-1 (1).csv')
    print(M.service_manquant())
    print(M.coup_manquant())
    print(M.zone_manquant())
    print(M.zone_non_necessaire())
    print(M.alternance())
    
    
    
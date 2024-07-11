import numpy as np
import os,sys,math, copy, pickle
from scipy.spatial import distance
from random import seed,random,randint
import pandas as pd
import matplotlib.pyplot as plt

#coloca o ponto de acesso 'ponto' em um lugar aleatorio
#troca o status de um ponto de acesso
def k1(dados):
    uso_PAs = dados['uso_PAs'].copy() #PAs ativos
    cliente_por_PA = dados['cliente_por_PA'].copy() #cliente x pa

    pas_act = np.where(uso_PAs==1)[0]
    pas_dact = np.where(uso_PAs==0)[0]

    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0 and len(pas_dact) > 0:

        pv = np.random.choice(pas_act, size=1, replace=False)
        pn = np.random.choice(pas_dact, size=1, replace=False)
        
        #passando todos os clientes que são atendidos pelo ponto de acesso para o novo ponto de acesso
        nad = cliente_por_PA[:,pn].copy()
        cliente_por_PA[:,pn] = cliente_por_PA[:,pv].copy()
        cliente_por_PA[:,pv] = nad.copy()

        #trocando o estados de utilização dos pontos de acesso
        uso_PAs[pv] = not uso_PAs[pv]
        uso_PAs[pn] = not uso_PAs[pn]
        #atualizando 
        dados['uso_PAs'] = uso_PAs
        dados['cliente_por_PA'] = cliente_por_PA

    return dados

#Coloca para um cliente ser atendido por outro ponto de acesso ativo
def k2(dados):
    uso_PAs = dados['uso_PAs'].copy()
    cliente_por_PA = dados['cliente_por_PA'].copy()

    pas_act = np.where(uso_PAs==1)[0]

    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0:

        pn = np.random.choice(pas_act, size=1, replace=False)
        cliente = np.random.choice(cliente_por_PA.shape[0], size=1, replace=False)
    
        pontovelho = cliente_por_PA[cliente,:] == 1
        cliente_por_PA[cliente,pontovelho[0]] = 0
        cliente_por_PA[cliente,pn] = 1
    
        dados['uso_PAs'] = uso_PAs
        dados['cliente_por_PA'] = cliente_por_PA
    
    return dados
    
#Altera o estado do ponto de acesso 
def k3(dados):
    uso_PAs = dados['uso_PAs'].copy()
    cliente_por_PA = dados['cliente_por_PA'].copy()


    pas_act = np.where(uso_PAs==1)[0]

    if len(pas_act) > 0:
        pv = np.random.choice(pas_act, size=1, replace=False)
        clt = np.where(cliente_por_PA[:,pv]==1)
        for c in clt:
            ps = np.random.choice(pas_act, size=1, replace=False)
            if ps == pv:
                ps = np.random.choice(pas_act, size=1, replace=False)
                cliente_por_PA[c,ps] = 1
        cliente_por_PA[clt, pv] = 0 
        
    
        uso_PAs[pv] = 0
        dados['uso_PAs'] = uso_PAs
        dados['cliente_por_PA'] = cliente_por_PA

    return dados


#Redistribui aleatoriamente os clientes
def k4(dados):
    uso_PAs = dados['uso_PAs'].copy()
    cliente_por_PA = dados['cliente_por_PA'].copy()

    pas_act = np.where(uso_PAs==1)[0]
    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0:
        clt1 = np.random.choice(pas_act, size=1, replace=False)
        clt2 = np.random.choice(pas_act, size=1, replace=False)
        #para cada cliente redistribui os clientes para cada um que será ativo
        clientes_1 = cliente_por_PA[:,clt1].copy()
        clientes_2 = cliente_por_PA[:,clt2].copy()
        clt1_ac = np.where(clientes_1==1)[0]
        clt2_ac = np.where(clientes_2==1)[0]
        if len(clt1_ac) > 0 and len(clt2_ac) > 0:
            s1 = np.random.choice(clt1_ac, size=1, replace=False)
            s2 = np.random.choice(clt2_ac, size=1, replace=False)
            clientes_1[s1], clientes_1[s2] = 0, 1
            clientes_2[s2], clientes_2[s1] = 0, 1
            cliente_por_PA[:,clt1] = clientes_1
            cliente_por_PA[:,clt2] = clientes_2

    dados['uso_PAs'] = uso_PAs
    dados['cliente_por_PA'] = cliente_por_PA
    return dados
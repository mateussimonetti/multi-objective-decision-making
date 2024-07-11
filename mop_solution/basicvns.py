import numpy as np
import os,sys,math, copy, pickle
from scipy.spatial import distance
from random import seed,random,randint
from estrutura_vizinhanca import k1,k2,k3,k4
from restricoes import r3,r4,r5,r6,r7,sum_restr
from graph_maker import plot_infos
import pandas as pd
import matplotlib.pyplot as plt


seed(321)
np.random.seed(321)

#Algoritmo para Basic VNS

#k_max Número de estruturas de vizinhaças definidas. No máximo, será 4
#max_int numero maximo de tentativas de novos valores
def basic_VNS(dados, f, k_max, max_int, plot, n_plot):
    nfe = 0
    n_ap, y_save, r3_save, r4_save, r5_save, r6_save, r7_save = [], [], [], [], [], [], []
    if (k_max > 4):
        k_max = 4
    
    # Solução inicial
    dados = sol_zero(copy.copy(dados))

    y = f(dados)

    while(nfe < max_int):
        print('Interação: {}'.format(nfe))
        print('Valor f(x): {:.4f}'.format(y))
        k = 1
        while(k<=k_max):
            print('k: {}; f(x): {:.4f}'.format(k,y))
            dados_ = shake(copy.copy(dados),k) # Solução na kesima vizinhança
            dados__ = best_change(copy.copy(dados_), f)
            dados, k = neigh_change(copy.copy(dados), copy.copy(dados__), k, f) # atualiza x
            y = f(dados)
            #update log
            n_ap.append(np.sum(dados['uso_PAs']))

        y_save.append(y)
        r3_save.append(r3(dados))
        r4_save.append(r4(dados))
        r5_save.append(r5(dados))
        r6_save.append(r6(dados))
        r7_save.append(r7(dados))
        

        if plot and nfe % n_plot == 0:
            log = [y_save, r3_save, r4_save, r5_save, r6_save, r7_save, n_ap]
            plot_infos(dados, log, 'output/mop_graphs/info/', str(nfe))
        nfe +=1
    return dados, [y_save, r3_save, r4_save, r5_save, r6_save, r7_save, n_ap]

#aplica perturbação
def shake(dados, k):
    n_change = 1
    switch = {
        1: k1,
        2: k2,
        3: k3,
        4: k4
    }
    return switch[k](dados)

#função do numero de PAs a ser instalado
def f1(dados):
    uso_PAs = dados['uso_PAs']
    f1 = sum(uso_PAs)
    f1_penal = f1 + 10 * (sum_restr(dados))

    return f1_penal

#funcao da distancia entre usuários e PA's
def f2(dados):
    cliente_por_PA = dados['cliente_por_PA']
    possiveis_coord_PA = dados['possiveis_coord_PA']
    coord_clientes = dados['coord_clientes']
    dist_cliente_PA = dados['dist_cliente_PA']
    
    f2_value = 0
    for id_c,c in enumerate(coord_clientes):
        for id_p,p in enumerate(possiveis_coord_PA):
            f2_value += dist_cliente_PA[id_c, id_p] * cliente_por_PA[id_c][id_p]
    
    f2_penal = f2_value + sum_restr(dados)

    return f2_penal

#retorna um valor inicial factível
def sol_zero(dados):
    # Calcula as coordenadas dos possíveis PAs
    coord_clientes = dados['coord_clientes']
    possiveis_coord_PA = dados['possiveis_coord_PA']
    dist_cliente_PA = dados['dist_cliente_PA']
    uso_PAs = dados['uso_PAs']
    n_max_PAs = dados['n_max_PAs']
    cliente_por_PA = dados['cliente_por_PA']
    sizex = dados['sizex']
    sizey = dados['sizey']
    grid_PAs = dados['grid_PAs']

    i=0
    for x in range(sizex[0], sizex[1], grid_PAs[0]):
        for y in range(sizey[0], sizey[1], grid_PAs[1]):
            possiveis_coord_PA[i, 0] = x
            possiveis_coord_PA[i, 1] = y
            i = i + 1

    # calcula distancia entre cada cliente a cada ponto de acesso
    for id_c, c in enumerate(coord_clientes):
        for id_p, p in enumerate(possiveis_coord_PA):
            dist_cliente_PA[id_c, id_p] = distance.euclidean(c, p)

    # gera solucao inicial - PAs ativos
    uso_PAs = np.zeros(len(possiveis_coord_PA))
    n_aps_act = np.random.randint(1,n_max_PAs)
    index = np.random.randint(0, uso_PAs.size, n_aps_act)
    uso_PAs[index] = 1

    # gera solucao inicial - clientes atendidos
    for i in range(0, len(cliente_por_PA)):
        j = np.random.choice(index)
        cliente_por_PA[i, j] = 1

    #atualiza os dados
    dados['possiveis_coord_PA'] = possiveis_coord_PA
    dados['uso_PAs'] = uso_PAs
    dados['cliente_por_PA'] = cliente_por_PA

    return dados

#Verifica
def neigh_change(x, x_linha, k, f):
    if f(x_linha) < f(x):
        return x_linha, 1
    return x, k + 1

#avalia a melhor configuração entre o valor atual, o valor "shiftado pra frente" e "shiftado para trás"
def best_change(dados, f):
    new_dados = [copy.deepcopy(dados) for _ in range(3)]  # Criando três cópias dos dados originais

    # Seleciona índice de ap válido
    ponto = False
    while not ponto:
        pv = np.random.choice(dados['uso_PAs'].shape[0], size=1, replace=False)  # pv é o índice de um ponto ativo
        ponto = dados['uso_PAs'][pv]

    # Verifica limites do índice
    pv = min(max(pv, 1), len(dados['uso_PAs']) - 2)

    # Shift para trás
    for i in range(len(new_dados[1]['cliente_por_PA'][:, pv])):
        new_dados[1]['cliente_por_PA'][i, pv], new_dados[1]['cliente_por_PA'][i, pv - 1] = \
            new_dados[1]['cliente_por_PA'][i, pv - 1], new_dados[1]['cliente_por_PA'][i, pv]
    new_dados[1]['uso_PAs'][pv - 1], new_dados[1]['uso_PAs'][pv] = new_dados[1]['uso_PAs'][pv], new_dados[1]['uso_PAs'][pv - 1]

    # Shift para frente
    for i in range(len(new_dados[2]['cliente_por_PA'][:, pv])):
        new_dados[2]['cliente_por_PA'][i, pv], new_dados[2]['cliente_por_PA'][i, pv + 1] = \
            new_dados[2]['cliente_por_PA'][i, pv + 1], new_dados[2]['cliente_por_PA'][i, pv]
    new_dados[2]['uso_PAs'][pv + 1], new_dados[2]['uso_PAs'][pv] = new_dados[2]['uso_PAs'][pv], new_dados[2]['uso_PAs'][pv + 1]

    # Avalia as funções objetivo
    f_values = [float(f(d)) for d in new_dados]

    # Retorna os dados correspondentes à melhor função objetivo
    return new_dados[np.argmax(f_values)]

#MAIN
if __name__ == "__main__":

    #Pega valores da chamada
    path_file = sys.argv[1]
    n_sol = int(sys.argv[2])
    k_max = int(sys.argv[3])
    max_int_vns = int(sys.argv[4])
    n_plot = int(sys.argv[5])
    f_desejada = sys.argv[6]
    
    print('Numero de solucoes: {}'.format(n_sol))
    print('K maximo: {} (no max 4)'.format(k_max))
    print('Numero maximo de interacoes: {}'.format(max_int_vns))

    df = pd.read_csv(path_file)
    mtx_clientes = df.values
    #Inicializa variáveis
    sizex = (0,400)
    sizey = (0,400)
    dist_grid_PAs = 5
    grid_PAs = (dist_grid_PAs,dist_grid_PAs)
    num_possiveis_alocacoes = int((sizex[1]*sizey[1])/ (grid_PAs[0]*grid_PAs[1]))  
    coord_clientes = mtx_clientes[:,:2]  # coordenadas dos clientes (x,y)
    num_clientes = len(coord_clientes)
    cons_clientes = mtx_clientes[:,2:]  # consumo do cliente i
    possiveis_coord_PA =  np.zeros((num_possiveis_alocacoes, 2)) #conjunto de possiveis locais para alocar P
    n_max_possivel_PAs = len(possiveis_coord_PA)
    capacidade_PA = 54 #capacidade do ponto de acesso p, em Mbps
    limite_sinal_PA = 85 # limite do sinal do ponto de acesso, em metros
    tx_coverage = 0.98 # taxa de cobertura dos clientes
    n_max_PAs = 30 #numero maximo de PAs disponiveis
    uso_PAs = np.zeros(n_max_possivel_PAs) # vetor binario para indicar se o PA i está sendo usado ou nao
    dist_cliente_PA = np.zeros((num_clientes, n_max_possivel_PAs)) # vetor de distacias
    cliente_por_PA = np.zeros((num_clientes, n_max_possivel_PAs)) #Matriz de numero de clientes por numero de PAs indica se a PA é utilizada pelo cliente

    x = {
        'dist_cliente_PA':dist_cliente_PA,
        'coord_clientes': coord_clientes,
        'cons_clientes': cons_clientes.reshape(-1,),
        'possiveis_coord_PA': possiveis_coord_PA,
        'capacidade_PA': capacidade_PA,
        'limite_sinal_PA': limite_sinal_PA,
        'tx_coverage': tx_coverage,
        'n_max_PAs': n_max_PAs,
        'uso_PAs': uso_PAs,
        'cliente_por_PA': cliente_por_PA,
        'grid_PAs':grid_PAs,
        'sizex':sizex,
        'sizey':sizey
    }

    #Otimizando
    if (f_desejada == "f1"):
        sol, log = basic_VNS(x, f1, k_max, max_int_vns, bool(n_plot), n_plot)
    else:
        sol, log = basic_VNS(x, f2, k_max, max_int_vns, bool(n_plot), n_plot)
    
    #print solution
    print('[Resultado] VNS:')
    print('Numero de Pontos de acesso: {}'.format(log[6][-1]))
    print('Valor de y: {}'.format(log[0][-1]))
    print('Valor de Rest3: {}'.format(log[1][-1]))
    print('Valor de Rest4: {}'.format(log[2][-1]))
    print('Valor de Rest5: {}'.format(log[3][-1]))
    print('Valor de Rest6: {}'.format(log[4][-1]))
    print('Valor de Rest7: {}'.format(log[5][-1]))
    
    #plot solution
    plot_infos(sol, log, dir_='output/vns/info/')
    
    
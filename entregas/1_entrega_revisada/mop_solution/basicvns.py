import numpy as np
import os
import sys, copy
from random import seed
from estrutura_vizinhanca import k1, k2, k3, k4, k5, k6, k7, k8, k9
from restricoes import r3,r4,r5,r6,r7,r8,sum_restr
from graph_maker import plot_infos
from solution import sol_zero
import pandas as pd
import time


np.random.seed(int(time.time()))

#Algoritmo para Basic VNS

#k_max Número de estruturas de vizinhaças definidas. No máximo, será 4
#max_int numero maximo de tentativas de novos valores
def basic_VNS(dados, f, k_max, max_int, plot, n_plot):
    nfe = 0
    n_ap, y_save, r3_save, r4_save, r5_save, r6_save, r7_save, r8_save = [], [], [], [], [], [], [], []
    if (k_max > 9):
        k_max = 9
    
    # Solução inicial
    dados = sol_zero(copy.deepcopy(dados))

    y = f(dados)

    while(nfe < max_int):
        print(f"{nfe+1}a interacao")
        print('f(x) inicial: {:.4f}'.format(y))
        k = 1
        while(k<=k_max):
            print('f(x): {:.4f} | k = {}'.format(y,k))
            dados_ = shake(copy.deepcopy(dados),k) # Solução na kesima vizinhança
            dados__ = best_change(copy.deepcopy(dados_), f)
            dados, k = neigh_change(copy.deepcopy(dados), copy.deepcopy(dados__), k, f) # atualiza x
            y = f(dados)
            #update log
            n_ap.append(len(dados['possiveis_coord_PA']))
        nfe +=1

    y_save.append(y)
    r3_save.append(r3(dados))
    r4_save.append(r4(dados))
    r5_save.append(r5(dados))
    r6_save.append(r6(dados))
    r7_save.append(r7(dados))
    r8_save.append(r8(dados))

    if plot and nfe % n_plot == 0:
        log = [y_save, r3_save, r4_save, r5_save, r6_save, r7_save, r8_save, n_ap]
        plot_infos(dados, log, 'output/mop_graphs/info/', str(nfe))
        
    return dados, [y_save, r3_save, r4_save, r5_save, r6_save, r7_save, r8_save, n_ap]

#aplica perturbação
def shake(dados, k):
    # Recomendação para redução de PAs
    # switch = {1: k1, 2: k6, 3: k3, 4: k5 }
    # Recomendação para redução de distancia
    # switch = {1: k5, 2: k7, 3: k3, 4: k4 }
    #Recomendação para ambas
    # switch = {1: k1, 2: k6, 3: k5, 4: k4 }

    switch = {1: k1, 2: k2, 3: k3, 4: k4, 5: k5, 6: k6, 7: k7, 8: k8, 9: k9  }

    return switch[k](dados)

#função do numero de PAs a ser instalado
def f1(dados, log = None):
    amplitude_f1 = 10
    max_penal_somado = 45
    multiplicador = (25/100) * amplitude_f1 / max_penal_somado
    f1 = len(dados['possiveis_coord_PA'])
    if (sum_restr(dados) > 0):
        if log is not None:
            print("restr impossiveis > 1")
        return 1e24
    if log is not None:
        print(f"ultima interação, f1 = {f1}")
    return f1

#funcao da distancia entre usuários e PA's
def f2(dados, log = None):
    amplitude_f2 = 15000
    max_penal_somado = 45
    multiplicador = (25/100) * amplitude_f2 / max_penal_somado
    cliente_por_PA = dados['cliente_por_PA']
    coord_PAs = dados['possiveis_coord_PA']
    dist_matrix = np.load('dist_matrix.npy')
    mascara = np.any(coord_PAs != 0, axis=1)
    pas_ativos = coord_PAs[mascara]
    coord_pas_ativos = pas_ativos / 5
    coord_pas_ativos = coord_pas_ativos.astype(int)
    f2 = 0
    for i, pa in enumerate(coord_pas_ativos):
        f2 += np.dot(dist_matrix[pa[0]][pa[1]], cliente_por_PA[:, i])
    if (sum_restr(dados) > 0):
        if log is not None:
            print("restr impossiveis > 1")
        return 1e24
    if log is not None:
        print(f"ultima interação, f2 = {f2}")
    return f2 

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
    return new_dados[np.argmin(f_values)]

#MAIN
if __name__ == "__main__":
    inicio = time.time()

    #Pega valores da chamada
    path_file = sys.argv[1]
    k_max = int(sys.argv[2])
    max_int_vns = int(sys.argv[3])
    n_plot = int(sys.argv[4])
    f_desejada = sys.argv[5]
    
    print('----------Basic VNS: params iniciais-----------')
    print('K maximo: {} (no max 9)'.format(k_max))
    print('Numero máximo de interacoes: {}'.format(max_int_vns))
    print('------------------------------------------------')

    df = pd.read_csv(path_file, header=None)
    mtx_clientes = df.values
    #Inicializa variáveis
    sizex = (0,400)
    sizey = (0,400)
    dist_grid_PAs = 5
    capacidade_PA = 54 #capacidade do ponto de acesso p, em Mbps
    limite_sinal_PA = 85 # limite do sinal do ponto de acesso, em metros
    tx_coverage = 0.98 # taxa de cobertura dos clientes
    n_max_PAs = 30 #numero maximo de PAs disponiveis
    coord_clientes = mtx_clientes[:,:2]  # coordenadas dos clientes (x,y)
    num_clientes = len(coord_clientes)
    grid_PAs = (dist_grid_PAs,dist_grid_PAs)
    num_possiveis_alocacoes = int((sizex[1]*sizey[1])/ (grid_PAs[0]*grid_PAs[1]))  
    cons_clientes = mtx_clientes[:,2:]  # consumo do cliente i
    possiveis_coord_PA =  np.zeros([]) #conjunto de possiveis locais para alocar P
    uso_PAs = np.zeros(n_max_PAs) # vetor binario para indicar se o PA i está sendo usado ou nao
    dist_cliente_PA = np.zeros((num_clientes, n_max_PAs)) # vetor de distacias
    cliente_por_PA = np.zeros((num_clientes, n_max_PAs)) #Matriz de numero de clientes por numero de PAs indica se a PA é utilizada pelo cliente
    
    if not os.path.exists('dist_matrix.npy'):
    # Inicializar a matriz tridimensional
        dim_x_matriz = int(sizex[1] // grid_PAs[0]) + 1
        dim_y_matriz = int(sizey[1] // grid_PAs[1]) + 1
        dist_matrix = np.zeros((dim_x_matriz, dim_y_matriz, num_clientes))

        # Calcular as coordenadas centrais de cada célula no grid
        
        grid_coords = np.array([[(i * grid_PAs[0], j * grid_PAs[1])
                                for j in range(dim_y_matriz+1)] for i in range(dim_x_matriz+1)])

        # Calcular as distâncias euclidianas
        for i in range(dim_x_matriz):
            for j in range(dim_y_matriz):
                for k in range(num_clientes):
                    dist_matrix[i][j][k] = np.linalg.norm(coord_clientes[k] - grid_coords[i][j])
        # Escrever a matriz em um arquivo
        np.save('dist_matrix.npy', dist_matrix)

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
    
    #plot solution
    plot_infos(sol, log, dir_='output/vns/info/')
    
    # print solution
    print('-------------------------- SOLUCAO OTIMA ENCONTRADA------------------------------')
    print('[Resultado]:')
    print('Numero de PAs: {}'.format(log[7][-1]))
    print(f'Valor de F(x) (f1 = numero de PAs | f2: distancia total): {log[0][-1]:.2f}')
    print('Restricoes: 0 -> cumprida | maior que 0 -> nao cumprida')
    print('Restricao de taxa de cobertura: {}'.format(log[1][-1]))
    print('Restricao de capacidade dos PAs: {}'.format(log[2][-1]))
    print('Restricao de apenas 1 PA por cliente: {}'.format(log[3][-1]))
    print('Restricao de numero maximo de PAs disponiveis: {}'.format(log[4][-1]))
    print('Restricao de distancia do usuario ao PA: {}'.format(log[5][-1]))
    print('Restricao de exposição dos usuarios aos PAs: {}'.format(log[6][-1]))

    fim = time.time()
    tempo_total_segundos = fim - inicio

    # Converter para horas, minutos e segundos
    horas = int(tempo_total_segundos // 3600)
    minutos = int((tempo_total_segundos % 3600) // 60)
    segundos = int(tempo_total_segundos % 60)

    # Formatando a saída
    print(f"Tempo de execução: {horas} horas, {minutos} minutos e {segundos} segundos")
    print('\n\n')


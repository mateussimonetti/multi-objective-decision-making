import numpy as np
import math

def r3(dados):
    tx_coverage = dados['tx_coverage'] # Taxa de cobertura
    coord_clientes = dados['coord_clientes'] # Coordenadas dos clientes
    cliente_por_PA = dados['cliente_por_PA']

    penal = int(tx_coverage * len(coord_clientes)) - cliente_por_PA.sum()
    penal = max(0, penal) ** 2
    return penal * 10000

# Garante nao estourar a capacidade do ponto de acesso
def r4(dados):
    cliente_por_PA = dados['cliente_por_PA']
    cons_clientes = dados['cons_clientes']
    capacidade_PA = dados['capacidade_PA']
    possiveis_coord_PA = dados['possiveis_coord_PA']
    penal = 0
    for id_p,p in enumerate(possiveis_coord_PA):
        penal += max(0, np.sum(cliente_por_PA[:,id_p]*cons_clientes) - capacidade_PA)
    return penal

# garante que cada cliente estará conectado a no maximo 1 PA
def r5(dados):
    cliente_por_PA = dados['cliente_por_PA']
    penal = 0
    coord_clientes = dados['coord_clientes'] # Coordenadas dos clientes

    for id_c,c in enumerate(coord_clientes):
        penal += max(0, np.sum(cliente_por_PA[id_c,:]) - 1)
    return penal

# garante que nao exceda o numero de pontos de acesso
def r6(dados):
    uso_PAs = dados['uso_PAs']
    n_max_PAs = dados['n_max_PAs']

    penal = np.sum(uso_PAs) - n_max_PAs
    penal = max(0, penal) ** 2

    return penal

# Garante que a distancia nao exceda a distancia max de um ponto de acesso (?)
def r7(dados):
    cliente_por_PA = dados['cliente_por_PA']
    limite_sinal_PA = dados['limite_sinal_PA']
    dist_cliente_PA = dados['dist_cliente_PA']
    coord_clientes = dados['coord_clientes'] # Coordenadas dos clientes
    possiveis_coord_PA = dados['possiveis_coord_PA']
    penal = 0
    for id_c,c in enumerate(coord_clientes):
        for id_p,p in enumerate(possiveis_coord_PA):
            penal += max(0, (dist_cliente_PA[id_c, id_p] * cliente_por_PA[id_c][id_p]) - limite_sinal_PA)

    return penal * 100


def sum_restr(dados):
    return r3(dados) + r4(dados) + r5(dados) + r6(dados) + r7(dados)
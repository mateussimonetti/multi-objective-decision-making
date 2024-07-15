import numpy as np

def r3(dados):
    tx_coverage = dados['tx_coverage'] # Taxa de cobertura
    coord_clientes = dados['coord_clientes'] # Coordenadas dos clientes
    cliente_por_PA = dados['cliente_por_PA']

    penal = int(tx_coverage * len(coord_clientes)) - cliente_por_PA.sum()
    penal = max(0, penal) ** 2
    return penal

# Garante nao estourar a capacidade do ponto de acesso
def r4(dados):
    cliente_por_PA = dados['cliente_por_PA']
    cons_clientes = dados['cons_clientes']
    capacidade_PA = dados['capacidade_PA']
    possiveis_coord_PA = dados['possiveis_coord_PA']
    penal = 0
    for id_p,p in enumerate(possiveis_coord_PA):
        penal += max(0, np.sum(cliente_por_PA[:,id_p]*cons_clientes) - capacidade_PA)

    # if penal > 0:
    #     print('biziu r4')
    return penal

# garante que cada cliente estará conectado a no maximo 1 PA
def r5(dados):
    cliente_por_PA = dados['cliente_por_PA']
    penal = 0
    coord_clientes = dados['coord_clientes'] # Coordenadas dos clientes

    for id_c,c in enumerate(coord_clientes):
        penal += max(0, np.sum(cliente_por_PA[id_c,:]) - 1)
    # if penal > 0:
    #     print('biziu r5')
    return penal

# garante que nao exceda o numero de pontos de acesso
def r6(dados):
    uso_PAs = dados['uso_PAs']
    n_max_PAs = dados['n_max_PAs']

    penal = np.sum(uso_PAs) - n_max_PAs
    penal = max(0, penal)
    # if penal > 0:
    #     print('biziu r6')

    return penal

# Garante que a distancia nao exceda a distancia max de um ponto de acesso
def r7(dados, teste = None):

    coord_PAs = dados['possiveis_coord_PA']
    cliente_por_PA = dados['cliente_por_PA']
    limite_sinal_PA = dados['limite_sinal_PA']
    distancias = calcular_distancias_cliente_PA(coord_PAs, cliente_por_PA, dados)
    rel_cliente_range = distancias - limite_sinal_PA
    distancias_positivas = rel_cliente_range[rel_cliente_range > 0]
    if teste is not None:
        np.savetxt('matriz_distancias_restr.txt', distancias, fmt='%.2f')
    penal = np.sum(distancias_positivas)
    # if penal > 0:
    #     print('biziu r7')
    return penal

def r8(dados):
        coord_PAs = dados['possiveis_coord_PA']
        dist_matrix = np.load('dist_matrix.npy')
        coord_pas_ativos = coord_PAs / 5
        coord_pas_ativos = coord_pas_ativos.astype(int)
        num_PAs = len(coord_pas_ativos)
        num_clientes = int(dist_matrix.shape[2])
        exposicao = np.zeros((num_PAs, num_clientes))
        for i, pa in enumerate(coord_pas_ativos):
            exposicao[i] = 1 / dist_matrix[pa[0]][pa[1]]
        soma_exposicoes = np.sum(exposicao, axis=0)
        pessoas_com_exp_abaixo = np.sum(soma_exposicoes < 0.05)
        # if pessoas_com_exp_abaixo > 0:
        #     print('biziu r8')
        return pessoas_com_exp_abaixo


def sum_restr(dados):
    return r3(dados) + r4(dados) + r5(dados) + r6(dados) + r7(dados) + r8(dados)

def calcular_distancias_cliente_PA(coord_PAs, cliente_por_PA, dados =  None):
    dist_matrix = np.load('dist_matrix.npy')
    num_clientes = int(dist_matrix.shape[2]) # 495
    pas_ativos = coord_PAs
    num_PAs = len(pas_ativos)
    coord_pas_ativos = pas_ativos / 5
    coord_pas_ativos = coord_pas_ativos.astype(int)
    distancias = np.zeros((num_PAs, num_clientes))

    for i, pa in enumerate(coord_pas_ativos):
        # if len(coord_pas_ativos) == 14:
        #     print(f"Para o PA {pa[0]} {pa[1]}")
        #     print(f"dist matrix: {dist_matrix[pa[0]][pa[1]][:20]}")
        #     print(f"cliente_por_PA: {cliente_por_PA[:, i][:20]}")
        distancias[i] = dist_matrix[pa[0]][pa[1]] * cliente_por_PA[:, i]




    
    # np.savetxt('matriz_distancias.txt', distancias.T, fmt='%.2f')
    # np.savetxt('cliente_por_PA.txt', cliente_por_PA, fmt='%.2f')
    # np.savetxt('coord_pas_ativos.txt', coord_pas_ativos, fmt='%.2f')


    return distancias.T
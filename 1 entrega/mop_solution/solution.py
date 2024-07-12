import numpy as np
from restricoes import r3,r4,r5,r6,r7,sum_restr

import math

def sol_zero(dados):
    sizex = dados['sizex'][1]
    sizey = dados['sizey'][1]
    diam_PA = dados["limite_sinal_PA"] * 2
    lado_quad_circunsc = diam_PA / math.sqrt(2)
    divisores_lado_area = encontrar_divisores(sizex)
    tamanho_quadrado = lado_quad_circunsc
    for i, divisor in enumerate(divisores_lado_area):
        if (divisor > lado_quad_circunsc):
            tamanho_quadrado = divisores_lado_area[i-1]
            break
    coord_clientes = dados['coord_clientes']
    possiveis_coord_PA = dados['possiveis_coord_PA']
    n_max_possivel_PAs = len(possiveis_coord_PA)

    # Calcular o número de quadrados em cada dimensão
    num_quadrados_x = int(np.ceil(sizex / tamanho_quadrado))
    num_quadrados_y = int(np.ceil(sizey / tamanho_quadrado))

    # Criar uma grade de quadrados
    grade_quadrados = np.zeros((num_quadrados_x, num_quadrados_y), dtype=int)

    # Atribuir cada ponto a um quadrado
    for coord in coord_clientes:
        x_index = int(coord[0] // tamanho_quadrado)
        y_index = int(coord[1] // tamanho_quadrado)
        grade_quadrados[x_index, y_index] += 1

    # Inicializar arrays para centroides e uso de PAs
    uso_PAs = np.zeros(n_max_possivel_PAs, dtype=bool)

    # Ordenar quadrados por população (do mais populoso para o menos populoso)
    quadrados_populosos = [(x, y, grade_quadrados[x, y]) for x in range(num_quadrados_x) for y in range(num_quadrados_y)]
    quadrados_populosos.sort(key=lambda x: x[2], reverse=True)

    # Calcular centroides e alocar PAs
    for x, y, _ in quadrados_populosos:
        if grade_quadrados[x, y] > 0:
            # Encontrar clientes neste quadrado
            clientes_no_quadrado = coord_clientes[(coord_clientes[:, 0] >= x * tamanho_quadrado) &
                                                  (coord_clientes[:, 0] < (x + 1) * tamanho_quadrado) &
                                                  (coord_clientes[:, 1] >= y * tamanho_quadrado) &
                                                  (coord_clientes[:, 1] < (y + 1) * tamanho_quadrado)]

            # Calcular o centroide
            centroid = np.mean(clientes_no_quadrado, axis=0)
            posicao_PA = np.floor(centroid / 5) * 5

            # Encontrar o índice disponível para PA
            pa_index = np.where(~uso_PAs)[0][0]

            # Atualizar dados
            possiveis_coord_PA[pa_index] = posicao_PA
            uso_PAs[pa_index] = True

            # Atribuir clientes ao PA mais próximo
            for i, coord in enumerate(coord_clientes):
                if x * tamanho_quadrado <= coord[0] < (x + 1) * tamanho_quadrado and \
                   y * tamanho_quadrado <= coord[1] < (y + 1) * tamanho_quadrado:
                    dados['cliente_por_PA'][i, pa_index] = 1

    # Atualizar dados
    dados['dist_cliente_PA'] = calcular_distancias_cliente_PA(coord_clientes, possiveis_coord_PA)
    dados['uso_PAs'] = uso_PAs

    return dados


def calcular_distancias_cliente_PA(coord_clientes, coord_PAs):
    num_clientes = len(coord_clientes)
    num_PAs = len(coord_PAs)
    distancias = np.zeros((num_clientes, num_PAs))

    for i, cliente in enumerate(coord_clientes):
        for j, pa in enumerate(coord_PAs):
            distancias[i, j] = np.linalg.norm(cliente - pa)

    return distancias

def encontrar_divisores(numero):
    if numero <= 0:
        return []  # Retorna lista vazia para números não positivos

    divisores = []
    raiz = int(math.sqrt(numero))
    
    for i in range(1, raiz + 1):
        if numero % i == 0:
            divisores.append(i)
            if i != numero // i:
                divisores.append(numero // i)

    return sorted(divisores)  # Ordena os divisores, se necessário
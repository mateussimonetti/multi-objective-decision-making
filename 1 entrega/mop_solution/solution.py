import numpy as np
from sklearn.cluster import DBSCAN

def sol_zero(dados, tamanho_quadrado=50):
    sizex = dados['sizex'][1]
    sizey = dados['sizey'][1]
    coord_clientes = dados['coord_clientes']
    num_clientes = len(coord_clientes)
    possiveis_coord_PA = dados['possiveis_coord_PA']
    n_max_possivel_PAs = len(possiveis_coord_PA)

    # Calcular o número de quadrados em cada dimensão
    num_quadrados_x = int(np.ceil(sizex / tamanho_quadrado))
    num_quadrados_y = int(np.ceil(sizey / tamanho_quadrado))

    # Criar uma grade de quadrados
    grade_quadrados = np.zeros((num_quadrados_x, num_quadrados_y), dtype=int)

    # Atribuir cada ponto a um quadrado
    for i, coord in enumerate(coord_clientes):
        x_index = int(coord[0] // tamanho_quadrado)
        y_index = int(coord[1] // tamanho_quadrado)
        grade_quadrados[x_index, y_index] += 1

    # Inicializar arrays para centroides e uso de PAs
    uso_PAs = np.zeros(n_max_possivel_PAs, dtype=bool)

    # Calcular centroides para cada quadrado com pelo menos um cliente
    for x in range(num_quadrados_x):
        for y in range(num_quadrados_y):
            if grade_quadrados[x, y] > 0:
                # Encontrar clientes neste quadrado
                clientes_no_quadrado = coord_clientes[(coord_clientes[:, 0] >= x * tamanho_quadrado) &
                                                      (coord_clientes[:, 0] < (x + 1) * tamanho_quadrado) &
                                                      (coord_clientes[:, 1] >= y * tamanho_quadrado) &
                                                      (coord_clientes[:, 1] < (y + 1) * tamanho_quadrado)]

                # Calcular o centroide
                centroid = np.mean(clientes_no_quadrado, axis=0)
                posicao_PA = np.round(centroid / 5) * 5

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
    dados['uso_PAs'] = uso_PAs

    return dados

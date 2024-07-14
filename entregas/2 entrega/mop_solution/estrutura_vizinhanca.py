import numpy as np
from restricoes import calcular_distancias_cliente_PA, sum_restr, r3, r4, r5, r6, r7, r8
from solution import client_is_able_to_connect

"""
Novo código para estruturas de vizinhança
Ainda sendo testado
"""

def k1(dados):
    """
    Estrutura de vizinhança que desativa o PA ativo com menos clientes
    e redistribui seus clientes para outros PAs ativos, considerando
    apenas o número de PAs atualmente ativos.

    Args:
        dados: Um dicionário contendo os dados do problema.

    Returns:
        dados: O dicionário de dados atualizado com a nova solução.
    """

    # Encontra o PA ativo com menos clientes
    PAs_ativos = dados['possiveis_coord_PA']
    num_PAs_ativos = len(PAs_ativos)
    clientes_ativos_por_PA = dados['cliente_por_PA'].sum(axis=0)[:num_PAs_ativos]
    PA_menos_clientes = np.argmin(clientes_ativos_por_PA)

    # Desativa o PA com menos clientes
    PAs_ativos = np.delete(PAs_ativos, PA_menos_clientes, axis=0)
    dados['possiveis_coord_PA'] = PAs_ativos

    # Obtém os clientes do PA desativado
    clientes_desalocados = np.where(dados['cliente_por_PA'][:, PA_menos_clientes] == 1)[0]
    # Remove os clientes do PA
    dados['cliente_por_PA'][:, PA_menos_clientes] = 0
    dados = realoca_clientes(dados, clientes_desalocados)


    # Atualiza a matriz de distâncias (considerando apenas PAs ativos)
    dados['dist_cliente_PA'] = calcular_distancias_cliente_PA(dados['possiveis_coord_PA'], dados['cliente_por_PA'])
    dados['possiveis_coord_PA'] = PAs_ativos

    print(f"{r3(dados)} | {r4(dados)} |{r5(dados)} |{r6(dados)} |{r7(dados, 1)} |{r8(dados)} ")
    return dados


def k2(dados):
    """
    Estrutura de vizinhança que seleciona uma região aleatória do grid (50x50),
    desabilita o PA ativo com menos clientes conectados na região e tenta
    redistribuir seus clientes para outros PAs habilitados, respeitando
    os limites de capacidade e distância.

    Args:
        dados: Um dicionário contendo os dados do problema.

    Returns:
        dados: O dicionário de dados atualizado com a nova solução.
    """

    # Define o tamanho da região
    tamanho_regiao = 50

    # Encontra as coordenadas da região aleatória
    x_inicio = np.random.randint(0, dados['sizex'][1] - tamanho_regiao + 1)
    y_inicio = np.random.randint(0, dados['sizey'][1] - tamanho_regiao + 1)
    x_fim = x_inicio + tamanho_regiao
    y_fim = y_inicio + tamanho_regiao

    # Encontra os PAs ativos dentro da região
    PAs_ativos = dados['possiveis_coord_PA']
    PAs_na_regiao = np.where(
        ((PAs_ativos[:, 0] >= x_inicio) & (PAs_ativos[:, 0] < x_fim)) &
        ((PAs_ativos[:, 1] >= y_inicio) & (PAs_ativos[:, 1] < y_fim))
    )[0]

    # Verifica se há PAs ativos na região
    if len(PAs_na_regiao) > 0:
        # Encontra o PA ativo com menos clientes na região
        clientes_por_PA_na_regiao = dados['cliente_por_PA'][:, PAs_na_regiao]
        clientes_ativos_por_PA = clientes_por_PA_na_regiao.sum(axis=0)
        PA_menos_clientes = np.argmin(clientes_ativos_por_PA)

        # Desativa o PA com menos clientes
        PAs_ativos = np.delete(PAs_ativos, PA_menos_clientes, axis=0)
        dados['possiveis_coord_PA'] = PAs_ativos

        # Obtém os clientes do PA desativado
        clientes_desalocados = np.where(dados['cliente_por_PA'][:, PA_menos_clientes] == 1)[0]

        # Remove os clientes do PA
        dados['cliente_por_PA'][:, PA_menos_clientes] = 0

        # Tenta realocar os clientes desalocados
        for cliente in clientes_desalocados:
            # Remove a conexão do cliente com o PA desativado
            dados['cliente_por_PA'][cliente, PA_menos_clientes] = 0
            # Calcula distâncias apenas para PAs ativos
            distancias = np.linalg.norm(dados['coord_clientes'][cliente] - dados['possiveis_coord_PA'], axis=1)

            # Encontra PAs ativos dentro do limite de sinal
            PAs_ativos_alcance = PAs_ativos[np.where(distancias <= dados['limite_sinal_PA'])[0]]

            # Tenta conectar ao PA com capacidade disponível
            for i in range(len(PAs_ativos_alcance)):
                PA = PAs_ativos_alcance[i]
                consumo_atual_pa = np.sum(dados['cliente_por_PA'][:, i] * dados['cons_clientes'])
                if consumo_atual_pa + dados['cons_clientes'][cliente] <= dados['capacidade_PA']:
                    dados['cliente_por_PA'][cliente, i] = 1
                    break  # Conectou o cliente, passa para o próximo


        # Atualiza a matriz de distâncias (considerando apenas PAs ativos)
        dados['dist_cliente_PA'] = calcular_distancias_cliente_PA(dados['possiveis_coord_PA'], dados['cliente_por_PA'])
        dados['possiveis_coord_PA'] = PAs_ativos


    return dados

def k3(dados):
    """
    Estrutura de vizinhança que seleciona uma região do grid (50x50)
    e tenta redistribuir os clientes nos PAs ativos dentro e fora da região,
    priorizando as menores distâncias e respeitando a capacidade dos PAs.

    Args:
        dados: Um dicionário contendo os dados do problema.

    Returns:
        dados: O dicionário de dados atualizado com a nova solução.
    """

    # Define o tamanho da região
    tamanho_regiao = 50

    # Escolhe uma região aleatória do grid
    x_inicio = np.random.randint(0, dados['sizex'][1] - tamanho_regiao + 1)
    y_inicio = np.random.randint(0, dados['sizey'][1] - tamanho_regiao + 1)
    x_fim = x_inicio + tamanho_regiao
    y_fim = y_inicio + tamanho_regiao

    # Encontra todos os clientes dentro da região
    clientes_na_regiao = np.where(
        ((dados['coord_clientes'][:, 0] >= x_inicio) & (dados['coord_clientes'][:, 0] < x_fim)) &
        ((dados['coord_clientes'][:, 1] >= y_inicio) & (dados['coord_clientes'][:, 1] < y_fim))
    )[0]

    # Para cada cliente na região, tenta conectá-lo ao PA mais próximo com capacidade
    dados = realoca_clientes(dados, clientes_na_regiao)

    # Atualiza a matriz de distâncias (considerando apenas PAs ativos)
    dados['dist_cliente_PA'] = calcular_distancias_cliente_PA(
        dados['possiveis_coord_PA'], dados['cliente_por_PA']
    )
    return dados

def realoca_clientes(dados, clientes):
    dist_ord_clientes = calcular_dist_ord_cliente_PAs(dados['possiveis_coord_PA'])
    cliente_por_PA = dados['cliente_por_PA']
    for i, cliente in enumerate(clientes):
        # Limpa cliente que será realocado
        cliente_por_PA[i] = np.zeros(dados['n_max_PAs'])
        consumo_PAs = np.zeros(len(dados['possiveis_coord_PA']))

        # Tenta conectar ao PA mais próximo com capacidade disponível
        for PA in dist_ord_clientes[i]:
            idx_PA = int(PA[2])
            if client_is_able_to_connect(dados, i, cliente, PA[:2], consumo_PAs[idx_PA]):
                cliente_por_PA[i][idx_PA] = 1
                consumo_PAs[idx_PA] += dados['cons_clientes'][i]
            break
    
    dados['cliente_por_PA'] = cliente_por_PA
    return dados

def k4(dados):
    """
    Estrutura de vizinhança que habilita um PA em posição aleatória
    e redistribui todos os clientes, priorizando a redução de distância
    e respeitando os limites de capacidade dos PAs.

    Args:
        dados: Um dicionário contendo os dados do problema.

    Returns:
        dados: O dicionário de dados atualizado com a nova solução.
    """
    num_PAs_alocados = len(dados['possiveis_coord_PA'])
    PAs_alocados = dados['possiveis_coord_PA']
    coord_clientes = dados["coord_clientes"]
    num_clientes = len(coord_clientes)
    n_max_PAs = dados['n_max_PAs']
    # Verifica se existem PAs inativos para habilitar
    if num_PAs_alocados < dados['n_max_PAs']:
        # Escolhe um local para habilitar um PA

        # Define uma posição aleatória para o PA dentro do grid
        valid_x_values = np.arange(0, dados['sizex'][1] + 1, 5)
        valid_y_values = np.arange(0, dados['sizey'][1]+ 1, 5)
        new_x = np.random.choice(valid_x_values)
        new_y = np.random.choice(valid_y_values)

        nova_posicao = (new_x, new_y)
        PAs_alocados = np.vstack((PAs_alocados, nova_posicao))

        # Redistribui os clientes, priorizando a redução de distância
        new_cliente_por_PA = np.zeros((num_clientes, n_max_PAs)) #Nova matriz de numero de clientes
        PAs_ordenados = calcular_dist_ord_cliente_PAs(PAs_alocados)
        # Passo 2: Acessar as coordenadas ordenadas dos PAs
        consumo_PAs = np.zeros(len(PAs_alocados))


        for i, coord in enumerate(coord_clientes):
            for idx, pa in enumerate(PAs_ordenados[i]):
                pa_idx = int(PAs_ordenados[i][idx][2])
                if client_is_able_to_connect(dados, i, coord, pa[:2], consumo_PAs[pa_idx]):
                    new_cliente_por_PA[i, pa_idx] = 1 
                    consumo_PAs[pa_idx] += dados['cons_clientes'][i]
                    break

        dados["cliente_por_PA"] = new_cliente_por_PA
        dados["possiveis_coord_PA"] = PAs_alocados


    return dados

def calcular_dist_ord_cliente_PAs(coord_PAs):
    print()
    dist_matrix = np.load('dist_matrix.npy')
    num_clientes = int(dist_matrix.shape[2])
    pas_ativos = coord_PAs
    num_PAs = len(pas_ativos)
    coord_pas_ativos = pas_ativos // 5
    coord_pas_ativos = coord_pas_ativos.astype(int)
    PAs_ordenados_por_dist = np.zeros((num_clientes, num_PAs, 3))

    for i in range(num_clientes):
        grid_dist = dist_matrix[:, :, i]
        try:
            dist_PAs = grid_dist[coord_pas_ativos[:, 0], coord_pas_ativos[:, 1]]
        except Exception as e:
            print(f"coord_pas_ativos: {coord_pas_ativos}")
        indexes_ordenados = np.argsort(dist_PAs)
        PAs_ordenados_por_dist[i, :, :2] = pas_ativos[indexes_ordenados]
        PAs_ordenados_por_dist[i, :, 2] = indexes_ordenados
    return PAs_ordenados_por_dist

# # novas estruturas

# def calcular_distancia(x1, y1, x2, y2):
#   #Calcula a distância euclidiana entre dois pontos.
#   return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# def calcular_uso_PA(x):
#   num_PAs = len(x['possiveis_coord_PA'])
#   users_on_PA = np.sum(x['cliente_por_PA'], axis=0)
#   return users_on_PA[:num_PAs]


# def encontrar_pas_na_regiao(x, regiao_x, regiao_y):
#   """Encontra os índices dos PAs dentro de uma região do grid."""
#   pas_na_regiao = []
#   for PA_index in range(x['n_max_possivel_PAs']):
#     pa_x = x['possiveis_coord_PA'][PA_index, 0]
#     pa_y = x['possiveis_coord_PA'][PA_index, 1]
#     if regiao_x[0] <= pa_x < regiao_x[1] and regiao_y[0] <= pa_y < regiao_y[1]:
#       pas_na_regiao.append(PA_index)
#   return pas_na_regiao

# def client_is_able_to_connect(dados, i, coord, posicao_PA, consumo_atual_pa):
#     return np.linalg.norm(coord - posicao_PA) <= dados['limite_sinal_PA'] and \
#            np.sum(dados['cliente_por_PA'][i]) ==  0 and \
#            consumo_atual_pa + dados['cons_clientes'][i] <= dados['capacidade_PA']

# def PAs_mais_prox(idx_cliente, coord_PAs):
#     dist_matrix = np.load('dist_matrix.npy')
#     pas_ativos = coord_PAs
#     num_PAs = len(pas_ativos)
#     coord_pas_ativos = pas_ativos / 5
#     coord_pas_ativos = coord_pas_ativos.astype(int)
#     coordenadas_PAs_mais_prox = np.zeros((num_PAs, 2))

#   # Criar uma lista de tuplas (coord_PA, dist_PA_atual)
#     lista_coord_dist = []

#     for i, pa in enumerate(coord_pas_ativos):
#         dist_PA_atual = dist_matrix[pa[0], pa[1], idx_cliente]  # Corrigido para acesso correto
#         lista_coord_dist.append((coord_PAs[i], dist_PA_atual))

#     # Ordenar a lista com base na distância atual do PA
#     lista_coord_dist_ordenada = sorted(lista_coord_dist, key=lambda x: x[1])

#     # Extrair as coordenadas ordenadas
#     coordenadas_PAs_mais_prox = np.array([coord for coord, _ in lista_coord_dist_ordenada])

#     return coordenadas_PAs_mais_prox

# def calcula_consumo_PAs(x):
#   clientes_por_PA = x['cliente_por_PA']
#   cons_clientes = x['cons_clientes']

#   return np.dot(cons_clientes.T, clientes_por_PA)

# def k11(x):
#   # Desativa o PA com menor uso e ativa um aleatório, redistribuindo clientes. 
#   # Clientes que não puderem ser atendidos por outro PA ficarão sem serviço.

#   # Calcula o uso de cada PA
#   uso_PAs = calcular_uso_PA(x)

#   # Encontra o PA com menor uso que está ativo
#   PA_menor_uso = np.argmin(uso_PAs)

#   # Desativa o PA com menor uso
#   coord_PAs = x['possiveis_coord_PA']
#   remocao_pa = np.delete(coord_PAs, PA_menor_uso, axis=0)
#   x['possiveis_coord_PA'] = remocao_pa

#   # Libera os clientes do PA desativado
#   idx_clientes_liberados = np.where(x['cliente_por_PA'][:, PA_menor_uso] == 1)[0]
#   x['cliente_por_PA'][idx_clientes_liberados, PA_menor_uso] = 0
#   coord_clientes = x['coord_clientes']

#   #Encontra o array de PAs mais proximos ordenado
#   print(f'index de clientes liberados: {idx_clientes_liberados}')
#   arr_consumo_pa = calcula_consumo_PAs(x)
#   for idx_cliente in idx_clientes_liberados:
#     print(f'coord cliente {idx_cliente}: {coord_clientes[idx_cliente]}')
#     possiveis_PAs_p_conectar = PAs_mais_prox(idx_cliente, x['possiveis_coord_PA'])
#     for pa_index, pa in enumerate(possiveis_PAs_p_conectar):
#       consumo_pa = arr_consumo_pa[pa_index]
#       if client_is_able_to_connect(x, idx_cliente, coord_clientes[idx_cliente], pa, consumo_pa):
#         x['cliente_por_PA'][idx_cliente, pa_index] = 1
#         print(f'alocou cliente {idx_cliente}') 
#       break
  
#   print(f"possiveis coord pa: {x['possiveis_coord_PA']}")
#   return x

# def k12(x):
#   # Encontra os 5 clientes mais distantes de seus PAs (apenas 
#   # clientes com PA atribuído) e tenta redistribuí-los.

#   distancias = np.full(len(x['coord_clientes']), np.inf)  # Inicializa com infinito para clientes sem PA
#   clientes_com_PA = np.where(np.sum(x['cliente_por_PA'], axis=1) > 0)[0]

#   # Calcula a distância apenas para clientes com PA atribuído
#   for cliente_index in clientes_com_PA:
#     PA_atual = np.where(x['cliente_por_PA'][cliente_index, :] == 1)[0][0] 
#     distancias[cliente_index] = calcular_distancia(
#         x['coord_clientes'][cliente_index, 0],
#         x['coord_clientes'][cliente_index, 1],
#         x['possiveis_coord_PA'][PA_atual, 0],
#         x['possiveis_coord_PA'][PA_atual, 1],
#     )

#   # Encontra os 5 clientes mais distantes que TEM PA
#   clientes_mais_distantes = np.argsort(distancias)[-5:]
#   clientes_mais_distantes = np.intersect1d(clientes_mais_distantes, clientes_com_PA)

#   # linhas para validação de resultados
#   # print(clientes_mais_distantes)
#   # for cliente_index in clientes_mais_distantes:
#   #   PA_atual = np.where(x['cliente_por_PA'][cliente_index, :] == 1)[0][0] 
#   #   distancias[cliente_index] = calcular_distancia(
#   #       x['coord_clientes'][cliente_index, 0],
#   #       x['coord_clientes'][cliente_index, 1],
#   #       x['possiveis_coord_PA'][PA_atual, 0],
#   #       x['possiveis_coord_PA'][PA_atual, 1],
#   #   )
#   #   print(distancias[cliente_index])

#   # Tenta redistribuir os clientes mais distantes
#   for cliente_index in clientes_mais_distantes:
#     # Calcula o consumo do cliente
#     cliente_consumo = x['cons_clientes'][cliente_index]

#     # Desconecta do PA atual
#     PA_atual = np.where(x['cliente_por_PA'][cliente_index, :] == 1)[0][0]
#     x['cliente_por_PA'][cliente_index, PA_atual] = 0

#     # Tenta conectar a outro PA disponível
#     PAs_disponiveis = np.where(x['uso_PAs'] == 1)[0]
#     random.shuffle(PAs_disponiveis) 

#     for PA_candidato in PAs_disponiveis:
#       if calcular_uso_PA(x, PA_candidato) + cliente_consumo <= x['capacidade_PA']:
#         distancia_candidato = calcular_distancia(
#             x['coord_clientes'][cliente_index, 0],
#             x['coord_clientes'][cliente_index, 1],
#             x['possiveis_coord_PA'][PA_candidato, 0],
#             x['possiveis_coord_PA'][PA_candidato, 1],
#         )
#         if distancia_candidato <= x['limite_sinal_PA']:
#           x['cliente_por_PA'][cliente_index, PA_candidato] = 1
#           break
#     else:
#       # Se não encontrar um PA disponível, reconecta ao PA original
#       x['cliente_por_PA'][cliente_index, PA_atual] = 1

#   # linhas para validação de resultados
#   # for cliente_index in clientes_mais_distantes:
#   #   PA_atual = np.where(x['cliente_por_PA'][cliente_index, :] == 1)[0][0] 
#   #   distancias[cliente_index] = calcular_distancia(
#   #       x['coord_clientes'][cliente_index, 0],
#   #       x['coord_clientes'][cliente_index, 1],
#   #       x['possiveis_coord_PA'][PA_atual, 0],
#   #       x['possiveis_coord_PA'][PA_atual, 1],
#   #   )
#   #   print(distancias[cliente_index])


#   return x

# def k13(x):
#   # Desabilita o PA com menor utilização e redistribui seus clientes 
#   # para outros PAs habilitados. Clientes que não puderem ser 
#   # redistribuídos serão desconectados.

#   # Calcula o uso de cada PA
#   uso_PAs = np.array([calcular_uso_PA(x, i) if x['uso_PAs'][i] == 1 else np.inf for i in range(len(x['uso_PAs']))])

#   # Encontra o PA com menor uso que está ativo
#   PA_menor_uso = np.argmin(uso_PAs)

#   # Verifica se existe mais de um PA ativo
#   if np.count_nonzero(x['uso_PAs']) <= 1:
#     print("Apenas um ou nenhum PA ativo. Impossível redistribuir.")
#     return x

#   # Desativa o PA com menor uso
#   x['uso_PAs'][PA_menor_uso] = 0

#   # Obtém os clientes do PA que será desativado
#   clientes_para_redistribuir = np.where(x['cliente_por_PA'][:, PA_menor_uso] == 1)[0]

#   # Tenta redistribuir os clientes
#   for cliente_index in clientes_para_redistribuir:
#     cliente_consumo = x['cons_clientes'][cliente_index]

#     # Desconecta do PA atual
#     x['cliente_por_PA'][cliente_index, PA_menor_uso] = 0

#     # Tenta conectar a outro PA disponível
#     PAs_disponiveis = np.where(x['uso_PAs'] == 1)[0]
#     random.shuffle(PAs_disponiveis)

#     for PA_candidato in PAs_disponiveis:
#       if calcular_uso_PA(x, PA_candidato) + cliente_consumo <= x['capacidade_PA']:
#         distancia_candidato = calcular_distancia(
#             x['coord_clientes'][cliente_index, 0],
#             x['coord_clientes'][cliente_index, 1],
#             x['possiveis_coord_PA'][PA_candidato, 0],
#             x['possiveis_coord_PA'][PA_candidato, 1],
#         )
#         if distancia_candidato <= x['limite_sinal_PA']:
#           # Conecta ao novo PA
#           x['cliente_por_PA'][cliente_index, PA_candidato] = 1
#           break  # Sai do loop se conectou com sucesso
#     else:
#       # Não encontrou nenhum PA disponível, cliente permanece desconectado
#       pass  # Não precisa fazer nada aqui, pois o cliente já foi desconectado

#   return x

# def k14(x):

#   # Seleciona uma região aleatória do grid, encontra o PA com 
#   # menos clientes conectados nessa região e tenta redistribuir 
#   # esses clientes para outros PAs habilitados em qualquer 
#   # lugar do grid.


#   # Define uma região aleatória de 50x50 com x e y sempre positivos
#   regiao_x = (random.randint(0, max(0, x['sizex'][1] - 50)), random.randint(0, max(0, x['sizex'][1] - 50)) + 50)
#   regiao_y = (random.randint(0, max(0, x['sizey'][1] - 50)), random.randint(0, max(0, x['sizey'][1] - 50)) + 50)

#   # Encontra os PAs ativos dentro da região
#   pas_na_regiao = encontrar_pas_na_regiao(x, regiao_x, regiao_y)
#   pas_ativos_na_regiao = np.intersect1d(pas_na_regiao, np.where(x['uso_PAs'] == 1)[0])

#   # Se não houver PAs ativos na região, retorna
#   if len(pas_ativos_na_regiao) == 0:
#     #print("Nenhum PA ativo encontrado na região selecionada.")
#     return x

#   # Encontra o PA com menos clientes conectados na região
#   num_clientes_por_pa = np.sum(x['cliente_por_PA'][:, pas_ativos_na_regiao], axis=0)
#   PA_menor_uso_na_regiao = pas_ativos_na_regiao[np.argmin(num_clientes_por_pa)]

#   # Desativa o PA com menor uso na região
#   x['uso_PAs'][PA_menor_uso_na_regiao] = 0

#   # Tenta redistribuir os clientes do PA desabilitado
#   clientes_para_redistribuir = np.where(x['cliente_por_PA'][:, PA_menor_uso_na_regiao] == 1)[0]
#   for cliente_index in clientes_para_redistribuir:
#     cliente_consumo = x['cons_clientes'][cliente_index]

#     # Tenta conectar a outro PA disponível em qualquer região
#     PAs_disponiveis = np.where(x['uso_PAs'] == 1)[0]
#     random.shuffle(PAs_disponiveis)

#     for PA_candidato in PAs_disponiveis:
#       if calcular_uso_PA(x, PA_candidato) + cliente_consumo <= x['capacidade_PA']:
#         distancia_candidato = calcular_distancia(
#             x['coord_clientes'][cliente_index, 0],
#             x['coord_clientes'][cliente_index, 1],
#             x['possiveis_coord_PA'][PA_candidato, 0],
#             x['possiveis_coord_PA'][PA_candidato, 1],
#         )
#         if distancia_candidato <= x['limite_sinal_PA']:
#           # Conecta ao novo PA
#           x['cliente_por_PA'][cliente_index, PA_candidato] = 1
#           break
#     else:
#       # Cliente permanece desconectado se nenhum PA estiver disponível
#       pass

#   return x
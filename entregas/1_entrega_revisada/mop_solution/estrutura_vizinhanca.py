import numpy as np
from restricoes import calcular_distancias_cliente_PA, sum_restr_impossiveis, r3, r4, r5, r6, r7, r8
from solution import client_is_able_to_connect

"""
Novo código para estruturas de vizinhança
Ainda sendo testado
"""

def k1(dados, log = None):
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
    # Remove os clientes do PA
    dados['possiveis_coord_PA'] = PAs_ativos
    # Obtém os clientes do PA desativado primeiro
    clientes_desalocados = np.where(dados['cliente_por_PA'][:, PA_menos_clientes] == 1)[0]
    #Apaga o PA da relação clientes por PA
    dados['cliente_por_PA'] = np.delete(dados['cliente_por_PA'], PA_menos_clientes, axis=1)
    coluna_zeros = np.zeros((dados['cliente_por_PA'].shape[0], 1))

    dados['cliente_por_PA'] = np.hstack((dados['cliente_por_PA'], coluna_zeros))


    dados = realoca_clientes(dados, clientes_desalocados)
    if log is not None:
        print(f"{r3(dados)} | {r4(dados)} | {r5(dados)} | {r6(dados)} | {r7(dados)} | {r8(dados)}")

    return dados

def k2(dados, log = None):
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
    tamanho_regiao = 100

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

        # Obtém os clientes do PA desativado
        clientes_desalocados = np.where(dados['cliente_por_PA'][:, PA_menos_clientes] == 1)[0]

        # Desativa o PA com menos clientes
        PAs_ativos = np.delete(PAs_ativos, PA_menos_clientes, axis=0)
        dados['possiveis_coord_PA'] = PAs_ativos
        dados['cliente_por_PA'] = np.delete(dados['cliente_por_PA'], PA_menos_clientes, axis=1)

        #Adiciona coluna de zeros no fim do array
        coluna_zeros = np.zeros((dados['cliente_por_PA'].shape[0], 1))
        dados['cliente_por_PA'] = np.hstack((dados['cliente_por_PA'], coluna_zeros))

        dados = realoca_clientes(dados, clientes_desalocados)
        if log is not None:
            print(f"{r3(dados)} | {r4(dados)} | {r5(dados)} | {r6(dados)} | {r7(dados)} | {r8(dados)}")

    return dados

def k3(dados, log = None):
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
    if log is not None:
        print(f"{r3(dados)} | {r4(dados)} | {r5(dados)} | {r6(dados)} | {r7(dados)} | {r8(dados)}")

    return dados

def k4(dados, log = None):
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
        new_cliente_por_PA = np.zeros((num_clientes, n_max_PAs)) #Nova matriz de numero de clientes
        dados["cliente_por_PA"] = new_cliente_por_PA
        dados["possiveis_coord_PA"] = PAs_alocados

        # Redistribui todos os clientes, priorizando a redução de distância
        clientes_para_alocar = array = np.arange(495)
        dados = realoca_clientes(dados, clientes_para_alocar)
        if log is not None:
            print(f"{r3(dados)} | {r4(dados)} | {r5(dados)} | {r6(dados)} | {r7(dados)} | {r8(dados)}")

    return dados

def k5(dados, log = None):
    """
    Estrutura de vizinhança que "move" um PA ativo para um ponto 
    próximo 
    Args:
        dados: Um dicionário contendo os dados do problema.

    Returns:
        dados: O dicionário de dados atualizado com a nova solução.
    """
    bkp_dados = dados

    PAs_ativos = dados['possiveis_coord_PA']

    # Encontra um PA ativo aleatorio e o desativa
    idx_PA_aleatorio = np.random.choice(PAs_ativos.shape[0])
    backup_PA = PAs_ativos[idx_PA_aleatorio]
    PAs_ativos = np.delete(PAs_ativos, idx_PA_aleatorio, axis=0)
    dados['possiveis_coord_PA'] = PAs_ativos

    # Obtém os clientes do PA desativado e que nao estavam conectados antes
    clientes_desalocados = np.where(dados['cliente_por_PA'][:, idx_PA_aleatorio] == 1)[0]
    clientes_desconectados = np.where(np.sum(dados['cliente_por_PA'], axis=1) == 0)[0]
    clientes_sem_PA = np.union1d(clientes_desalocados, clientes_desconectados)


    #Apaga o PA da relação clientes por PA e adiciona uma coluna para nao quebrar cliente_por_PA
    dados['cliente_por_PA'] = np.delete(dados['cliente_por_PA'], idx_PA_aleatorio, axis=1)
    coluna_zeros = np.zeros((dados['cliente_por_PA'].shape[0], 1))
    dados['cliente_por_PA'] = np.hstack((dados['cliente_por_PA'], coluna_zeros))

    #Adiciona um novo PA para a vizinhança do PA removido no fim do array
    PA_na_vizinhanca = deslocar_coordenada(backup_PA, PAs_ativos)
    PAs_ativos = np.append(PAs_ativos, [PA_na_vizinhanca], axis=0)

    coluna_PA_novo = dados['cliente_por_PA'][:, len(PAs_ativos) - 1]
    soma_coluna = np.sum(coluna_PA_novo)
    if soma_coluna > 0:
        linhas_como_tuplas = {tuple(linha) for linha in dados['cliente_por_PA']}
        linhas_duplicadas = len(linhas_como_tuplas) < len(dados['cliente_por_PA'])
        # if log is not None:
        #     print(f"Coluna do PA novo {PA_na_vizinhanca} (idx {len(PAs_ativos) - 1}) nao esta zerada. Linhas dupicadas: {linhas_duplicadas}. Retornando solução recebida")
        return bkp_dados
    dados['possiveis_coord_PA'] = PAs_ativos
    #Pega ID do novo PA, que é o ultimo da fila, e prioriza a conexao dos desalocados nele
    idx_prioridade = len(PAs_ativos) - 1

    dados = realoca_clientes(dados, clientes_sem_PA, idx_prioridade)
    if log is not None:
        print(f"{r3(dados)} | {r4(dados)} | {r5(dados)} | {r6(dados)} | {r7(dados)} | {r8(dados)}")
    return dados

def k6(dados, log = None):
    """
    Estrutura de vizinhança que "junta" dois PAs em um, no meio do caminho entre eles
    Args:
        dados: Um dicionário contendo os dados do problema.

    Returns:
        dados: O dicionário de dados atualizado com a nova solução.
    """
    bkp_dados = dados
    PAs_ativos_bkp = dados['possiveis_coord_PA']
    PAs_ativos = dados['possiveis_coord_PA']

    # Encontra dois PAs ativos aleatorios e desativa ambos
    idx_PA_aleatorio_1 = np.random.choice(PAs_ativos.shape[0], replace=False)
    backup_PA_1 = PAs_ativos[idx_PA_aleatorio_1]
    idx_PA_aleatorio_2 = np.random.choice(np.delete(np.arange(PAs_ativos.shape[0]), idx_PA_aleatorio_1), replace=False)
    backup_PA_2 = PAs_ativos[idx_PA_aleatorio_2]
    idxs_PAs_para_remover = [idx_PA_aleatorio_1, idx_PA_aleatorio_2]
    PAs_ativos = np.delete(PAs_ativos, idxs_PAs_para_remover, axis=0)
    dados['possiveis_coord_PA'] = PAs_ativos

    # Obtém os clientes dos PAs desativados e que nao estavam conectados antes
    clientes_desalocados_PA_1 = np.where(dados['cliente_por_PA'][:, idx_PA_aleatorio_1] == 1)[0]
    clientes_desalocados_PA_2 = np.where(dados['cliente_por_PA'][:, idx_PA_aleatorio_2] == 1)[0]
    clientes_desalocados = np.union1d(clientes_desalocados_PA_1, clientes_desalocados_PA_2)
    clientes_desconectados = np.where(np.sum(dados['cliente_por_PA'], axis=1) == 0)[0]
    clientes_sem_PA = np.union1d(clientes_desalocados, clientes_desconectados)

    #Apaga os PAs da relação clientes por PA e adiciona duas coluna para nao quebrar cliente_por_PA

    dados['cliente_por_PA'] = np.delete(dados['cliente_por_PA'], idxs_PAs_para_remover, axis=1)
    # if log is not None:
    #     print(f"Largura da matriz após os dois PAs {idxs_PAs_para_remover} serem removidos: {dados['cliente_por_PA'].shape[1]}")
    coluna_zeros = np.zeros((dados['cliente_por_PA'].shape[0], 1))
    dados['cliente_por_PA'] = np.hstack((dados['cliente_por_PA'], coluna_zeros, coluna_zeros))
    # if log is not None:
    #     print(f"Largura da matriz após as adições das colunas vazias: {dados['cliente_por_PA'].shape[1]}")

    #Adiciona um novo PA para a vizinhança do PA removido no fim do array
    PA_no_meio = coordenada_media(backup_PA_1, backup_PA_2)
    PAs_ativos = np.append(PAs_ativos, [PA_no_meio], axis=0)

    coluna_PA_novo = dados['cliente_por_PA'][:, len(PAs_ativos) - 1]
    soma_coluna = np.sum(coluna_PA_novo)
    if soma_coluna > 0:
        linhas_como_tuplas = {tuple(linha) for linha in dados['cliente_por_PA']}
        linhas_duplicadas = len(linhas_como_tuplas) < len(dados['cliente_por_PA'])
        # if log is not None:
        #     print(f"Coluna do PA novo {PA_no_meio} (idx {len(PAs_ativos) - 1}) nao esta zerada. Linhas dupicadas: {linhas_duplicadas}. Retornando solução recebida")
        return bkp_dados
    dados['possiveis_coord_PA'] = PAs_ativos
    #Pega ID do novo PA, que é o ultimo da fila, e prioriza a conexao dos desalocados nele
    idx_prioridade = len(PAs_ativos) - 1

    dados = realoca_clientes(dados, clientes_sem_PA, idx_prioridade)
    if log is not None:
    #     print(f"PAs ativos antes das mudanças: {PAs_ativos_bkp}")
    #     print(f"PAs escolhidos: {backup_PA_1} e {backup_PA_2}")
    #     print(f"PAs do meio: {PA_no_meio}")
    #     print(f"Os PAs ativos agora são: {PAs_ativos}")
    #     print(f"clientes a serem alocados: {clientes_sem_PA}")
    #     print(f"PA prioritario: {PAs_ativos[len(PAs_ativos) - 1]} (idx {len(PAs_ativos) - 1})")
        print(f"{r3(dados)} | {r4(dados)} | {r5(dados)} | {r6(dados)} | {r7(dados)} | {r8(dados)}")
    return dados

def k7(dados, log = None):
    """
    Estrutura de vizinhança que adiciona um PA no meio do caminho entre dois PAs aleatórios.
    Desaloca os clientes de ambos os PAs e os realoca, priorizando o novo PA criado
    (Só acontece se ainda puder alocar PAs)
    Args:
        dados: Um dicionário contendo os dados do problema.

    Returns:
        dados: O dicionário de dados atualizado com a nova solução.
    """
    n_max_PAs = dados['n_max_PAs']
    PAs_ativos = dados['possiveis_coord_PA']
    bkp_dados = dados
    if (len(PAs_ativos) >= n_max_PAs):
        return dados

    # Encontra dois PAs aleatórios
    idx_PA_aleatorio_1 = np.random.choice(PAs_ativos.shape[0], replace=False)
    coord_PA_1 = PAs_ativos[idx_PA_aleatorio_1]
    idx_PA_aleatorio_2 = np.random.choice(np.delete(np.arange(PAs_ativos.shape[0]), idx_PA_aleatorio_1), replace=False)    
    coord_PA_2 = PAs_ativos[idx_PA_aleatorio_2]
    idxs_PAs_para_limpar_clientes = [idx_PA_aleatorio_1, idx_PA_aleatorio_2]

    # Obtém os clientes dos PAs desativados e que nao estavam conectados antes
    clientes_desalocados_PA_1 = np.where(dados['cliente_por_PA'][:, idx_PA_aleatorio_1] == 1)[0]
    clientes_desalocados_PA_2 = np.where(dados['cliente_por_PA'][:, idx_PA_aleatorio_2] == 1)[0]
    clientes_desalocados = np.union1d(clientes_desalocados_PA_1, clientes_desalocados_PA_2)
    clientes_desconectados = np.where(np.sum(dados['cliente_por_PA'], axis=1) == 0)[0]
    clientes_sem_PA = np.union1d(clientes_desalocados, clientes_desconectados)

    #Limpa os PAs de todos os clientes na relação clientes por PA
    dados['cliente_por_PA'][:, idxs_PAs_para_limpar_clientes] = 0
    # if log is not None:
    #     print(f"Largura da matriz após os dois PAs serem removidos: {dados['cliente_por_PA'].shape[1]}")

    #Adiciona um novo PA para a vizinhança do PA removido no fim do array
    PA_no_meio = coordenada_media(coord_PA_1, coord_PA_2)
    PAs_ativos = np.append(PAs_ativos, [PA_no_meio], axis=0)

    coluna_PA_novo = dados['cliente_por_PA'][:, len(PAs_ativos) - 1]
    soma_coluna = np.sum(coluna_PA_novo)
    if soma_coluna > 0:
        linhas_como_tuplas = {tuple(linha) for linha in dados['cliente_por_PA']}
        linhas_duplicadas = len(linhas_como_tuplas) < len(dados['cliente_por_PA'])
        # if log is not None:
        #     print(f"Coluna do PA novo {PA_no_meio} (idx {len(PAs_ativos) - 1}) nao esta zerada. Linhas dupicadas: {linhas_duplicadas}. Retornando solução recebida")
        return bkp_dados
    dados['possiveis_coord_PA'] = PAs_ativos
    #Pega ID do novo PA, que é o ultimo da fila, e prioriza a conexao dos desalocados nele
    idx_prioridade = len(PAs_ativos) - 1

    dados = realoca_clientes(dados, clientes_sem_PA, idx_prioridade)
    if log is not None:
        # print(f"PAs escolhidos: {coord_PA_1} e {coord_PA_2}")
        # print(f"PAs do meio: {PA_no_meio}")
        # print(f"Os PAs ativos agora são: {PAs_ativos}")
        # print(f"clientes a serem alocados: {clientes_sem_PA}")
        # print(f"PA prioritario: {PAs_ativos[len(PAs_ativos) - 1]} (idx {len(PAs_ativos) - 1})")
        print(f"{r3(dados)} | {r4(dados)} | {r5(dados)} | {r6(dados)} | {r7(dados)} | {r8(dados)}")
    return dados

def k8(dados, log = None):
    for i in range(3):
        dados = k5(dados)
    return dados

def k9(dados, log = None):
    for i in range(5):
        dados = k5(dados)
    return dados

# Funções utilizadas pelas estruturas de vizinhança
def realoca_clientes(dados, clientes_indexes, pa_priorizado = None):
    coords_PAs = dados['possiveis_coord_PA']
    cons_clientes = dados['cons_clientes']

    PAs_ordenados_por_prioridade = calcular_dist_ord_cliente_PAs(coords_PAs) # ordena por distancia. Funciona bem tanto para f1 quanto f2
    #Caso haja algum PA prioritário, coloca ele na frente
    if pa_priorizado is not None:
        PAs_ordenados_por_prioridade = priorizar_PA(PAs_ordenados_por_prioridade, pa_priorizado)

    cliente_por_PA = dados['cliente_por_PA']
    clientes_reconectados = 0

    for i, idx_cliente in enumerate(clientes_indexes):
        coord_cliente = dados['coord_clientes'][idx_cliente]
        cliente_por_PA[idx_cliente] = np.zeros(dados['n_max_PAs'])
        consumo_PAs = np.zeros(len(coords_PAs))

        # Tenta conectar ao PA mais próximo com capacidade disponível
        for PA in PAs_ordenados_por_prioridade[idx_cliente]:
            # Encontra o consumo atual do PA pelo index normalizado
            idx_PA = int(PA[2])
            consumo_PAs[idx_PA] = np.sum(cliente_por_PA[:,idx_PA]*cons_clientes)
            #Se for possivel conectar, faz a conexao
            if client_is_able_to_connect(dados, idx_cliente, coord_cliente, PA[:2], consumo_PAs[idx_PA]):
                clientes_reconectados = clientes_reconectados + 1 # Atualiza od dados para registrar a conexao
                dados["cliente_por_PA"][idx_cliente][idx_PA] = 1
                consumo_PAs[idx_PA] += dados['cons_clientes'][i]
                break

    somas = np.sum(cliente_por_PA, axis=1)
    # Verifique se todas as somas são iguais a 1
    todas_iguais_a_um = np.all((somas == 0.0) | (somas == 1.0))
    if (not todas_iguais_a_um):
        print("Tem cliente em dois PAs")
    dados['cliente_por_PA'] = cliente_por_PA
    return dados

def calcular_dist_ord_cliente_PAs(coord_PAs):
    dist_matrix = np.load('dist_matrix.npy')
    num_clientes = int(dist_matrix.shape[2])
    #Obtém, a partir da coord do PA, as coordenadas do array de distancia dele para todos os clientes
    pas_ativos = coord_PAs
    num_PAs = len(pas_ativos)
    coord_pas_ativos = pas_ativos // 5
    coord_pas_ativos = coord_pas_ativos.astype(int)

    PAs_ordenados_por_dist = np.zeros((num_clientes, num_PAs, 3)) #Coordenadas do array de distancia dele para todos os clientes

    for i in range(num_clientes):
        grid_dist = dist_matrix[:, :, i] # Obtem todas as distancias do grid para o cliente i
        dist_PAs = grid_dist[coord_pas_ativos[:, 0], coord_pas_ativos[:, 1]] # Obtem todas as distancias dos PAs ativos para o cliente i
        indexes_ordenados = np.argsort(dist_PAs) # Ordena por distancias e obtém os indexes normalizados

        PAs_ordenados_por_dist[i, :, :2] = pas_ativos[indexes_ordenados] #Seta as coords dos PAs
        PAs_ordenados_por_dist[i, :, 2] = indexes_ordenados #Seta os indexes ordenados
    return PAs_ordenados_por_dist

def calcular_popularidade_ord_cliente_PAs(coord_PAs):
    dist_matrix = np.load('dist_matrix.npy')
    num_clientes = int(dist_matrix.shape[2])
    #Obtém, a partir da coord do PA, as coordenadas do array de distancia dele para todos os clientes
    pas_ativos = coord_PAs
    num_PAs = pas_ativos.shape[0]
    coord_pas_ativos = pas_ativos // 5
    coord_pas_ativos = coord_pas_ativos.astype(int)
    PAs_com_idx = np.zeros((num_PAs, 3))

    #Obtem a quantidade de pessoas no range de cada PA
    contagem_menores_que_85 = np.zeros(num_PAs, dtype=int)    
    sorted_indices = np.zeros(num_PAs, dtype=int)
    PAs_com_indexes =  np.zeros((num_PAs, 2))

    for idx, cp in enumerate(coord_pas_ativos):
        # Acessar o array correspondente em dist_matrix
        distancias = dist_matrix[cp[0], cp[1]]
        # Contar quantos elementos são menores que 85
        contagem_menores_que_85[idx] = np.sum(distancias < 85)

    sorted_indices = np.argsort(-contagem_menores_que_85)
    PAs_com_idx[:,2] = sorted_indices
    for idx, pos_array in enumerate(sorted_indices):
        PAs_com_idx[idx][0] = pas_ativos[pos_array][0]
        PAs_com_idx[idx][1] = pas_ativos[pos_array][1]

    PAs_ordenados_por_popularidade = np.zeros((num_clientes, num_PAs, 3)) #Coordenadas do array de distancia dele para todos os clientes
    PAs_ordenados_por_popularidade[:] = np.broadcast_to(PAs_com_idx, (num_clientes, num_PAs, 3))
    return PAs_ordenados_por_popularidade

def adicionar_indices(coord_PAs):
    dist_matrix = np.load('dist_matrix.npy')
    num_clientes = int(dist_matrix.shape[2])
    num_PAs = coord_PAs.shape[0]
    # Obtém o número de linhas (Y) da matriz
    Y = coord_PAs.shape[0]
    
    # Cria um array de índices
    indices = np.arange(Y).reshape(Y, 1)
    
    # Concatena a matriz original com o array de índices
    matriz_com_indices = np.hstack((coord_PAs, indices))

    #Coloca essa ordenação para todos os clientes
    PAs_ordenados_por_popularidade = np.zeros((num_clientes, num_PAs, 3)) #Coordenadas do array de distancia dele para todos os clientes
    PAs_ordenados_por_popularidade[:] = np.broadcast_to(matriz_com_indices, (num_clientes, num_PAs, 3))
    return PAs_ordenados_por_popularidade


def priorizar_PA(coord_PAs_idxados, idx_PA):
    # Crie uma cópia da matriz para não modificar a original
    matriz_ordenada = np.empty_like(coord_PAs_idxados)
    # Iterar sobre cada um dos 495 clientes
    for i in range(coord_PAs_idxados.shape[0]):
        # Encontre o índice da linha que contém o valor prioritário no idx normalizado
        indices_prioritarios = np.where(coord_PAs_idxados[i][:, 2] == idx_PA)[0]
        
        if len(indices_prioritarios) == 0:
            matriz_ordenada[i] = coord_PAs_idxados[i]  # Se o idx normalizado não for encontrado, mantenha a matriz original
        else:
            # Extrai a linha prioritária
            linha_prioritaria = coord_PAs_idxados[i][indices_prioritarios[0]]
            # Remove a linha prioritária da matriz
            matriz_sem_prioritaria = np.delete(coord_PAs_idxados[i], indices_prioritarios[0], axis=0)
            # Adiciona a linha prioritária no início da matriz
            matriz_ordenada[i] = np.vstack([linha_prioritaria, matriz_sem_prioritaria])
    
    return matriz_ordenada

def deslocar_coordenada(coordenada, PAs_ativos, max_tentativas=100):
    deslocamentos = np.array([-10, -5, 5, 10])
    tentativas = 0
    
    while tentativas < max_tentativas:
        deslocamento_x = np.random.choice(deslocamentos)
        deslocamento_y = np.random.choice(deslocamentos)
        
        # Calcular a nova coordenada
        nova_coordenada = coordenada + np.array([deslocamento_x, deslocamento_y])
        
        # Verificar se nova_coordenada já existe em PAs_ativos
        if not any((nova_coordenada == PA).all() for PA in PAs_ativos):
            # Se não existir, retornar a coordenada ajustada dentro dos limites
            nova_coordenada = np.maximum(0, np.minimum(nova_coordenada, 400))
            return nova_coordenada
        
        tentativas += 1

def coordenada_media(c1, c2):
    # Calcular a coordenada do meio
    meio = (np.array(c1) + np.array(c2)) / 2
    # Arredondar para os múltiplos de 5 mais próximos
    coordenada_proxima = np.round(meio / 5) * 5
    
    return coordenada_proxima
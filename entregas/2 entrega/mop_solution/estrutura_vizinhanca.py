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
    # Remove os clientes do PA
    dados['possiveis_coord_PA'] = PAs_ativos
    # Obtém os clientes do PA desativado primeiro
    clientes_desalocados = np.where(dados['cliente_por_PA'][:, PA_menos_clientes] == 1)[0]
    #Apaga o PA da relação clientes por PA
    dados['cliente_por_PA'] = np.delete(dados['cliente_por_PA'], PA_menos_clientes, axis=1)
    coluna_zeros = np.zeros((dados['cliente_por_PA'].shape[0], 1))
    
    dados['cliente_por_PA'] = np.hstack((dados['cliente_por_PA'], coluna_zeros))


    dados = realoca_clientes(dados, clientes_desalocados)

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
        dados['cliente_por_PA'] = np.delete(dados['cliente_por_PA'], PA_menos_clientes, axis=1)
        #Adiciona coluna de zeros no fim do array
        coluna_zeros = np.zeros((dados['cliente_por_PA'].shape[0], 1))
        dados['cliente_por_PA'] = np.hstack((dados['cliente_por_PA'], coluna_zeros))

        # Obtém os clientes do PA desativado
        clientes_desalocados = np.where(dados['cliente_por_PA'][:, PA_menos_clientes] == 1)[0]

        # Remove os clientes do PA
        dados['cliente_por_PA'][:, PA_menos_clientes] = 0

        dados = realoca_clientes(dados, clientes_desalocados)
        # Tenta realocar os clientes desalocados
        # for cliente in clientes_desalocados:
        #     # Remove a conexão do cliente com o PA desativado
        #     dados['cliente_por_PA'][cliente, PA_menos_clientes] = 0
        #     # Calcula distâncias apenas para PAs ativos
        #     distancias = np.linalg.norm(dados['coord_clientes'][cliente] - dados['possiveis_coord_PA'], axis=1)

        #     # Encontra PAs ativos dentro do limite de sinal
        #     PAs_ativos_alcance = PAs_ativos[np.where(distancias <= dados['limite_sinal_PA'])[0]]

        #     # Tenta conectar ao PA com capacidade disponível
        #     for i in range(len(PAs_ativos_alcance)):
        #         PA = PAs_ativos_alcance[i]
        #         consumo_atual_pa = np.sum(dados['cliente_por_PA'][:, i] * dados['cons_clientes'])
        #         if consumo_atual_pa + dados['cons_clientes'][cliente] <= dados['capacidade_PA']:
        #             dados['cliente_por_PA'][cliente, i] = 1
        #             break  # Conectou o cliente, passa para o próximo

    print(f"{r3(dados)} | {r4(dados)} |{r5(dados)} |{r6(dados)} |{r7(dados, 1)} |{r8(dados)} ")
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
            print(f'Tentando realocart o cliente {i} ao PA {PA}')
            idx_PA = int(PA[2])
            if client_is_able_to_connect(dados, i, cliente, PA[:2], consumo_PAs[idx_PA]):
                print("Conseguiu")
                cliente_por_PA[i][idx_PA] = 1
                consumo_PAs[idx_PA] += dados['cons_clientes'][i]
            break
    
    somas = np.sum(cliente_por_PA, axis=1)
    # Verifique se todas as somas são iguais a 1
    todas_iguais_a_um = np.all(somas == 1)
    if (todas_iguais_a_um):
        print("Nao tem cliente em dois PAs")
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
    dist_matrix = np.load('dist_matrix.npy')
    num_clientes = int(dist_matrix.shape[2])
    pas_ativos = coord_PAs
    num_PAs = len(pas_ativos)
    coord_pas_ativos = pas_ativos // 5
    coord_pas_ativos = coord_pas_ativos.astype(int)
    PAs_ordenados_por_dist = np.zeros((num_clientes, num_PAs, 3))

    for i in range(num_clientes):
        grid_dist = dist_matrix[:, :, i] #(81,81)
        
        try:
            dist_PAs = grid_dist[coord_pas_ativos[:, 0], coord_pas_ativos[:, 1]]
        except Exception as e:
            print(f"coord_pas_ativos: {coord_pas_ativos}")
        indexes_ordenados = np.argsort(dist_PAs)
        PAs_ordenados_por_dist[i, :, :2] = pas_ativos[indexes_ordenados]
        PAs_ordenados_por_dist[i, :, 2] = indexes_ordenados
    return PAs_ordenados_por_dist

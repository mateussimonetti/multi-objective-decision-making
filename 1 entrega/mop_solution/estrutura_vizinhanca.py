import numpy as np
import os,sys,math, copy, pickle
from scipy.spatial import distance
import random
import pandas as pd
import matplotlib.pyplot as plt


# novas estruturas

def calcular_distancia(x1, y1, x2, y2):
  #Calcula a distância euclidiana entre dois pontos.
  return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calcular_uso_PA(x):
  num_PAs = len(x['possiveis_coord_PA'])
  users_on_PA = np.sum(x['cliente_por_PA'], axis=0)
  return users_on_PA[:num_PAs]


def encontrar_pas_na_regiao(x, regiao_x, regiao_y):
  """Encontra os índices dos PAs dentro de uma região do grid."""
  pas_na_regiao = []
  for PA_index in range(x['n_max_possivel_PAs']):
    pa_x = x['possiveis_coord_PA'][PA_index, 0]
    pa_y = x['possiveis_coord_PA'][PA_index, 1]
    if regiao_x[0] <= pa_x < regiao_x[1] and regiao_y[0] <= pa_y < regiao_y[1]:
      pas_na_regiao.append(PA_index)
  return pas_na_regiao

def client_is_able_to_connect(dados, i, coord, posicao_PA, consumo_atual_pa):
    return np.linalg.norm(coord - posicao_PA) <= dados['limite_sinal_PA'] and \
           np.sum(dados['cliente_por_PA'][i]) ==  0 and \
           consumo_atual_pa + dados['cons_clientes'][i] <= dados['capacidade_PA']

def PAs_mais_prox(idx_cliente, coord_PAs):
    dist_matrix = np.load('dist_matrix.npy')
    pas_ativos = coord_PAs
    num_PAs = len(pas_ativos)
    coord_pas_ativos = pas_ativos / 5
    coord_pas_ativos = coord_pas_ativos.astype(int)
    coordenadas_PAs_mais_prox = np.zeros((num_PAs, 2))

  # Criar uma lista de tuplas (coord_PA, dist_PA_atual)
    lista_coord_dist = []

    for i, pa in enumerate(coord_pas_ativos):
        dist_PA_atual = dist_matrix[pa[0], pa[1], idx_cliente]  # Corrigido para acesso correto
        lista_coord_dist.append((coord_PAs[i], dist_PA_atual))

    # Ordenar a lista com base na distância atual do PA
    lista_coord_dist_ordenada = sorted(lista_coord_dist, key=lambda x: x[1])

    # Extrair as coordenadas ordenadas
    coordenadas_PAs_mais_prox = np.array([coord for coord, _ in lista_coord_dist_ordenada])

    return coordenadas_PAs_mais_prox

def calcula_consumo_PAs(x):
  clientes_por_PA = x['cliente_por_PA']
  cons_clientes = x['cons_clientes']

  return np.dot(cons_clientes.T, clientes_por_PA)

def k11(x):
  # Desativa o PA com menor uso e ativa um aleatório, redistribuindo clientes. 
  # Clientes que não puderem ser atendidos por outro PA ficarão sem serviço.

  # Calcula o uso de cada PA
  uso_PAs = calcular_uso_PA(x)

  # Encontra o PA com menor uso que está ativo
  PA_menor_uso = np.argmin(uso_PAs)

  # Desativa o PA com menor uso
  coord_PAs = x['possiveis_coord_PA']
  remocao_pa = np.delete(coord_PAs, PA_menor_uso, axis=0)
  x['possiveis_coord_PA'] = remocao_pa

  # Libera os clientes do PA desativado
  idx_clientes_liberados = np.where(x['cliente_por_PA'][:, PA_menor_uso] == 1)[0]
  x['cliente_por_PA'][idx_clientes_liberados, PA_menor_uso] = 0
  coord_clientes = x['coord_clientes']

  #Encontra o array de PAs mais proximos ordenado
  print(f'index de clientes liberados: {idx_clientes_liberados}')
  arr_consumo_pa = calcula_consumo_PAs(x)
  for idx_cliente in idx_clientes_liberados:
    print(f'coord cliente {idx_cliente}: {coord_clientes[idx_cliente]}')
    possiveis_PAs_p_conectar = PAs_mais_prox(idx_cliente, x['possiveis_coord_PA'])
    for pa_index, pa in enumerate(possiveis_PAs_p_conectar):
      consumo_pa = arr_consumo_pa[pa_index]
      if client_is_able_to_connect(x, idx_cliente, coord_clientes[idx_cliente], pa, consumo_pa):
        x['cliente_por_PA'][idx_cliente, pa_index] = 1
        print(f'alocou cliente {idx_cliente}') 
      break
  
  print(f"possiveis coord pa: {x['possiveis_coord_PA']}")
  return x

def k12(x):
  # Encontra os 5 clientes mais distantes de seus PAs (apenas 
  # clientes com PA atribuído) e tenta redistribuí-los.

  distancias = np.full(len(x['coord_clientes']), np.inf)  # Inicializa com infinito para clientes sem PA
  clientes_com_PA = np.where(np.sum(x['cliente_por_PA'], axis=1) > 0)[0]

  # Calcula a distância apenas para clientes com PA atribuído
  for cliente_index in clientes_com_PA:
    PA_atual = np.where(x['cliente_por_PA'][cliente_index, :] == 1)[0][0] 
    distancias[cliente_index] = calcular_distancia(
        x['coord_clientes'][cliente_index, 0],
        x['coord_clientes'][cliente_index, 1],
        x['possiveis_coord_PA'][PA_atual, 0],
        x['possiveis_coord_PA'][PA_atual, 1],
    )

  # Encontra os 5 clientes mais distantes que TEM PA
  clientes_mais_distantes = np.argsort(distancias)[-5:]
  clientes_mais_distantes = np.intersect1d(clientes_mais_distantes, clientes_com_PA)

  # linhas para validação de resultados
  # print(clientes_mais_distantes)
  # for cliente_index in clientes_mais_distantes:
  #   PA_atual = np.where(x['cliente_por_PA'][cliente_index, :] == 1)[0][0] 
  #   distancias[cliente_index] = calcular_distancia(
  #       x['coord_clientes'][cliente_index, 0],
  #       x['coord_clientes'][cliente_index, 1],
  #       x['possiveis_coord_PA'][PA_atual, 0],
  #       x['possiveis_coord_PA'][PA_atual, 1],
  #   )
  #   print(distancias[cliente_index])

  # Tenta redistribuir os clientes mais distantes
  for cliente_index in clientes_mais_distantes:
    # Calcula o consumo do cliente
    cliente_consumo = x['cons_clientes'][cliente_index]

    # Desconecta do PA atual
    PA_atual = np.where(x['cliente_por_PA'][cliente_index, :] == 1)[0][0]
    x['cliente_por_PA'][cliente_index, PA_atual] = 0

    # Tenta conectar a outro PA disponível
    PAs_disponiveis = np.where(x['uso_PAs'] == 1)[0]
    random.shuffle(PAs_disponiveis) 

    for PA_candidato in PAs_disponiveis:
      if calcular_uso_PA(x, PA_candidato) + cliente_consumo <= x['capacidade_PA']:
        distancia_candidato = calcular_distancia(
            x['coord_clientes'][cliente_index, 0],
            x['coord_clientes'][cliente_index, 1],
            x['possiveis_coord_PA'][PA_candidato, 0],
            x['possiveis_coord_PA'][PA_candidato, 1],
        )
        if distancia_candidato <= x['limite_sinal_PA']:
          x['cliente_por_PA'][cliente_index, PA_candidato] = 1
          break
    else:
      # Se não encontrar um PA disponível, reconecta ao PA original
      x['cliente_por_PA'][cliente_index, PA_atual] = 1

  # linhas para validação de resultados
  # for cliente_index in clientes_mais_distantes:
  #   PA_atual = np.where(x['cliente_por_PA'][cliente_index, :] == 1)[0][0] 
  #   distancias[cliente_index] = calcular_distancia(
  #       x['coord_clientes'][cliente_index, 0],
  #       x['coord_clientes'][cliente_index, 1],
  #       x['possiveis_coord_PA'][PA_atual, 0],
  #       x['possiveis_coord_PA'][PA_atual, 1],
  #   )
  #   print(distancias[cliente_index])


  return x

def k13(x):
  # Desabilita o PA com menor utilização e redistribui seus clientes 
  # para outros PAs habilitados. Clientes que não puderem ser 
  # redistribuídos serão desconectados.

  # Calcula o uso de cada PA
  uso_PAs = np.array([calcular_uso_PA(x, i) if x['uso_PAs'][i] == 1 else np.inf for i in range(len(x['uso_PAs']))])

  # Encontra o PA com menor uso que está ativo
  PA_menor_uso = np.argmin(uso_PAs)

  # Verifica se existe mais de um PA ativo
  if np.count_nonzero(x['uso_PAs']) <= 1:
    print("Apenas um ou nenhum PA ativo. Impossível redistribuir.")
    return x

  # Desativa o PA com menor uso
  x['uso_PAs'][PA_menor_uso] = 0

  # Obtém os clientes do PA que será desativado
  clientes_para_redistribuir = np.where(x['cliente_por_PA'][:, PA_menor_uso] == 1)[0]

  # Tenta redistribuir os clientes
  for cliente_index in clientes_para_redistribuir:
    cliente_consumo = x['cons_clientes'][cliente_index]

    # Desconecta do PA atual
    x['cliente_por_PA'][cliente_index, PA_menor_uso] = 0

    # Tenta conectar a outro PA disponível
    PAs_disponiveis = np.where(x['uso_PAs'] == 1)[0]
    random.shuffle(PAs_disponiveis)

    for PA_candidato in PAs_disponiveis:
      if calcular_uso_PA(x, PA_candidato) + cliente_consumo <= x['capacidade_PA']:
        distancia_candidato = calcular_distancia(
            x['coord_clientes'][cliente_index, 0],
            x['coord_clientes'][cliente_index, 1],
            x['possiveis_coord_PA'][PA_candidato, 0],
            x['possiveis_coord_PA'][PA_candidato, 1],
        )
        if distancia_candidato <= x['limite_sinal_PA']:
          # Conecta ao novo PA
          x['cliente_por_PA'][cliente_index, PA_candidato] = 1
          break  # Sai do loop se conectou com sucesso
    else:
      # Não encontrou nenhum PA disponível, cliente permanece desconectado
      pass  # Não precisa fazer nada aqui, pois o cliente já foi desconectado

  return x

def k14(x):

  # Seleciona uma região aleatória do grid, encontra o PA com 
  # menos clientes conectados nessa região e tenta redistribuir 
  # esses clientes para outros PAs habilitados em qualquer 
  # lugar do grid.


  # Define uma região aleatória de 50x50 com x e y sempre positivos
  regiao_x = (random.randint(0, max(0, x['sizex'][1] - 50)), random.randint(0, max(0, x['sizex'][1] - 50)) + 50)
  regiao_y = (random.randint(0, max(0, x['sizey'][1] - 50)), random.randint(0, max(0, x['sizey'][1] - 50)) + 50)

  # Encontra os PAs ativos dentro da região
  pas_na_regiao = encontrar_pas_na_regiao(x, regiao_x, regiao_y)
  pas_ativos_na_regiao = np.intersect1d(pas_na_regiao, np.where(x['uso_PAs'] == 1)[0])

  # Se não houver PAs ativos na região, retorna
  if len(pas_ativos_na_regiao) == 0:
    #print("Nenhum PA ativo encontrado na região selecionada.")
    return x

  # Encontra o PA com menos clientes conectados na região
  num_clientes_por_pa = np.sum(x['cliente_por_PA'][:, pas_ativos_na_regiao], axis=0)
  PA_menor_uso_na_regiao = pas_ativos_na_regiao[np.argmin(num_clientes_por_pa)]

  # Desativa o PA com menor uso na região
  x['uso_PAs'][PA_menor_uso_na_regiao] = 0

  # Tenta redistribuir os clientes do PA desabilitado
  clientes_para_redistribuir = np.where(x['cliente_por_PA'][:, PA_menor_uso_na_regiao] == 1)[0]
  for cliente_index in clientes_para_redistribuir:
    cliente_consumo = x['cons_clientes'][cliente_index]

    # Tenta conectar a outro PA disponível em qualquer região
    PAs_disponiveis = np.where(x['uso_PAs'] == 1)[0]
    random.shuffle(PAs_disponiveis)

    for PA_candidato in PAs_disponiveis:
      if calcular_uso_PA(x, PA_candidato) + cliente_consumo <= x['capacidade_PA']:
        distancia_candidato = calcular_distancia(
            x['coord_clientes'][cliente_index, 0],
            x['coord_clientes'][cliente_index, 1],
            x['possiveis_coord_PA'][PA_candidato, 0],
            x['possiveis_coord_PA'][PA_candidato, 1],
        )
        if distancia_candidato <= x['limite_sinal_PA']:
          # Conecta ao novo PA
          x['cliente_por_PA'][cliente_index, PA_candidato] = 1
          break
    else:
      # Cliente permanece desconectado se nenhum PA estiver disponível
      pass

  return x
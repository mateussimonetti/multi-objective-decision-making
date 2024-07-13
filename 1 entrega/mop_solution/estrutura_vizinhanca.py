import numpy as np
import os,sys,math, copy, pickle
from scipy.spatial import distance
import random
import pandas as pd
import matplotlib.pyplot as plt

#coloca o ponto de acesso 'ponto' em um lugar aleatorio
#troca o status de um ponto de acesso
def k1(dados):
    uso_PAs = dados['uso_PAs'].copy() #PAs ativos
    cliente_por_PA = dados['cliente_por_PA'].copy() #cliente x pa

    pas_act = np.where(uso_PAs==1)[0]
    pas_dact = np.where(uso_PAs==0)[0]

    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0 and len(pas_dact) > 0:

        pv = np.random.choice(pas_act, size=1, replace=False)
        pn = np.random.choice(pas_dact, size=1, replace=False)
        
        #passando todos os clientes que são atendidos pelo ponto de acesso para o novo ponto de acesso
        nad = cliente_por_PA[:,pn].copy()
        cliente_por_PA[:,pn] = cliente_por_PA[:,pv].copy()
        cliente_por_PA[:,pv] = nad.copy()

        #trocando o estados de utilização dos pontos de acesso
        uso_PAs[pv] = not uso_PAs[pv]
        uso_PAs[pn] = not uso_PAs[pn]
        #atualizando 
        dados['uso_PAs'] = uso_PAs
        dados['cliente_por_PA'] = cliente_por_PA

    return dados

#Coloca para um cliente ser atendido por outro ponto de acesso ativo
def k2(dados):
    uso_PAs = dados['uso_PAs'].copy()
    cliente_por_PA = dados['cliente_por_PA'].copy()

    pas_act = np.where(uso_PAs==1)[0]

    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0:

        pn = np.random.choice(pas_act, size=1, replace=False)
        cliente = np.random.choice(cliente_por_PA.shape[0], size=1, replace=False)
    
        pontovelho = cliente_por_PA[cliente,:] == 1
        cliente_por_PA[cliente,pontovelho[0]] = 0
        cliente_por_PA[cliente,pn] = 1
    
        dados['uso_PAs'] = uso_PAs
        dados['cliente_por_PA'] = cliente_por_PA
    
    return dados
    
#Altera o estado do ponto de acesso 
def k3(dados):
    uso_PAs = dados['uso_PAs'].copy()
    cliente_por_PA = dados['cliente_por_PA'].copy()


    pas_act = np.where(uso_PAs==1)[0]

    if len(pas_act) > 0:
        pv = np.random.choice(pas_act, size=1, replace=False)
        clt = np.where(cliente_por_PA[:,pv]==1)
        for c in clt:
            ps = np.random.choice(pas_act, size=1, replace=False)
            if ps == pv:
                ps = np.random.choice(pas_act, size=1, replace=False)
                cliente_por_PA[c,ps] = 1
        cliente_por_PA[clt, pv] = 0 
        
    
        uso_PAs[pv] = 0
        dados['uso_PAs'] = uso_PAs
        dados['cliente_por_PA'] = cliente_por_PA

    return dados


#Redistribui aleatoriamente os clientes
def k4(dados):
    uso_PAs = dados['uso_PAs'].copy()
    cliente_por_PA = dados['cliente_por_PA'].copy()

    pas_act = np.where(uso_PAs==1)[0]
    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0:
        clt1 = np.random.choice(pas_act, size=1, replace=False)
        clt2 = np.random.choice(pas_act, size=1, replace=False)
        #para cada cliente redistribui os clientes para cada um que será ativo
        clientes_1 = cliente_por_PA[:,clt1].copy()
        clientes_2 = cliente_por_PA[:,clt2].copy()
        clt1_ac = np.where(clientes_1==1)[0]
        clt2_ac = np.where(clientes_2==1)[0]
        if len(clt1_ac) > 0 and len(clt2_ac) > 0:
            s1 = np.random.choice(clt1_ac, size=1, replace=False)
            s2 = np.random.choice(clt2_ac, size=1, replace=False)
            clientes_1[s1], clientes_1[s2] = 0, 1
            clientes_2[s2], clientes_2[s1] = 0, 1
            cliente_por_PA[:,clt1] = clientes_1
            cliente_por_PA[:,clt2] = clientes_2

    dados['uso_PAs'] = uso_PAs
    dados['cliente_por_PA'] = cliente_por_PA
    return dados

# novas estruturas

def calcular_distancia(x1, y1, x2, y2):
  #Calcula a distância euclidiana entre dois pontos.
  return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calcular_uso_PA(x, PA_index):
  #Calcula o uso total de banda do PA.
  clientes_conectados = np.where(x['cliente_por_PA'][:, PA_index] == 1)[0]
  uso_total = np.sum(x['cons_clientes'][clientes_conectados])
  return uso_total

def encontrar_pas_na_regiao(x, regiao_x, regiao_y):
  """Encontra os índices dos PAs dentro de uma região do grid."""
  pas_na_regiao = []
  for PA_index in range(x['n_max_possivel_PAs']):
    pa_x = x['possiveis_coord_PA'][PA_index, 0]
    pa_y = x['possiveis_coord_PA'][PA_index, 1]
    if regiao_x[0] <= pa_x < regiao_x[1] and regiao_y[0] <= pa_y < regiao_y[1]:
      pas_na_regiao.append(PA_index)
  return pas_na_regiao

def k11(x):
  # Desativa o PA com menor uso e ativa um aleatório, redistribuindo clientes. 
  # Clientes que não puderem ser atendidos por outro PA ficarão sem serviço.

  # Calcula o uso de cada PA
  uso_PAs = np.array([calcular_uso_PA(x, i) if x['uso_PAs'][i] == 1 else np.inf for i in range(len(x['uso_PAs']))])

  # Encontra o PA com menor uso que está ativo
  PA_menor_uso = np.argmin(uso_PAs)

  # Desativa o PA com menor uso
  x['uso_PAs'][PA_menor_uso] = 0
  
  # Libera os clientes do PA desativado
  clientes_liberados = np.where(x['cliente_por_PA'][:, PA_menor_uso] == 1)[0]
  x['cliente_por_PA'][clientes_liberados, PA_menor_uso] = 0

  # Seleciona um novo PA aleatoriamente entre os não utilizados
  PAs_nao_utilizados = np.where(x['uso_PAs'] == 0)[0]
  novo_PA = random.choice(PAs_nao_utilizados)

  # Ativa o novo PA
  x['uso_PAs'][novo_PA] = 1

  # Redistribui os clientes liberados
  for cliente in clientes_liberados:
    # Calcula a distância do cliente para o novo PA
    distancia_novo_PA = calcular_distancia(
      x['coord_clientes'][cliente, 0], 
      x['coord_clientes'][cliente, 1],
      x['possiveis_coord_PA'][novo_PA, 0], 
      x['possiveis_coord_PA'][novo_PA, 1]
    )

    # Tenta conectar ao novo PA se estiver dentro do limite de sinal e houver capacidade
    if distancia_novo_PA <= x['limite_sinal_PA'] and \
       calcular_uso_PA(x, novo_PA) + x['cons_clientes'][cliente] <= x['capacidade_PA']:
      x['cliente_por_PA'][cliente, novo_PA] = 1
    else:
      # Tenta conectar a outro PA disponível
      PAs_disponiveis = np.where(x['uso_PAs'] == 1)[0]
      PAs_disponiveis = np.delete(PAs_disponiveis, np.where(PAs_disponiveis == novo_PA))
      
      for PA_candidato in PAs_disponiveis:
        distancia_candidato = calcular_distancia(
          x['coord_clientes'][cliente, 0], 
          x['coord_clientes'][cliente, 1],
          x['possiveis_coord_PA'][PA_candidato, 0], 
          x['possiveis_coord_PA'][PA_candidato, 1]
        )
        if distancia_candidato <= x['limite_sinal_PA'] and \
           calcular_uso_PA(x, PA_candidato) + x['cons_clientes'][cliente] <= x['capacidade_PA']:
          x['cliente_por_PA'][cliente, PA_candidato] = 1
          break
      else:
        # Cliente fica sem atendimento
        pass  

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
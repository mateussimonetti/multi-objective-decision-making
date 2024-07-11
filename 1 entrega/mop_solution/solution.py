import numpy as np
from sklearn.cluster import DBSCAN

def sol_zero(dados):
    eps = 50  # Distância máxima entre dois pontos para que um seja considerado como vizinho do outro
    db = get_clusters(np.array(dados['coord_clientes']), eps=eps)
    labels = db.labels_

    # Encontrar as coordenadas dos PAs como centróides dos clusters
    unique_labels = set(labels)
    unique_labels.discard(-1)  # Remove o rótulo de ruído
    print(unique_labels)

    coord_clientes = dados['coord_clientes']
    num_clientes = len(coord_clientes)
    n_max_possivel_PAs = dados['cliente_por_PA'].shape[1]
    num_possiveis_alocacoes = dados['possiveis_coord_PA'].shape[0]

    # Verificar se o número de clusters é maior que o número máximo de PAs
    if len(unique_labels) > n_max_possivel_PAs:
        unique_labels = set(list(unique_labels)[:n_max_possivel_PAs])

    label_to_pa_index = {label: idx for idx, label in enumerate(unique_labels)}

    # Inicializar a matriz uso_PAs
    uso_PAs = [False] * num_possiveis_alocacoes

    for label in unique_labels:
        cluster_points = coord_clientes[labels == label]
        centroid = cluster_points.mean(axis=0)
        posicao_PA = np.round(centroid / 5) * 5
        print(posicao_PA)


        pa_index = label_to_pa_index[label]
        dados['possiveis_coord_PA'][pa_index] = posicao_PA
        uso_PAs[pa_index] = True
        
        # Atribuir clientes ao PA mais próximo
        for i, coord in enumerate(coord_clientes):
            if labels[i] == label:
                dados['cliente_por_PA'][i, pa_index] = 1

    # Atualiza os dados
    dados['uso_PAs'] = uso_PAs

    return dados

def get_clusters(coord_clientes, eps=3, min_samples=5, min_min_samples=1):
    while True:
        # Aplicar o DBSCAN
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(coord_clientes)
        labels = db.labels_

        # Encontrar o número de clusters (rótulos únicos, excluindo ruído)
        unique_labels = set(labels)
        unique_labels.discard(-1)  # Remove o rótulo de ruído

        # Verificar se pelo menos dois clusters foram encontrados
        if len(unique_labels) >= 3 or min_samples <= min_min_samples:
            break

        # Reduzir min_samples pela metade, garantindo que não vá abaixo de 1
        min_samples = max(min_samples // 2, min_min_samples)

    return db  # Retorna o objeto DBSCAN ajustado
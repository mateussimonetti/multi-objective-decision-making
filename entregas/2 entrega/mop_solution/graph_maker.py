import matplotlib.pyplot as plt
import numpy as np

def plot_infos(dados, y, dir_='./', cod='final'):
    possiveis_coord_PA = dados['possiveis_coord_PA']
    coord_clientes = dados['coord_clientes']
    cliente_por_PA_ = dados['cliente_por_PA']
    x_sol = possiveis_coord_PA

    fig, axes = plt.subplots(4, 1, figsize=(8, 16))

    # Plot dos erros e restrições
    labels = ['Erro', 'Restrição 3', 'Restrição 4', 'Restrição 5', 'Restrição 6', 'Restrição 7']
    for i in range(6):
        axes[0].plot(y[i], label=labels[i])
    axes[0].legend(loc=1)
    axes[0].set_ylabel('Erro')
    axes[0].set_xlabel('Alterações')
    axes[0].set_title('Erros e Restrições')
    axes[0].grid(True)

    # Plot dos pontos de acesso
    axes[1].plot(y[6])
    axes[1].set_ylabel('#Pontos de Acesso')
    axes[1].set_xlabel('Alterações')
    axes[1].set_title('Pontos de Acesso')
    axes[1].grid(True)

    # Plot da distribuição de clientes e pontos de acesso
    axes[2].plot(coord_clientes[:, 0], coord_clientes[:, 1], 'bs', label='Clientes')
    axes[2].plot(x_sol[:, 0], x_sol[:, 1], 'ro', label='Pontos de Acesso')
    axes[2].legend(loc=1)
    axes[2].set_xlabel('X')
    axes[2].set_ylabel('Y')
    axes[2].set_title('Distribuição de Clientes e Pontos de Acesso')
    axes[2].grid(True)

    # Plot das conexões entre clientes e pontos de acesso
    axes[3].plot(coord_clientes[:, 0], coord_clientes[:, 1], 'bs', label='Clientes')
    axes[3].plot(x_sol[:, 0], x_sol[:, 1], 'ro', label='Pontos de Acesso')
    for id_c, c in enumerate(coord_clientes):
        s = np.where(cliente_por_PA_[id_c, :] == 1)[0]
        if len(s > 0) and s <= len(possiveis_coord_PA)-1:
            axes[3].plot([int(coord_clientes[id_c, 0]), int(possiveis_coord_PA[s, 0])], [int(coord_clientes[id_c, 1]), int(possiveis_coord_PA[s, 1])])
    axes[3].legend(loc=1)
    axes[3].set_xlabel('X')
    axes[3].set_ylabel('Y')
    axes[3].set_title('Conexões entre Clientes e Pontos de Acesso')
    axes[3].grid(True)

    # Salvar figuras
    print(f'Resultado em {dir_}plot_{cod}.png')
    fig.savefig(dir_ + 'plot_' + cod + '.png')
    plt.close(fig)

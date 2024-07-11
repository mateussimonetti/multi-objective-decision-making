import numpy as np
import os,sys,math, copy, pickle, time
from scipy.spatial import distance
from random import seed,random,randint,randrange
import pandas as pd
import matplotlib.pyplot as plt


seed(1234)
np.random.seed(1234)


def plot_infos(dados, y, dir_='./', cod = 'final'):
    P = dados['P']
    pos = dados['ap'] == 1
    C = dados['C']
    acp_ = dados['acp']
    x_sol = P[pos]
    plt.ylabel('Erro')
    plt.xlabel('Alterações')
    plt.plot(y[0], label = 'y')
    plt.plot(y[1], label = 'Rest 3')
    plt.plot(y[2], label = 'Rest 4')
    plt.plot(y[3], label = 'Rest 5')
    plt.plot(y[4], label = 'Rest 6')
    plt.plot(y[5], label = 'Rest 7')
    plt.legend(loc=1)
    #plt.show()
    plt.savefig(dir_+'log_'+cod+'.png')
    plt.close()
    plt.plot(y[6])
    plt.ylabel('#Pontos de Acesso')
    plt.xlabel('Alterações')
    #plt.show()
    plt.savefig(dir_+'PAs_'+cod+'.png')
    plt.close()

    plt.plot(C[:,0], C[:,1], 'bs', label='Clientes')
    plt.plot(x_sol[:,0], x_sol[:,1], 'ro', label='Pontos de Acesso')
    plt.savefig(dir_+'Distrib_'+cod+'.png')
    plt.close()
    plt.plot(C[:,0], C[:,1], 'bs', label='Clientes')
    plt.plot(x_sol[:,0], x_sol[:,1], 'ro', label='Pontos de Acesso')
    for id_c,c in enumerate(C):
        s = np.where(acp_[id_c,:]==1)[0]
        if len(s)>0:
            plt.plot([int(C[id_c,0]), int(P[s,0])], [int(C[id_c,1]), int(P[s,1])])
    plt.legend(loc=1)
    plt.savefig(dir_+'DistCon_'+cod+'.png')
    #plt.show()
    plt.close()

#função que será otimizada
def f1(dados):
    ap = dados['ap']

    # Calcula o valor da função objetivo f1
    f1 = sum(ap)

    # valor de f1 penalizada pelos valores das restrições
    f1_penal = f1 + 10 * (rest3(dados) + rest4(dados) + rest5(dados) + rest6(dados) + rest7(dados))

    return f1_penal

def f2(dados):
    acp = dados['acp']
    rp = dados['rp']
    d = dados['d']
    P = dados['P']
    
    #Calcula o valor da função objetivo f2
    f2_value = 0
    for id_c,c in enumerate(C):
        for id_p,p in enumerate(P):
            f2_value += d[id_c, id_p] * acp[id_c][id_p]
    
    #valor de f2 penalizada pelos valores das restrições
    f2_penal = f2_value + 10 * (rest3(dados) + rest4(dados) + rest5(dados) + rest6(dados) + rest7(dados))

    return f2_penal

def rest3(dados):
    N = dados['N']
    C = dados['C']
    acp = dados['acp']

    penal = int(N * len(C)) - acp.sum()
    penal = max(0, penal) ** 2
    return penal *1000

# Garante nao estourar a capacidade do ponto de acesso
def rest4(dados):
    acp = dados['acp']
    cc = dados['cc']
    cp = dados['cp']

    #pontos_cap = np.matmul(acp.transpose(), cc) - cp

    # soma somente os pontos que nao obedecem a restricao
    penal = 0
    
    for id_p,p in enumerate(P):
        penal += max(0, np.sum(acp[:,id_p]*cc) - cp)

    #for i in pontos_cap:
    #    if (i > 0):
    #        penal += i

    return penal * 1000

# garante que cada cliente estará conectado a no maximo 1 PA
def rest5(dados):
    acp = dados['acp']
    pert = acp.sum(axis=1) - 1
    penal = 0

    for id_c,c in enumerate(C):
        penal += max(0, np.sum(acp[id_c,:]) - 1)
    
    return penal *1000

# garante que nao exceda o numero de pontos de acesso
def rest6(dados):
    ap = dados['ap']
    n_max = dados['n_max']

    penal = np.sum(ap) - n_max
    penal = max(0, penal) ** 2

    return penal * 10000

# Garante que a distancia nao exceda a distancia max de um ponto de acesso
def rest7(dados):
    acp = dados['acp']
    rp = dados['rp']
    d = dados['d']

    penal = 0
    for id_c,c in enumerate(C):
        for id_p,p in enumerate(P):
            penal += max(0, (d[id_c, id_p] * acp[id_c][id_p]) - rp)
    
    
    return penal

#coloca o ponto de acesso 'ponto' em um lugar aleatorio
#troca o status de um ponto de acesso
def novoLocalPontoAcesso(dados):
    ap = dados['ap'].copy() #pas ativos
    acp = dados['acp'].copy() #cliente x pa

    pas_act = np.where(ap==1)[0]
    pas_dact = np.where(ap==0)[0]

    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0 and len(pas_dact) > 0:
        #ponto velho
        #ponto = False
        #while(not ponto):

        pv = np.random.choice(pas_act, size=1, replace=False)
        #    ponto = ap[pv]
        #novo ponto
        #ponto = True
        #while(ponto):
        
        pn = np.random.choice(pas_dact, size=1, replace=False)
        #ponto = ap[pn]
        
        #passando todos os clientes que são atendidos pelo ponto de acesso para o novo ponto de acesso
        nad = acp[:,pn].copy()
        acp[:,pn] = acp[:,pv].copy()
        acp[:,pv] = nad.copy()

        '''#Redistribuir clientes entre outros pas ativos aleatoriamente
        #clients_pv = acp[:,pv].copy()
        #client_pv = clients_pv == 1
        #for client in client_pv:
            #selecionar ap
            pas_activ = ap == 1
            pa = np.random.choice(pas_activ, size=1, replace=False)
            #passar o cliente para ap
            acp[client'''

        #trocando o estados de utilização dos pontos de acesso
        ap[pv] = not ap[pv]
        ap[pn] = not ap[pn]
        #ap[pn] = 1
        #atualizando 
        dados['ap'] = ap
        dados['acp'] = acp

    return dados

#Coloca para um cliente ser atendido por outro ponto de acesso ativo
def novoPontoAcessoClient(dados):
    ap = dados['ap'].copy()
    acp = dados['acp'].copy()

    pas_act = np.where(ap==1)[0]

    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0:

        pn = np.random.choice(pas_act, size=1, replace=False)
        cliente = np.random.choice(acp.shape[0], size=1, replace=False)
    
        pontovelho = acp[cliente,:] == 1
        acp[cliente,pontovelho[0]] = 0
        acp[cliente,pn] = 1
    
        dados['ap'] = ap
        dados['acp'] = acp
    
    return dados
    
#Altera o estado do ponto de acesso 
def usoUmPontoAcesso(dados):
    ap = dados['ap'].copy()
    acp = dados['acp'].copy()
    P = dados['P'].copy()
    C = dados['C'].copy()


    pas_act = np.where(ap==1)[0]

    if len(pas_act) > 0:
        pv = np.random.choice(pas_act, size=1, replace=False)
        clt = np.where(acp[:,pv]==1)
        for c in clt:
            ps = np.random.choice(pas_act, size=1, replace=False)
            if ps == pv:
                ps = np.random.choice(pas_act, size=1, replace=False)
                acp[c,ps] = 1
        acp[clt, pv] = 0 
        
    
        ap[pv] = 0
        dados['ap'] = ap
        dados['acp'] = acp

    return dados


#Redistribui aleatoriamente os clientes
def usoPontoAcesso(dados):
    ap = dados['ap'].copy()
    acp = dados['acp'].copy()
    P = dados['P'].copy()
    C = dados['C'].copy()

    pas_act = np.where(ap==1)[0]
    #selecionar um ligado para distribuir entre outros
    if len(pas_act) > 0:
        clt1 = np.random.choice(pas_act, size=1, replace=False)
        clt2 = np.random.choice(pas_act, size=1, replace=False)
        #para cada cliente redistribui os clientes para cada um que será ativo
        clientes_1 = acp[:,clt1].copy()
        clientes_2 = acp[:,clt2].copy()
        clt1_ac = np.where(clientes_1==1)[0]
        clt2_ac = np.where(clientes_2==1)[0]
        if len(clt1_ac) > 0 and len(clt2_ac) > 0:
            s1 = np.random.choice(clt1_ac, size=1, replace=False)
            s2 = np.random.choice(clt2_ac, size=1, replace=False)
            clientes_1[s1], clientes_1[s2] = 0, 1
            clientes_2[s2], clientes_2[s1] = 0, 1
            acp[:,clt1] = clientes_1
            acp[:,clt2] = clientes_2
        '''for id_, clt in enumerate(clientes):
            #sorteia um novo ponto de acesso que sera ativado
            if clt:
                p = np.random.choice(ap.shape[0], size=1, replace=False)       
                acp[id_,p] = 1'''


        #for i in range(len(acp[:,io])):
        #    acp[i,io] = 0
        #troca os estados
        #ap[io] = 0


    dados['ap'] = ap
    dados['acp'] = acp
    return dados

    
#pertubação do domínio de solução
def shake(dados, k):
    #Estruturas de vizinhaças
    #1 - Coloca o ponto de acesso em um novo ponto aleatorio - passa os clientes para o novo ponto
    #2 - Trocar um cliente para outro ponto de acesso aleatorio 
    #3 - Trocar o estado de uso de um ponto de acesso aleatorio
    #4 - Altera o estado de uso de todos os pontos de acesso se tiver ativo e tiver cliente passa para outro ponto de acesso ativo
    n_change = 1
    if k == 1:
        for n in range(n_change):
            dados = novoPontoAcessoClient(copy.copy(dados))
    elif k == 2:
        for n in range(n_change):
            dados = novoLocalPontoAcesso(copy.copy(dados))
    elif k == 3:
        for n in range(n_change):
            dados = usoUmPontoAcesso(copy.copy(dados))
    else:
        for n in range(n_change):
            dados = usoPontoAcesso(copy.copy(dados))
    return dados

#retorna um valor inicial de x aleatório e factível
def initialSol(dados):
    # Calcula as coordenadas dos possíveis PAs
    C = dados['C']
    P = dados['P']
    d = dados['d']
    ap = dados['ap']
    n_max = dados['n_max']
    acp = dados['acp']
    sizex = dados['sizex']
    sizey = dados['sizey']
    grid = dados['grid']

    i=0
    for x in range(sizex[0], sizex[1], grid[0]):
        for y in range(sizey[0], sizey[1], grid[1]):
            P[i, 0] = x
            P[i, 1] = y
            i = i + 1

    # calcula distancia entre cada cliente a cada ponto de acesso
    for id_c, c in enumerate(C):
        for id_p, p in enumerate(P):
            d[id_c, id_p] = distance.euclidean(c, p)

    # gera solucao inicial - PAs ativos
    ap = np.zeros(len(P))
    n_aps_act = np.random.randint(1,n_max)
    index = np.random.randint(0, ap.size, n_aps_act)
    ap[index] = 1

    # gera solucao inicial - clientes atendidos
    for i in range(0, len(acp)):
        j = np.random.choice(index)
        acp[i, j] = 1

    #atualiza os dados
    dados['P'] = P
    dados['ap'] = ap
    dados['acp'] = acp

    return dados


def neighborhoodChange(x_, x_line_, k, f, e):
    y_ = f(x_,e)
    y_line_ = f(x_line_,e)

    if y_line_ < y_:
        x_ = copy.copy(x_line_)
        k = 1
    else:
        k += 1
    
    return x_, k

def bestImprovement(dados, f, e):

    new_dados_1 = copy.copy(dados)
    new_dados_2 = copy.copy(dados)

    # seleciona index de ap válido
    ponto = False
    while not ponto:
        pv = np.random.choice(dados['ap'].shape[0], size=1, replace=False) # pv é o index de um ponto ativo
        ponto = dados['ap'][pv]

    if pv == 0:
        pv+=1
    elif pv>=int(dados['ap'].shape[0])-2:
        pv-=1

    for i in range(len(new_dados_1['acp'][:, pv])):
        current_client = new_dados_1['acp'][i, pv]
        new_dados_1['acp'][i, pv] = new_dados_1['acp'][i, pv - 1]
        new_dados_1['acp'][i, pv - 1] = current_client

        current_client = new_dados_2['acp'][i, pv]
        new_dados_2['acp'][i, pv] = new_dados_2['acp'][i, pv + 1]
        new_dados_2['acp'][i, pv + 1] = current_client

    cpy = new_dados_1['ap'][pv] 
    new_dados_1['ap'][pv-1] = new_dados_1['ap'][pv]
    new_dados_1['ap'][pv] = cpy

 
    cpy = new_dados_2['ap'][pv] 
    new_dados_2['ap'][pv+1] = new_dados_2['ap'][pv]
    new_dados_2['ap'][pv] = cpy

    f_1 = float(f(dados,e))
    f_2 = float(f(new_dados_1, e))
    f_3 = float(f(new_dados_2, e))

    if f_1 > f_2 and f_1 > f_3:
        return dados
    elif f_2 > f_1 and f_2> f_3:
        return new_dados_1
    else:
        return new_dados_2

    
#k_max Número de estruturas de vizinhaças definidas
#max_int numero maximo de tentativas de novos valores
def BVNS(dados, f, e, k_max, max_int = 100, plot = False, n_plot = 10000, dir_save = './'):
    nfe = 0
    n_ap, y_save, rest3_save, rest4_save, rest5_save, rest6_save, rest7_save = [], [], [], [], [], [], []
    
    # Solução inicial
    dados = initialSol(copy.copy(dados))
    
    y = f(dados, e)
    time_total = 0

    while(nfe<max_int):
        print('Interação: {}'.format(nfe))
        print('Valor f(x): {}'.format(y))
        sys.stdout.flush()
        start = time.time()
        k = 1
        while(k<=k_max):
            #print('k: {}; f(x): {}'.format(k,y))
            # Gera uma solução na k-esima vizinhança de x
            dados_line = shake(copy.copy(dados),k) #shaking
            dados_line_line = bestImprovement(copy.copy(dados_line), f, e)
            #update x
            dados, k = neighborhoodChange(copy.copy(dados), copy.copy(dados_line_line), k, f, e)
            #save 
            y = f(dados, e)
            #update log
            n_ap.append(np.sum(dados['ap']))

        y_save.append(y)
        rest3_save.append(rest3(dados))
        rest4_save.append(rest4(dados))
        rest5_save.append(rest5(dados))
        rest6_save.append(rest6(dados))
        rest7_save.append(rest7(dados))
        

        if plot and nfe % n_plot == 0:
            log = [y_save, rest3_save, rest4_save, rest5_save, rest6_save, rest7_save, n_ap]
            plot_infos(dados, log, dir_save+'/info/', str(nfe))
            save_dic = {'cc':dados['cc'], 
                        'ap':dados['ap'],
                        'acp':dados['acp'],
                        'd':dados['d'],
                        'grid':dados['grid'],
                        'sizex':dados['sizex'],
                        'sizey':dados['sizey']}

            with open(dir_save+'/file_save/pw_'+str(nfe)+'.pkl', 'wb') as handle:
                pickle.dump(save_dic, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        end = time.time()
        _time_exec = (end - start)/60
        time_total += _time_exec
        nfe +=1

    return dados, [y_save, rest3_save, rest4_save, rest5_save, rest6_save, rest7_save, n_ap], time_total

#f1 principal
def pe_f1(dados,e):
    fob = f1(dados) + max(0,(f2(dados)-e))**2 
    return fob

#f2 principal
def pe_f2(dados,e):
    fob = f2(dados) + max(0,(f1(dados)-e))**2 
    return fob

def problemaPe(dados, main, n_sol, k_max, max_VNS_it, plot = True, dir_save = './'):
    dados_init = initialSol(copy.copy(dados))
    fval = np.zeros((n_sol, 2))

    #decide qual funcão usar como principal
    if main == 'f1':
        pe = pe_f1
    else:
        pe = pe_f2

    for i in range(0,n_sol):
        print('\nExecução {}\n'.format(i+1))
        
        e = randrange(969496, 1052924)

        print('epsilon  = {}\n'.format(e))

        dados_res, log, time_total = BVNS(copy.copy(dados_init), pe, e, k_max, max_VNS_it, plot = False)
        fval[i,0]=f1(dados_res)
        fval[i,1]=f2(dados_res)

        #print solution
        print('[Resultado] VNS - PW:')
        print('Numero de Pontos de acesso: {}'.format(log[6][-1]))
        print('Valor de y: {}'.format(log[0][-1]))
        print('Valor de Rest3: {:.2f}'.format(log[1][-1]))
        print('Valor de Rest4: {:.2f}'.format(log[2][-1]))
        print('Valor de Rest5: {:.2f}'.format(log[3][-1]))
        print('Valor de Rest6: {:.2f}'.format(log[4][-1]))
        print('Valor de Rest7: {:.2f}'.format(log[5][-1]))
        print('\ntempo total da execução {}: {:.2f} hora(s)'.format(i+1,time_total/60))
        print('--------------------------------------------')
        #print(sol['acp'])
        sys.stdout.flush()
        #plot solution
        if plot:
            #plot_infos(dados_res, log, dir_=dir_save+'info/')
            
            save_dic = {'cc':dados_res['cc'], 
                        'ap':dados_res['ap'],
                        'acp':dados_res['acp'],
                        'd':dados_res['d'],
                        'grid':dados_res['grid'],
                        'sizex':dados_res['sizex'],
                        'sizey':dados_res['sizey'],
                        'fval': fval}
        
            with open(dir_save+'/file_save/pe_'+main+'_'+str(i+1)+'.pkl', 'wb') as handle:
                pickle.dump(save_dic, handle, protocol=pickle.HIGHEST_PROTOCOL)



if __name__ == "__main__":


    if len(sys.argv) > 2:
        path_file = sys.argv[1]
        n_sol = int(sys.argv[2])
        k_max = int(sys.argv[3])
        max_int_vns = int(sys.argv[4])
        v_grid = int(sys.argv[5])
        n_plot = int(sys.argv[6])
        mainf = sys.argv[7]
    else:
        path_file = '../clientes_debug.csv'
        n_sol = 10
        k_max = 4
        max_int_vns = 5
        v_grid = 80
        n_plot = 4
        mainf = 'f2'
    
    print('File: {}'.format(path_file))
    print('n_sol: {}'.format(n_sol))
    print('k_max: {}'.format(k_max))
    print('max interações: {}'.format(max_int_vns))
    print('Grid {}x{}'.format(v_grid,v_grid))
    print('Função Principal: {}'.format(mainf))

    df = pd.read_csv(path_file)
    value = df.values
    #Inicializa variáveis
    #(0,805)
    sizex = (0,800)
    sizey = (0,800)
    #5x5
    grid = (v_grid,v_grid)
    n_P = int((sizex[1]*sizey[1])/ (grid[0]*grid[1]))
    C = value[:,:2] #conjunto de clientes (x,y)
    cc = value[:,2:] #consumo do cliente i
    #setar valores dos grides como (x,y) ou como x e y separados
    P =  np.zeros((n_P, 2))#conjunto de pontos(x,y) de possiveis locais para AP
    cp = 150 #capacidade do ponto de acesso p
    rp = 85 # limite do sinal do ponto de acesso
    N = 0.95 # taxa de cobertura dos clientes
    n_max = 100 #numero maximo de PAs disponiveis
    ap = np.zeros(len(P)) # vetor len == numero de PAs e binario para indicar se a PA é usada ou nao
    #acp = np.zeros((int(C.shape[0]), n_max))
    d = np.zeros((len(C), len(P))) #vetor de distacias
    acp = np.zeros((len(C), len(P)))#Matriz de numero de clientes por numero de PAs indica se a PA é utilizada pelo cliente

    x = {
        'd':d,
        'C': C,
        'cc': cc.reshape(-1,),
        'P': P,
        'cp': cp,
        'rp': rp,
        'N': N,
        'n_max': n_max,
        'ap': ap,
        'acp': acp,
        'grid':grid,
        'sizex':sizex,
        'sizey':sizey
    }

    #Otimizando
    problemaPe(x, mainf, n_sol = n_sol, k_max = k_max, max_VNS_it = max_int_vns, plot = bool(n_plot), dir_save='output/pe/'+mainf)

    print('\n\n=====================Finish Execution=================\n\n')
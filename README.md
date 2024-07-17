## Projeto de otimização de pontos de acesso em uma área - Engenharia de Sistemas
### Autores: Mateus Simonetti (2019057004) e Vitor Oliveira (2019057217)



### Solução do problema mono-objetivo

Implementação mono-objetivo utilizando BVNS (basicvns.py)\
Exemplo para rodar o código:\
\
python mop_solution/1_entrega_revisada/basicvns.py clientes.csv 4 20 10 f1

- Parametro     : significado\
mop_so...ns.py  : (string) Caminho dos arquivos desejados;\
clientes.csv    : (string) diretório do arquivo com detalhes dos clientes;\
4               : (int) k_max, parametro do método bvns que indica número de estruturas utilizadas;\
20              : (int) valor máximo de interações;\
10              : (int) parâmetro relativo à forma do plot. Pode ser passado apenas 10;\
f1              : (string) indicativo de qual função será chamada: f1 (otimização do número de PAs) ou f2 (otimização de distância total)

### Solução do problema bi-objetivo

Implementação do PW (arquivo pw) e do PE (arquivo pe) a partir do BVNS\
\
Exemplo para rodar o código PW: python mop_solution/pw/basicvns.py clientes.csv 4 3 10 f
Exemplo para rodar o código PW: python mop_solution/pe/basicvns.py clientes.csv 4 3 10 f

- Parametro     : significado\
mop_so...ns.py  : (string) Caminho dos arquivos desejados;\
clientes.csv    : (string) diretório do arquivo com detalhes dos clientes;\
4               : (int) k_max, parametro do método bvns que indica número de estruturas utilizadas;\
100             : (int) valor máximo de interações;\
80              : (int) parâmetro relativo à forma do plot. Pode ser passado apenas 10;\
f              : (string) indicativo de que serão otimizadas ambas funções

### Pontos da revisão relativos à primeira entrega
- Performance em relação ao tempo de execução:
    * Tempo necessário para a execução do código diminuiu drasticamente, permitindo mais testes e debugging facilitado.

- Restrições implementadas e resposta sempre factível:
    * Restrição relativa à exposição de cada usuário aos PAs alocados foi implementada (r9, em restricoes.py).
    * Agora, todas as soluções encontradas respeitam todas as restrições.

- Novas estruturas de vizinhança:
    * Além das que já existiam, foram adicionadas outras 5 estruturas de vizinhança (k5, k6, k7, k8 e k9, disponíveis em estrutura_vizinhanca.py). 
    * Possibilidade de testar ambas as funções com diversas configurações.

- Realocação de clientes priorizada e aleatória:
    * Implementação de função que realoca os clientes, garantindo que toda realocação respeite as restrições devidas
    * Implementação de três lógicas de priorização de PAs para que os clientes se conectem:
        -> Priorização por PA mais próximo (calcular_dist_ord_cliente_PAs, disponível em estrutura_vizinhanca.py)
        -> Priorização por PA com mais pessoas no seu raio de ação (calcular_popularidade_ord_cliente_PAs, disponível em estrutura_vizinhanca.py)
        -> Sem priorização (adicionar_indices, disponível em estrutura_vizinhanca.py)

- Logs e tratativas de exceção:
    * Adicionados logs para verificação do funcionamento de funções-chave, facilitando debugging
    * Adicionadas verificações que garantem que, devido a algum cenário que não foi mapeado ou não pôde ser simulado, a execução quebre




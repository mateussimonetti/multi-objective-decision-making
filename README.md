## Projeto do componente curricular Teoria da Decisão da UFMG - Escola de Engenharia - Engenharia de Sistemas
### Problema de posicionamento de pontos de acesso de internet sem fio

![Execução](https://github.com/jesimonbarreto/TeoriaDecisao/blob/main/iterationss.gif?raw=true)




### Solução do problema mono-objetivo

Implementação com BVNS (bvns.py)\
Exemplo para rodar o código:\
\
python mono_obj/bvns.py clientes.csv 1 4 100 80 10

- Parametro     : significado\
clientes.csv    : (string) diretório do arquivo com detalhes dos clientes;\
1               : (int) parametro não utilizado nessa versão;\
4               : (int) k_max, parametro do método bvns;\
100             : (int) valor máximo de interações;\
80              : (int) tamanho do grid usado para os pontos de acesso (distancia entre os pontos de acesso);\
10              : (int) intervalo de interações para salvar (solução e plot) - 0 para não salvar.

### Solução do problema bi-objetivo

Implementação do PW (pw_code.py) e do PE (pe_code.py) a partir do BVNS\
\
Exemplo para rodar o código PW:\
\
python multi_obj/pw_code.py clientes.csv 10 4 100 80 10

- Parametro     : significado\
clientes.csv    : (string) diretório do arquivo com detalhes dos clientes;\
10              : (int) parametro para definir quantidade de soluções calculadas com w diferentes;\
4               : (int) k_max, parametro do método bvns;\
100             : (int) valor máximo de interações;\
80              : (int) tamanho do grid usado para os pontos de acesso (distancia entre os pontos de acesso);\
10              : (int) intervalo de interações para salvar (solução e plot) - 0 para não salvar.


Exemplo para rodar o código PE:\
\
python multi_obj/pe_code.py clientes.csv 10 4 100 80 10 f1

- Parametro: significado\
clientes.csv    : (string) diretório do arquivo com detalhes dos clientes;\
10              : (int) parametro para definir quantidade de soluções calculadas com w diferentes;\
4               : (int) k_max, parametro do método bvns;\
100             : (int) valor máximo de interações;\
80              : (int) tamanho do grid usado para os pontos de acesso (distancia entre os pontos de acesso);\
10              : (int) intervalo de interações para salvar (solução e plot) - 0 para não salvar;\
f1              : (string) indica qual função será utilizada como principal, as outras serão restrições (possibilidades: f1 ou f2)


### Decisão da melhor solução
 - [Adicionar]

### Detalhes da saída

- Os arquivos de solução dos métodos são direcionados para pasta output/[nome_metodo]/file_save
- Os plots são direcionados para output/[nome_metodo]/info
- Estrutura da saída (dict.pickle):

- Key   : significado\
'cc'    : consumo do cliente i;\
'ap'    : vetor binario para indicar se a PA é usada;\
'acp'   : matrix binaria (clientesxPA) que indica se a PA atende ao cliente;\
'd'     : vetor de distacias;\
'grid'  : espaço entre as PAs;\
'sizex' : domínio de busca X;\
'sizey' : domínio de busca Y;

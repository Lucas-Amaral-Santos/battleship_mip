"""
Solving battleship problem using MIP
Aluno Lucas Amaral
Programação Linear Inteira

Artigo:

Meuffels, W. J. M., & den Hertog, D. (2010). Solving the Battleship puzzle as an integer programming problem.
INFORMS Transactions on Education, 10(3), 156-162.
    
https://research.tilburguniversity.edu/en/publications/7cd77b04-eb53-4e21-9d4b-670cd414658c


CELL-BASED MODEL
"""

from mip import Model, xsum, minimize, BINARY

"""======================================================================
                DADOS DO PROBLEMA
======================================================================="""

""" -------------------------------------------------------------------------
                   Instância 1
 -------------------------------------------------------------------------"""

"""
# O tamanho do tabuleiro é 15x10
# Número de linhas I = 15
# Número de colunas J = 10 """
I, J = 15, 10

"""
 Cada um tem a soma de linha e coluna, respectivamente, que indica 
 quantos navios estão presentes em cada linha e coluna. """
R = [2, 1, 2, 0, 2, 0, 7, 1, 6, 1, 2, 2, 5, 2, 2]
C = [4, 4, 3, 3, 5, 2, 3, 3, 1, 7]



grid = [[None for j in range(J)] for i in range(I)]
grid[0][4] = 0
grid[0][8] = 0
grid[2][3] = 2
grid[4][1] = 0
grid[4][6] = 6
grid[4][8] = 0
grid[6][9] = 0
grid[8][4] = 0
grid[8][7] = 0
grid[8][9] = 5
grid[10][1] = 0
grid[12][7] = 0
grid[14][7] = 2

"""
Tipos de células:
  água -> 0
  <    -> 1
  >    -> 2
  ^    -> 3
  v    -> 4
  #    -> 5
  o    -> 6
"""
k = [0, 1, 2, 3, 4, 5, 6]

"""
Número de cada navio  
  índice 0: submarine -> 5
  índice 1: destroyer -> 4
  índice 2: cruiser -> 3
  índice 3: battleship -> 2
  índice 4: carrier -> 1
"""
S = [i for i in reversed(range(1, 6))]

# T = [0 if grid[i][j] is None else grid[i][j] for i in range(I) for j in range(J)]

"""
Conjunto de navios
consiste em todos os navios enumerados com a qual cada número representa o tamanho do navio. 
Por exemplo, 1 representa um navio de tamanho 1, 2 representa um navio de tamanho 2 e assim por diante.
"""

model = Model("modelo batalha naval baseado em células")



"""
Adicionar as variáveis ao modelo

Variáveis de decisão:   
 x_{i, j, k} = 1 se a célula (i, j) contém o tipo de célula k, 0 caso contrário.
 s_{i,j,l} = 1 se o navio de tamanho l começa na célula (i, j), 0 caso contrário.
"""
x = [[[model.add_var(var_type=BINARY) for k in range(7)] for j in range(J)] for i in range(I)]
s = [[[model.add_var(var_type=BINARY) for l in range(1, 6)] for j in range(J)] for i in range(I)] 



"""
Função objetiva
Não possui
"""

"""
RESTRIÇÕES DO PROBLEMA

Restrição 1: 
Cada célula do tabuleiro deve ser ocupada por um dos 7 símbolos.
Se a célula não contém um pedaço do navio, contém água. 
"""

for i in range(I):
    for j in range(J):
        model += xsum(x[i][j][k] for k in range(7)) == 1

"""
Restrição 2:
Se a uma célula é associada a um simbolo, este simbolo não pode ser modificado ou acompanhado por outro simbolo.
Por exemplo, se a célula (i, j) contém o símbolo '<', então não pode conter o símbolo '>' ou qualquer outro símbolo.
"""
for i in range(I):
    for j in range(J):
        if grid[i][j] is not None:
            model += x[i][j][grid[i][j]] == 1

"""
Restrição 3 e 4:
A soma das células que contém pedaços de navio na linha i da grid final deve ser 
igual a soma_linha[i] e a soma das células que contém pedaços de navio na coluna j 
da grid final deve ser igual a soma_coluna[j].
"""
for i in range(I):
    model += xsum(x[i][j][k] for j in range(J) for k in range(1,7)) == R[i]
for j in range(J):
    model += xsum(x[i][j][k] for i in range(I) for k in range(1,7)) == C[j]

"""
Restrição 5:
Força que se um célula (i,j) tem uma navio de comprimento 1, s[i,j,1] tem que ser igual a 1,
e 0 caso contrário.
"""
for i in range(I):
    for j in range(J):
        model += s[i][j][0] == x[i][j][6]

"""
Restrição 6:
Se uma célula (i,j) contém a primeira peça de um navio (< e ^) de tamanho != 1, então s[i, j, l] é igual a 1.
"""
for i in range(I):
    for j in range(J):
        for l in range(2, 6):
            cabe_h = j + l - 1 < J
            cabe_v = i + l - 1 < I
            model += l*s[i][j][l-1] <= x[i][j][1] + (x[i][j+l-1][2] if cabe_h else 0) \
                + xsum(x[i][c][5] for c in range(j+1, min(j+l-1, J))) \
                + x[i][j][3] + (x[i+l-1][j][4] if cabe_v else 0) \
                + xsum(x[r][j][5] for r in range(i+1, min(i+l-1, I)))
            
"""
Restrição 7:
Força que a soma dos navios do comprimento l na grid final é igual ao número requerido de navios de 
comprimento l que tem que ser alocados. Os navios podem ser colocados horizontalmente ou verticalmente.
"""
for l in range(1, 6):
    model += xsum(s[i][j][l-1] for i in range(I) for j in range(J)) == S[l-1]

"""
Restrição 8:

"""
for i in range(I-1):
    for j in range(J-1):
        model += xsum(x[i][j][k] for k in range(1, len(k))) + xsum(x[i+1][j+1][k] for k in range(1, len(k))) <= 1

"""
Restrição 9:

"""
for i in range(1,I):
    for j in range(J-1):
        model += xsum(x[i][j][k] for k in range(1, len(k))) + xsum(x[i-1][j+1][k] for k in range(1, len(k))) <= 1


"""
Restrição 10:

"""
for i in range(I):
    for j in range(J-1):
        model += x[i][j][1] <= x[i][j+1][2] + x[i][j+1][5]
    model += x[i][J-1][1] == 0

"""
Restrição 11:

"""
for i in range(I):
    for j in range(1,J):
        model += x[i][j][1] <= x[i][j-1][0]

"""
Restrição 12:

"""
for i in range(I):
    for j in range(J-1):
        model += x[i][j][2] <= x[i][j+1][0]

"""
Restrição 13:
 '>' precisa de '<' ou meio à esquerda

"""
for i in range(I):
    for j in range(1, J):
        model += x[i][j][2] <= x[i][j-1][1] + x[i][j-1][5]
    model += x[i][0][2] == 0

"""
Restrição 14:
'^' precisa de 'v' ou meio embaixo
"""
for i in range(I-1):
    for j in range(J):
        model += x[i][j][3] <= x[i+1][j][4] + x[i+1][j][5]
for j in range(J):
    model += x[I-1][j][3] == 0

        

"""
Restrição 15:

"""
for i in range(1, I):
    for j in range(J):
        model += x[i][j][3] <= x[i-1][j][0]

"""
Restrição 16:

"""
for i in range(I-1):
    for j in range(J):
        model += x[i][j][4] <= x[i+1][j][0]

"""
Restrição 17:

"""
for i in range(1, I):
    for j in range(J):
        model += x[i][j][4] <= x[i-1][j][3] + x[i-1][j][5]
for j in range(J):
    model += x[0][j][4] == 0


"""
Restrição 18, 19, 20, 21:
meio precisa de navio em cima E embaixo, ou à esquerda E à direita

"""
for i in range(I):
    for j in range(J):
        cima  = x[i-1][j][3] + x[i-1][j][5] if i > 0   else 0
        baixo = x[i+1][j][4] + x[i+1][j][5] if i < I-1 else 0
        esq   = x[i][j-1][1] + x[i][j-1][5] if j > 0   else 0
        dir   = x[i][j+1][2] + x[i][j+1][5] if j < J-1 else 0

        model += x[i][j][5] <= cima + dir
        model += x[i][j][5] <= cima + esq
        model += x[i][j][5] <= baixo + esq
        model += x[i][j][5] <= baixo + dir

"""
Restrição 22:

"""
for i in range(I):
    for j in range(1, J):
        model += x[i][j][6] <= 1 - x[i][j-1][6]

"""
Restrição 23:

"""
for i in range(1, I):
    for j in range(J):
        model += x[i][j][6] <= 1 - x[i-1][j][6]

"""
Restrição 24:

"""
for i in range(I):
    for j in range(J):
        for k_i in k:
            x[i][j][k_i]



status = model.optimize()
print(status)

simbolo = {0: '.', 1: '<', 2: '>', 3: '^', 4: 'v', 5: '#', 6: 'o'}

if model.num_solutions:
    for i in range(I):
        linha = ''
        for j in range(J):
            for k in range(7):
                if x[i][j][k].x >= 0.99:
                    linha += simbolo[k] + ' '
        print(linha, ' ', R[i])
    print(' '.join(str(c) for c in C))
else:
    print('Nenhuma solução encontrada')



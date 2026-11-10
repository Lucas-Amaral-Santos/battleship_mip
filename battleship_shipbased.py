"""
Solving battleship problem using MIP
Aluno Lucas Amaral
Programação Linear Inteira

Artigo:

Meuffels, W. J. M., & den Hertog, D. (2010). Solving the Battleship puzzle as an integer programming problem.
INFORMS Transactions on Education, 10(3), 156-162.
    
https://research.tilburguniversity.edu/en/publications/7cd77b04-eb53-4e21-9d4b-670cd414658c


SHIP-BASED MODEL
"""

from mip import Model, xsum, minimize, maximize, BINARY, INTEGER

"""======================================================================
                DADOS DO PROBLEMA
======================================================================="""

"""
Conjunto de grids que coontém UM navio de tamanho l
"""
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


"""
PRÉ PROCESSAMENTO
Defininição de parâmetros

M_{i,j} = 1 se a célula (i,j) contém um pedaço do navio na grid inicial, 0 se contém água, 100 se nenhuma das duas.
    G_{i,j,g} = 1 se a célula (i,j) contém um pedaço do navio na grid com enumeração g.
    P_{i,j,g} = 1, se as células (i,j), (i, j+1), (i+1, j), (i+1, j+1) da grid g contém a peça do navio, e é 0 caso contrário.
        Ou seja,
            P_{i,j,g} = 1           se      G_{i,j,g} = 1   G_{i,j+1,g} =1
                                            G_{i+1,j,g}=1   G_{i+1, j+1,g}=1 
"""
def papel(c, i, j):
    L = len(c); p = c.index((i, j))
    if L == 1:
        return 6
    horiz = c[0][0] == c[-1][0]
    if p == 0:
        return 1 if horiz else 3
    if p == L - 1:
        return 2 if horiz else 4
    return 5

def compativel(c):
    for (i, j) in c:
        t = grid[i][j]
        if t == 0:
            return False
        if t is not None and papel(c, i, j) != t:
            return False
    return True

celulas = []                          
grids = {l: [] for l in range(1, 6)}  

for l in range(1, 6):                 
    for i in range(I):
        for j in range(J):
            candidatos = []
            if j + l - 1 < J:
                candidatos.append([(i, j + c) for c in range(l)])   # horizontal
            if l > 1 and i + l - 1 < I:
                candidatos.append([(i + r, j) for r in range(l)])   # vertical
            for c in candidatos:
                if compativel(c):
                    grids[l].append(len(celulas))
                    celulas.append(c)

N = len(celulas)


M = [[100 if grid[i][j] is None else (0 if grid[i][j] == 0 else 1)
      for j in range(J)] for i in range(I)]


G = [[[0 for g in range(N)] for j in range(J)] for i in range(I)]
for g in range(N):
    for (i, j) in celulas[g]:
        G[i][j][g] = 1

P = [[[0 for g in range(N)] for j in range(J-1)] for i in range(I-1)]

for g in range(N):
    for i in range(I-1):
        for j in range(J-1):
            if G[i][j][g] == 1 or G[i][j+1][g] == 1 or G[i+1][j][g] == 1 or G[i+1][j+1][g] == 1:
                P[i][j][g] = 1



model = Model("modelo batalha naval baseado em navio")

"""
Adicionar as variáveis ao modelo

Variáveis de decisão:   
    
"""
y = [model.add_var(var_type=BINARY) for g in range(N)]

"""
            RESTRIÇÕES
"""

"""
Restrição 1 e 2:
Requer que a soma das células que contém um pedaço da navio na linha i(coluna j) é igual ao numero requerido de células que 
é necessário ter o pedaço de navio na linha i(coluna j).
"""

for i in range(I):
    model += xsum(y[g] * G[i][j][g] for g in range(N) for j in range(J)) == R[i]

for j in range(J):
    model += xsum(y[g] * G[i][j][g] for g in range(N) for i in range(I)) == C[j]

"""
Restrição 3:
Força que a soma dos navios de comprimento l na grid final é igual ao numero requerido de navios de comprimento l
que tem que ser colocado na grid.
"""
for l in range(1,6):
    model += xsum(y[g] for g in grids[l]) == S[l-1]

"""
Restrição 4:
Assegura que nenhuma grid que não pode ser usada concomitantemente é usada na grid final.
Duas grids não podem ser usadas juntas se os navios encostam um no outro horizontalmente, verticalmente.
E também não podem se cruzar.
"""

for i in range(I-1):
    for j in range(J-1):
        model += xsum(P[i][j][g] * y[g] for g in range(N)) <= 1

"""
Restrição 5:
A grid inicial tem um pedaço de navio em uma célula, a grid final também tem que ter
esse navio na grid final. Assim como água.
"""
for i in range(I):
    for j in range(J):
        if M[i][j] == 0 or M[i][j] == 1:
            model += xsum(y[g]*G[i][j][g] for g in range(N)) == M[i][j]


status = model.optimize()
print(status)

simbolo = {1: '<', 2: '>', 3: '^', 4: 'v', 5: '#', 6: 'o'}

if model.num_solutions:
    tab = [['.' for j in range(J)] for i in range(I)]
    for g in range(N):
        if y[g].x >= 0.99:
            for (i, j) in celulas[g]:
                tab[i][j] = simbolo[papel(celulas[g], i, j)]

    for i in range(I):
        print(' '.join(tab[i]), ' ', R[i])
    print(' '.join(str(c) for c in C))
else:
    print('Nenhuma solução encontrada')


""" guarda a primeira solução """
ybar = [1 if y[g].x >= 0.99 else 0 for g in range(N)]

""" unicidade """
model.objective = maximize(
    - xsum(y[g] for g in range(N) if ybar[g] == 1)
    + xsum(y[g] for g in range(N) if ybar[g] == 0)
)

model.optimize()
print('Valor ótimo:', model.objective_value)

if model.objective_value <= -sum(ybar) + 0.5:
    print('Solução única')
else:
    print('Existe outra solução')
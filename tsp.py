from mip import Model, xsum, minimize, BINARY
from sys import stdout as out
from itertools import product

# Nome de lugares para visitar
places = ['Antwerp', 'Bruges', 'C-Mine', 'Dinant', 'Ghent',
          'Grand-Place de Bruxelles', 'Hasselt', 'Leuven',
          'Mechelen', 'Mons', 'Montagne de Bueren', 'Namur',
          'Remouchamps', 'Waterloo']

# Distâncias em uma upper triangular matrix (em km)
dists = [[83, 81, 113, 52, 42, 73, 44, 23, 91, 105, 90, 124, 57],
         [161, 160, 39, 89, 151, 110, 90, 99, 177, 143, 193, 100],
         [90, 125, 82, 13, 57, 71, 123, 38, 72, 59, 82],
         [123, 77, 81, 71, 91, 72, 64, 24, 62, 63],
         [51, 114, 72, 54, 69, 139, 105, 155, 62],
         [70, 25, 22, 52, 90, 56, 105, 16],
         [45, 61, 111, 36, 61, 57, 70],
         [23, 71, 67, 48, 85, 29],
         [74, 89, 69, 107, 36],
         [117, 65, 125, 43],
         [54, 22, 84],
         [60, 44],
         [97],
         []]

# Números de nós e lista de vértices
n, V = len(dists), set(range(len(dists)))

# Matriz de distâcias
# (transformando a upper triangular matrix em uma matriz completa)
c = [[
    0 if i == j
    else dists[i][j-i-1] if j > i
    else dists[j][i-j-1]
    for j in V] for i in V]

# Define o modelo
model = Model('TSP')

# Variáveis binárias indicando que se o arco (i,j) é usado na rota ou não
x = [[model.add_var(var_type=BINARY) for j in V] for i in V]

# variável contínua para prevenir subciclos: cada cidade terá um número sequencial associado 
# a ela, exceto a cidade inicial.
y = [model.add_var() for i in V]

# Função objetiva
model.objective = minimize(xsum(c[i][j] * x[i][j] for i in V for j in V))

# Restrição: sair de cada cidade apenas uma vez
for i in V:
    model += xsum(x[i][j] for j in V - {i}) == 1

# Restrição: entrar em cada cidade apenas uma vez
for i in V:
    model += xsum(x[j][i] for j in V - {i}) == 1

# Eliminação de subciclos: se a cidade i é visitada antes da cidade j, então y[i] < y[j]
## O operador de produto cartesiano é usado para gerar todos os pares de cidades (i,j) possíveis,
## exceto a cidade inicial (0). A restrição garante que, se o arco (i,j) é usado na rota (ou seja, x[i][j] = 1),
## então a cidade i deve ser visitada antes da cidade j (ou seja, y[i] < y[j]). 
# A constante n é usada para garantir que a diferença entre y[i] e y[j] seja suficientemente grande para evitar subciclos.
# A conta é y[i] - y[j] + n * x[i][j] <= n - 1, que garante que se x[i][j] = 1, então y[i] < y[j].
for (i,j) in product (V - {0}, V - {0}):
    if i != j:
        model += y[i] - (n+1)*x[i][j] >= y[j]-n


# Otimização do modelo
model.optimize()

# Checar se a solução foi encontrada
if model.num_solutions:
    # Imprimir a distância total da rota
    print('rota com distância total %g encontrada: %s' % (model.objective_value, places[0]), end='')

    # Imprimir a rota
    nc = 0
    while True:
        nc = [i for i in V if x[nc][i].x >= 0.99][0]
        print(' -> %s' % places[nc], end='')
        if nc == 0:
            break
    print()
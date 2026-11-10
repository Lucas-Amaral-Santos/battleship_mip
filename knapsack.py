from mip import Model, xsum, maximize, BINARY

# Dados ====================================
p = [10, 13, 18, 31, 7, 15]
w = [11, 15, 20, 35, 10, 33]
c, I = 47, range(len(w))
# =========================================
# 

# Definindo o modelo
m = Model("knapsack")

# x_i é uma variável binária que indica se o item i é selecionado ou não
x = [m.add_var(var_type=BINARY) for i in I]

# Essa é a funçõao objetivo do problema
### A função vai maximizar a soma dos valores dos itens selecionados, ponderados 
### pelos seus respectivos lucros p[i]. A função xsum é usada para somar os produtos 
### p[i] * x[i] para todos os itens i em I. O objetivo é encontrar a combinação de 
### itens que maximize o lucro total sem exceder a capacidade da mochila c.
m.objective = maximize(xsum(p[i] * x[i] for i in I))

# Restrição de capacidade da mochila
### A restrição garante que a soma dos pesos dos itens selecionados não exceda a
### capacidade da mochila c. A função xsum é usada para somar os produtos w[i] * x[i]
### para todos os itens i em I. Se a soma dos pesos dos itens selecionados for
### maior que a capacidade da mochila, a solução não será viável.

### No mip, o operador += é usado para adicionar a restrição ao modelo. 
### A expressão xsum(w[i] * x[i] for i in I) calcula o peso total dos itens selecionados, 
### e a restrição garante que esse peso total seja menor ou igual à capacidade da mochila c.
m += xsum(w[i] * x[i] for i in I) <= c

# Chamada do solver para resolver o problema
m.optimize()

# Extratir os índices dos itens selecionados na solução ótima
selected = [i for i in I if x[i].x >= 0.99]
print("selected items: {}".format(selected))



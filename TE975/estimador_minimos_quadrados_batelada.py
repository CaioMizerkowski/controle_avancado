# Estimador dos mínimos quadrados não-recursivo (em batelada)
# Processo de segunda ordem (2 pólos e 2 zeros)
#Bibliotecas usadas
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sb

#Importa um arquivo com os dados de saída
with open('aula_03.csv','r') as f:
    data = np.loadtxt(f,delimiter=',')
    
print('Método dos mínimos quadrados em batelada')
npts = data.size # O número de pontos existentes
u = np.arange(npts) # Como os dados são sequênciais, é gerado uma sequência de números
y = data # Salva os dados de saídas
print(f'Número de pontos: {npts}')

phi = np.ones([npts,4]) # Inicia a matriz Phi para 4 parametros
for j in range(npts): # Loop para preencher a matriz Phi
    if j <= 2:
        y1 = y[0]
        y2 = y[0]
        u1 = 0
        u2 = 0
    else:
        y1 = y[j-1]
        y2 = y[j-2]
        u1 = u[j-1]
        u2 = u[j-2]
    phi[j] = [-y1,-y2,u1,u2]
 
theta = np.linalg.inv(phi.T.dot(phi)).dot(phi.T).dot(y) # Calcula os parametros através de operações matriciais
numparametros = theta.shape[0]
print(f'Número de parâmetros estimados (na + nb): {numparametros}')

# Printa os parametros estimados
for i in range(numparametros):
    print(f'theta({i}) = {theta[i]}')

# Inicia a matriz de valores n passos a frente para ser preenchida
yest_n = np.ones(npts)
yest_n[:2] = y[:2] # Preenche os dois pontos iniciais
yest_1 = yest_n.copy() # Cria uma copia da matriz

# Theta e seus respectivos valores
a1=theta[0]
a2=theta[1]
b1=theta[2]
b2=theta[3]

# A partir do segundo ponto, calcula o valor da saída conforme os parametros estimados
for t in range(2,npts):
    # Previsão de n passos a frente
    yest_n[t] = -a1*yest_n[t-1]-a2*yest_n[t-2]+b1*u[t-1]+b2*u[t-2]
    # Previsão de um passo a frente
    yest_1[t] = -a1*y[t-1]-a2*y[t-2]+b1*u[t-1]+b2*u[t-2]

# Mean Squared Error (MSE) – objetivo é um menor MSE
MSE_1 = np.sum((y-yest_1)**2)/(npts-2)
MSE_n = np.sum((y-yest_n)**2)/(npts-2)

print(f'MSE_1: {MSE_1}')
print(f'MSE_n: {MSE_n}')

# Plota a figura
plt.figure(figsize = (15,15))
sb.scatterplot(x=u,y=y,color='green',markers='.')
sb.lineplot(x=u,y=yest_1,color='red',linestyle='--')
sb.lineplot(x=u,y=yest_n,color='blue',linestyle='--')
plt.title(f'Desempenho do modelo\nMSE_1: {MSE_1}\nMSE_n: {MSE_n}')
plt.legend(labels=["Real","Um passo a frente","N passos a frente"])
plt.xlabel('Amostra')
plt.ylabel('Saída')
plt.show()
plt.close()
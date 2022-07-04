import numpy as np

def gerar_phi(na, nb, u, y, delay=1):
    numparametros = na+nb
    npts = u.size
    phi = np.ones([npts, numparametros]) # Inicia a matriz Phi para na+nb parametros

    for j in range(npts): # Loop para preencher a matriz Phi
        new_phi = []
        for i in range(1,na+1):
            new_phi.append(-y[max(j-i,0)])
        for i in range(delay,nb+delay):
            new_phi.append(u[max(j-i,0)])
        phi[j] = new_phi

    return phi

def gerar_coeficientes(na, nb, u, y, delay=1):
    phi = gerar_phi(na, nb, u, y, delay)
    
    theta = np.linalg.inv(phi.T.dot(phi)).dot(phi.T).dot(y) # Calcula os parametros através de operações matriciais
    return theta

# Usado para o debug, importante para conferir se os atrasos estão corretos
def gerar_index_phi(na, nb, size, delay):
    numparametros = na+nb
    npts = size
    index_phi = np.ones([npts, numparametros]) # Inicia a matriz Phi para na+nb parametros

    for t in range(npts): # Loop para preencher a matriz Phi
        new_phi = []
        for i in range(1,na+1):
            new_phi.append(max(t-i,0))
        for i in range(delay,nb+delay):
            new_phi.append(max(t-i,0))
        index_phi[t] = new_phi

    return index_phi

def gerar_yest_n(na, nb, u, y, theta, delay=0):
    # Inicia a matriz de valores n passos a frente para ser preenchida
    numparametros = na+nb
    npts = u.size
    yest_n = np.ones(npts)*y[0]

    # A partir do n ponto, calcula o valor da saída conforme os parametros estimados
    yest_u_z = np.ones(numparametros)
    for t in range(npts):
        for i in range(na):
            yest_u_z[i] = -yest_n[max(t-i-1,0)]

        for i in range(nb):
            yest_u_z[i+na] = u[max(t-i-delay,0)]

        yest_n[t] = np.sum(theta*yest_u_z)
    return yest_n

def gerar_yest_1(na, nb, u, y, theta, delay=0):
    # Inicia a matriz de valores 1 passo a frente para ser preenchida
    numparametros = na+nb
    npts = u.size
    yest_1 = np.ones(npts)*y[0]

    # Calcula o valor da saída para o próximo passo conforme os parametros estimados
    yest_u_z = np.ones(numparametros)

    for t in range(npts):
        for i in range(na):
            yest_u_z[i] = -y[max(t-i-1,0)]

        for i in range(nb):
            yest_u_z[i+na] = u[max(t-i-delay,0)]

        # Previsão de um passo a frente
        yest_1[t] = np.sum(theta*yest_u_z)
    return yest_1

def gerar_dados(na, nb, u, y, delay=1):
    theta = gerar_coeficientes(na, nb, u, y, delay)
    yest_n = gerar_yest_n(na, nb, u, y, theta, delay)
    yest_1 = gerar_yest_1(na, nb, u, y, theta, delay)
    return theta, yest_1, yest_n

def lsqr_batelada(na, nb, u, y, delay=1):
    theta = gerar_coeficientes(na, nb, u, y, delay)
    yest_1 = gerar_yest_1(na, nb, u, y, theta, delay)
    return theta, yest_1

def gerar_mse(na, nb, u, y, delay):
    yest_1, yest_n = gerar_dados(na, nb, u, y, delay)
    deep = max(na, nb)
    npts = u.size

    MSE_1 = np.sum((y-yest_1)**2)/(npts-deep)
    MSE_n = np.sum((y-yest_n)**2)/(npts-deep)
    return MSE_1, MSE_n

def comparar_mse(u, y, rna, rnb, delay, p=False):
    MSE_1_array = []
    i = 0
    for na in range(1,rnb+1):
        for nb in range(1,rna+1):
            MSE_1, MSE_n = gerar_mse(na, nb, u, y, delay)
            # Limitador para permitir a plotagem
            if MSE_n >= 9999:
                MSE_n = np.inf
            if p:
                theta = gerar_coeficientes(na, nb, u, y, delay)
                theta = " ".join(map(lambda x: f'{x:0.5}',theta))
                print(f'Modelo {i} com na:{na} nb:{nb}')
                print(f'MSE 1: {MSE_1:0.6f} e MSE n: {MSE_n:0.6f}')
                print(f'Theta: {theta}')
                print()
            MSE_1_array.append(MSE_1)
            i+=1
    return np.array(MSE_1_array)


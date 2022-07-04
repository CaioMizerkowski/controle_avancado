import numpy as np

def lsqrt_polinomial(n, u, y):
    amostras = len(u)
    u = u.flatten()
    y = y.flatten()
    M = np.ones((amostras,n))
    for i in range(n):
        M[:,i] = u**i
    y = np.array(y)
    theta = np.linalg.inv(M.T.dot(M)).dot(M.T).dot(y)
    y_hat = np.sum(M*theta.T,axis=1)
    return theta, y_hat

def lsqr_complex_polinomial(u, y, na=2, nb=1, Ainv=np.ones(1)):
    amostras = u.size
    params = na+nb+1
    M = np.ones((amostras, params), dtype=complex)

    for i in range(nb+1):
        M[:,i] = u**i

    for i in range(nb+1, params):
        j = i - nb
        M[:,i] = -u**j*y
    M = M*Ainv.reshape((Ainv.size,1))
    y = y*Ainv
    M = np.concatenate([M.real, M.imag])
    y_tilde = np.concatenate([y.real, y.imag])
    theta = np.linalg.inv(M.T.dot(M)).dot(M.T).dot(y_tilde)
    y_hat_tilde = np.sum(M*theta.T,axis=1)
    y_hat = y_hat_tilde[:amostras]+1j*y_hat_tilde[amostras:]
    return y_hat, theta

def funcao_g_sk(u, theta, na=2, nb=1):
    params = na+nb+1
    B = 0
    for i in range(nb+1):
        B += theta[i]*u**i
    A = 1
    for i in range(nb+1, params):
        j = i - nb
        A += theta[i]*u**j
    return B/A

def A_sk(u, theta, na, nb):
    A = 1
    params = na+nb+1
    for i in range(nb+1, params):
        j = i - nb
        A += theta[i]*u**j
    return 1/A

def gerar_dados_freq_complex(u, y, na, nb, L=1):
    theta = np.zeros(na+nb+1)
    for _ in range(L):
        Ainv = A_sk(u, theta, na, nb)
        _, theta = lsqr_complex_polinomial(u, y, na=na, nb=nb, Ainv=Ainv)
        y_hat = funcao_g_sk(u, theta, na, nb)
    return y_hat
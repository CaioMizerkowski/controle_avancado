import numpy as np


class controler:
    def __init__(self, A) -> None:
        shape_sistema = 3
        valor_matriz_covar = 100
        self.A = A

        # valores dos a's e b's
        self.sistema = np.ones((1, shape_sistema)) * 0.1

        self.u_max = 100
        self.u_min = 0

        self.M = valor_matriz_covar * np.eye(shape_sistema)

        self.du = np.zeros(3)
        self.dy = np.zeros(2)
        self.psi = np.zeros(3)

        self.y_passado = 0
        self.u_passado = 0
        self.e_passado = 0

        self.denom = 0

    def new_e_atual(self, y_atual, y_esperado):
        """
        operações escalares para atualizar o valor do erro
        """
        e_atual = y_esperado - y_atual
        return e_atual

    def update_psi(self):
        self.psi = np.array([[self.dy[1], self.du[1], self.du[2]]])
        self.update_numerador()
        self.update_denominador()

    def update_numerador(self):
        """
        operação matricial com resultado matricial
        """
        # self.numer = self.M * self.psi.T
        self.numer = self.M @ self.psi.T

    def update_denominador(self):
        """
        operação matricial com resultado escalar
        """
        # self.denom = 1 + self.psi * self.numer
        self.denom = 1 + self.psi @ self.numer

    def update_dy(self, y_atual):
        """
        operações escalares para atualizar o valor de dy
        """
        self.dy[0] = y_atual - self.y_passado
        self.dy[1] = self.dy[0]

    def update_sistema(self):
        """
        operação matricial com resultado matricial
        """
        erro = self.dy[0] - self.psi @ self.sistema.T  # valor escalar
        ganho = self.numer / self.denom  # vetor
        self.sistema += ganho.T * erro

    def update_M(self):
        """
        operação matricial com resultado matricial
        """
        # self.M -= self.numer * self.psi * self.M / self.denom
        self.M -= (self.numer @ self.psi @ self.M) / self.denom

    def update_du(self, e_atual):
        """
        operações escalares para atualizar o valor de du
        """
        a1 = self.sistema[0, 0]
        b0 = self.sistema[0, 1]
        b1 = self.sistema[0, 2]

        g0 = self.A * self.A * (1 - self.A) / (self.A * b0 + b1)
        self.du[0] = g0 * (e_atual - a1 * self.e_passado)
        self.du[2], self.du[1] = self.du[1], self.du[0]

    def new_u_atual(self):
        """
        operações escalares para o cálculo do novo valor de u
        """
        u_atual = self.u_passado + self.du[0]
        u_atual = max(min(u_atual, self.u_max), self.u_min)
        return u_atual

    def controlador(self, y_atual, y_esperado):
        e_atual = self.new_e_atual(y_atual, y_esperado)

        self.update_psi()
        self.update_dy(y_atual)
        self.update_sistema()
        self.update_M()
        self.update_du(e_atual)

        u_atual = self.new_u_atual()

        self.e_passado = e_atual
        self.y_passado = y_atual
        self.u_passado = u_atual

        return u_atual


def modelo_teste(u_passado, y_passado):
    return 0.0025 * u_passado + 0.9936 * y_passado + np.random.normal(0, 0.0001)


if __name__ == "__main__":
    from matplotlib import pyplot as plt

    plt.figure()
    y_esperado = 5
    min_erro = 100
    A_min = 0
    for i in range(0, 50):
        A = 2 * i / (50 + i)
        control = controler(A)
        erros = []
        for k in range(200):
            y_atual = modelo_teste(control.u_passado, control.y_passado)
            u_atual = control.controlador(y_atual, y_esperado)
            erro = y_esperado - y_atual
            erros.append(erro)
            # print(f"{k}: erro: {erro:.02f}")
        if np.abs(min_erro) > np.abs(np.mean(erros[100:])):
            A_min = A
            min_erro = np.mean(erros[100:])
            plt.plot(erros)
    print(f"A_min: {A_min:.03f} erro: {min_erro:.02f}")
    _ = input(f"Sistema identificado com A = {A_min:.03f}")
    plt.grid()
    plt.show()
    plt.close()

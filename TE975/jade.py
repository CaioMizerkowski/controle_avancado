#!/usr/bin/env python
# coding: utf-8
import numpy as np


def random_sample(arr, size: int = 1):
    return arr[np.random.choice(arr.shape[0], size=size, replace=False)]


class JADifferentialEvolution():
    def __init__(self, fitness, bounds, seed=np.random.choice(range(1000)),
                 X=None, G=1000, mutation=0.75, recombination=0.75):
        self._bounds = bounds
        self._dim = bounds.shape[0]
        self._fitness = fitness
        self._pop_size = self._dim*15

        self._c = 0.1
        self._sucess_idx = np.array([], dtype=int)

        self._uf = mutation  # 0.5
        self._f = np.array([]).reshape([0, self._pop_size])
        self._sucess_f = np.array([]).reshape([0, self._pop_size])

        self._ucr = recombination  # 0.5
        self._cr = np.array([]).reshape([0, self._pop_size])
        self._sucess_cr = np.array([]).reshape([0, self._pop_size])

        self._G = G
        self._g = 0

        self._seed = seed
        self._idx = 0
        self.X_vector = None
        self.X_values = None

        self.X = None
        self.P = np.array([]).reshape([0, self._dim])
        self.A = np.array([]).reshape([0, self._dim])

        self._gen_x_orig(X)
        self._mutation = self._mutation_current_to_pbest_1_bin
        self._shape = self.X.shape

        self._p = 0.1
        self._P = int(np.round(self._p*self._pop_size))

    def _gen_cr(self):
        cr = np.random.normal(self._ucr, 0.1, size=self._pop_size)
        self._cr = cr.clip(0, 1)

    def _gen_f(self):
        f = np.random.standard_cauchy(size=self._pop_size)*0.1+self._uf
        self._f = f.clip(0, 1)

    def _update_ucr(self):
        if self._sucess_idx.size > 0:
            scr = self._cr[self._sucess_idx]
            self._ucr = (1-self._c)*self._ucr+self._c*scr.mean()

    def _update_uf(self):
        if self._sucess_idx.size > 0:
            sf = self._f[self._sucess_idx]
            self._uf = (1-self._c)*self._uf+self._c*(sum(sf**2)/sf.sum())

    def _check_bound(self, u):
        for idx, k in enumerate(u):
            if self._bounds[idx][0] > k:
                u[idx] = self._bounds[idx][0]
            if self._bounds[idx][1] < k:
                u[idx] = self._bounds[idx][1]
        return u

    def _selection(self, x, u):
        u = self._check_bound(u)
        x_func = self._fitness(x)
        u_func = self._fitness(u)
        if x_func <= u_func:
            return x_func, x
        self._sucess_idx = np.concatenate([self._sucess_idx, [self._idx]])
        self._increment_archive(x)
        return u_func, u

    def _mutation_current_to_pbest_1_bin(self, x):
        x1 = random_sample(self.X)[0]
        x2 = random_sample(np.concatenate([self.X, self.A]))[0]
        pb = random_sample(self.P)[0]
        x = self.X[self._idx]
        f = self._f[self._idx]
        return x+f*(pb-x)+f*(x1-x2)

    def _recombination(self, x, v):
        u = np.zeros(shape=v.shape)
        cidx = np.random.randint(0, self._dim)
        cr = self._cr[self._idx]
        for idx, (x0, v0) in enumerate(zip(x, v)):
            u[idx] = v0 if np.random.uniform(
            ) < cr or idx == cidx else x0
        return u

    def _gen_p_bests(self):
        idx_p = self.X_values.argpartition(self._P)[:self._P]
        self.P = self.X[idx_p, :]

    def _increment_archive(self, x):
        self.A = np.concatenate([self.A.copy(), [x]])

    def _clean_archive(self):
        self.A = self.A[np.unique(self.A, axis=0, return_index=True)[
            1].sort()][0]
        if self.A.shape[0] > self._pop_size:
            self.A = random_sample(self.A, size=self._pop_size)

    def differential_evolution(self):

        self.X_vector = [self.X]
        np.random.seed(self._seed)

        while self._g < self._G:
            X_new = np.zeros(self._shape)
            X_values_new = np.zeros(self._pop_size)
            self._sucess_idx = np.array([], dtype=int)

            self._gen_cr()
            self._gen_f()
            self._gen_p_bests()

            for self._idx, x in enumerate(self.X):
                v = self._mutation(x)
                u = self._recombination(x, v)
                X_values_new[self._idx], X_new[self._idx] = self._selection(
                    x, u)

            self.X = X_new.copy()
            self.X_values = X_values_new.copy()
            self._clean_archive()

            self._update_ucr()
            self._update_uf()
            self.X_vector.append([self.X_values, self.X])
            self._g += 1

    def run(self):
        self.differential_evolution()

    @property
    def fun(self):
        return min(map(self._fitness, self.X))

    def _gen_x_orig(self, X=None):
        if X is not None:
            self.X = X
        else:
            np.random.seed(self._seed)
            self.X = np.zeros(shape=(self._pop_size, self._dim))
            for i in range(self._dim):
                self.X.T[i] = np.random.uniform(low=self._bounds[i][0],
                                                high=self._bounds[i][1],
                                                size=(self._pop_size))
        self.X_values = np.array(list(map(self._fitness, self.X)))


if __name__ == '__main__':
    pass
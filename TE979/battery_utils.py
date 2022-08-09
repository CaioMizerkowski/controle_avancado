from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.optimize import curve_fit
from functools import partial
import polars as ps
import pandas as pd
import numpy as np
import json

WS = pd.read_excel("./Tensão_vs_SoC_C100.xlsx")
df_soc = ps.DataFrame(WS)
df_soc = df_soc.drop("Unnamed: 0")
argmin = df_soc["SoC"][:500].to_numpy().argmin()
df_soc = df_soc[argmin:]
argmax = df_soc["SoC"].to_numpy().argmax()


def v_inf():
    inf = df_soc[argmax:].unique().sort(by="SoC").clone()
    inf = inf[370:34693]

    soc = inf["SoC"].to_numpy()
    v = inf["Tensão [V]"].to_numpy()

    cs_inf = CubicSpline(soc, v)
    return cs_inf


def v_sup():
    sup = df_soc[362:argmax].unique().clone()
    sup.sort(by="SoC", in_place=True)

    soc = sup["SoC"].to_numpy()
    v = sup["Tensão [V]"].to_numpy()

    cs_sup = CubicSpline(soc, v)
    return cs_sup


def v_mid():
    cs_inf = v_inf()
    cs_sup = v_sup()

    return lambda soc: (cs_sup(soc) + cs_inf(soc)) / 2


def aproximacao_coef(soc, x0, x1):  # , x2):
    coef = x0 + x1 * soc  # +x2*soc**2
    return coef


def cs_base():
    indexes = dict()
    I = "100A"
    bounds = ([-np.inf, -np.inf, -np.inf, -np.inf], [np.inf, np.inf, np.inf, np.inf])
    soc = np.array(
        [
            0.99992121,
            0.89972373,
            0.80011121,
            0.70018156,
            0.59969705,
            0.49886181,
            0.39787608,
            0.29648346,
            0.19333107,
            0.08972434,
        ]
    )[-1::-1]

    def inner(index):
        nonlocal indexes
        if index in indexes:
            return indexes[index]

        with open("../data/coef.json", "r") as f:
            coef = json.load(f)
        coef = np.array([coef[I][c][index] for c in coef[I]])[-1::-1]
        p0 = [0, 0]
        if index == 7:
            coef[3] = (coef[2] + coef[4]) / 2
        interpolation = curve_fit(
            f=aproximacao_coef,
            xdata=soc,
            ydata=coef,
            p0=p0,
            maxfev=30000,
            bounds=bounds,
        )[0]
        interpolation = partial(
            aproximacao_coef, x0=interpolation[0], x1=interpolation[1]
        )  # , x2=interpolation[2]) #, x3=interpolation[3])
        indexes[index] = interpolation

        return interpolation

    return inner


cs_inner = cs_base()


def cs_r0(soc):
    return cs_inner(5)(soc)


def cs_r1(soc):
    return cs_inner(6)(soc)


def cs_r2(soc):
    return cs_inner(7)(soc)


def cs_c1(soc):
    return cs_inner(8)(soc)


def cs_c2(soc):
    return cs_inner(9)(soc)

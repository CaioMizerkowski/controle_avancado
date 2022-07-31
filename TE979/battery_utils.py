from scipy.interpolate import CubicSpline, PchipInterpolator
import polars as ps
import pandas as pd
import numpy as np
import json

WS = pd.read_excel('./Tensão_vs_SoC_C100.xlsx')
df_soc = ps.DataFrame(WS)
df_soc = df_soc.drop('Unnamed: 0')
argmin = df_soc['SoC'][:500].to_numpy().argmin()
df_soc = df_soc[argmin:]
argmax = df_soc['SoC'].to_numpy().argmax()

def v_inf():
    inf = df_soc[argmax:].unique().sort(by='SoC').clone()
    inf = inf[370:34693]
    
    soc = inf['SoC'].to_numpy()
    v = inf['Tensão [V]'].to_numpy()
    
    cs_inf = CubicSpline(soc, v)
    return cs_inf

def v_sup():
    sup = df_soc[362:argmax].unique().clone()
    sup.sort(by='SoC', in_place=True)
    
    soc = sup['SoC'].to_numpy()
    v = sup['Tensão [V]'].to_numpy()
    
    cs_sup = CubicSpline(soc, v)
    return cs_sup

def v_mid():
    cs_inf = v_inf()
    cs_sup = v_sup()
    
    return lambda soc: (cs_sup(soc)+cs_inf(soc))/2

def cs_base():
    indexes = dict()
    I = '100A'

    with open('../data/coef.json', 'r') as f:
        coef = json.load(f)
        v = [coef[I][c][11] for c in coef[I]][-1::-1]

    def inner(index):
        nonlocal indexes
        if index in indexes:
            return indexes[index]
        
        with open('../data/coef.json', 'r') as f:
            coef = json.load(f)
        coef = np.array([coef[I][c][index] for c in coef[I]])[-1::-1]

        interpolation = PchipInterpolator(v, coef)
        indexes[index] = interpolation

        return interpolation
    
    return inner

cs_inner = cs_base()

def cs_r0(v):
    return cs_inner(5)(v)

def cs_r1(v):
    return cs_inner(6)(v)

def cs_r2(v):
    return cs_inner(7)(v)

def cs_c1(v):
    return cs_inner(8)(v)

def cs_c2(v):
    return cs_inner(9)(v)

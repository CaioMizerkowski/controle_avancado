from scipy.interpolate import CubicSpline
import polars as ps
import pandas as pd
import numpy as np
import json

with open('../data/coef.json', 'r') as f:
    coef = json.load(f)
I = '100A'

WS = pd.read_excel('./Tensão_vs_SoC_C100.xlsx')
df_soc = ps.DataFrame(WS)
df_soc = df_soc.drop('Unnamed: 0')
argmin = df_soc['SoC'][:500].to_numpy().argmin()
df_soc = df_soc[argmin:]
argmax = df_soc['SoC'].to_numpy().argmax()

def soc_inf():
    inf = df_soc[argmax:].unique().sort(by='SoC').clone()
    inf = inf[370:34693]
    
    soc = inf['SoC'].to_numpy()
    v = inf['Tensão [V]'].to_numpy()
    
    cs_inf = CubicSpline(soc, v)
    return cs_inf

def soc_sup():
    sup = df_soc[362:argmax].unique().clone()
    sup.sort(by='SoC', in_place=True)
    
    soc = sup['SoC'].to_numpy()
    v = sup['Tensão [V]'].to_numpy()
    
    cs_sup = CubicSpline(soc, v)
    return cs_sup

def soc_mid():
    cs_inf = soc_inf()
    cs_sup = soc_sup()
    
    return lambda soc: (cs_sup(soc)+cs_inf(soc))/2

def cs_r0():
    v_max = [coef[I][c][11] for c in coef[I]]
    soc = soc_mid()(v_max)[-1:0:-1]
    x = np.array([coef[I][c][4] for c in coef[I]])[-1:0:-1]
    cs = CubicSpline(soc, x)
    return cs

def cs_r1():
    v_max = [coef[I][c][11] for c in coef[I]]
    soc = soc_mid()(v_max)[-1:0:-1]
    x = np.array([coef[I][c][5] for c in coef[I]])[-1:0:-1]
    cs = CubicSpline(soc, x)
    return cs

def cs_r2():
    v_max = [coef[I][c][11] for c in coef[I]]
    soc = soc_mid()(v_max)[-1:0:-1]
    x = np.array([coef[I][c][6] for c in coef[I]])[-1:0:-1]
    cs = CubicSpline(soc, x)
    return cs

def cs_c1():
    v_max = [coef[I][c][11] for c in coef[I]]
    soc = soc_mid()(v_max)[-1:0:-1]
    x = np.array([coef[I][c][7] for c in coef[I]])[-1:0:-1]
    cs = CubicSpline(soc, x)
    return cs

def cs_c2():
    v_max = [coef[I][c][11] for c in coef[I]]
    soc = soc_mid()(v_max)[-1:0:-1]
    x = np.array([coef[I][c][8] for c in coef[I]])[-1:0:-1]
    cs = CubicSpline(soc, x)
    return cs
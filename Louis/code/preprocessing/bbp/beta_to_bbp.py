from preprocessing.bbp.betasw_zhh09 import betasw_ZHH2009
from numpy import pi
def beta_to_bbp(beta, temp, salinity):
    theta = 124
    delta = 0.039
    Xi = 1.077
    l = 700
    betasw, beta90sw, bsw = betasw_ZHH2009(l, temp, theta, salinity, delta)
    betap = beta - betasw
    bbp = betap * 2 * pi * Xi
    return bbp
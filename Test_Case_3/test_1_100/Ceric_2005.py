import numpy as np
import pandas as pd



Qgpm = 10
Qcfd = Qgpm * (60*24) / 7.4018
n = .3
hk = 10
H = 200 # ft
h1 = 210 -200
h2 = 200 - 200
d = 4000 # ft
i = (h2 - h1) /d 
###############################

Qcfd = 190000
n = .3
hk = 1500
H = 75 # ft
h1 = 210 -200
h2 = 200 - 200
d = 4000 # ft
i = .003 


Q0 = hk*H * i
print(f'Q0 = {Q0}')

T0 = n*H*Qcfd / (2 * np.pi*Q0**2) 


print(f'T0 = {T0}')

Ls = Qcfd/(2*np.pi*Q0)

print(f'Ls = {Ls}')

T = 0.331504032454500E+05 # taken from modpath endpt
T = 20
# def TOT(Qo,T,n,b,Q):
#     numerater = 2*np.pi*(Qo**2)*T
#     denom = n*b*Q
#     return numerater/denom

T_s = (2*np.pi*(Q0**2)*T)/(n*H*Qcfd)

print(f'T_s = {T_s}')



Lu = T_s + np.log(T_s + np.e)

print(Lu)

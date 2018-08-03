import numpy as np
import pandas as pd





def ymax(Q,b,k,i):
	return Q/(2*b*k*i)

def stag_dist(Q,b,k,i):
	return -Q / (2 * np.pi * k * b * i)

def get_y_vals(ymax):
	y = abs(int(ymax))
	y = [y-1]
	for i in range(80):
		if i <= 10:
			val = .99
		elif i <= 49:
			val = .95
		else:
			val = .9
		y.append(y[-1]*val)
	return y

def make_shape(y,Q,b,k,i):
	x = -y/ np.tan((2*np.pi*k*b*i*y)/Q)
	return x

def ymax_uc(Q,k,h1,h2,L):
	return (Q*L)/(k*((h2**2)-(h1**2)))

def make_shape_uc(y,Q,b,k,h1,h2,L):
	x = -y/ np.tan((np.pi*k*((h2**2)-(h1**2))*y)/(Q*L))
	return x

# Qgpm = 10
# Qcfd = Qgpm * (60*24) / 7.4018
# n = .3
# hk = 10
# H = 200 # ft
# h1 = 210 -200
# h2 = 200 - 200
# d = 4000 # ft
# i = (h2 - h1) /d 
# ###############################

# Qcfd = 190000
# n = .3
# hk = 1500
# H = 75 # ft
# h1 = 210 -200
# h2 = 200 - 200
# d = 4000 # ft
# i = .003 


# Q0 = hk*H * i
# print(f'Q0 = {Q0}')

# T0 = n*H*Qcfd / (2 * np.pi*Q0**2) 


# print(f'T0 = {T0}')

# Ls = Qcfd/(2*np.pi*Q0)

# print(f'Ls = {Ls}')

# T = 0.331504032454500E+05 # taken from modpath endpt
# T = 20
# # def TOT(Qo,T,n,b,Q):
# #     numerater = 2*np.pi*(Qo**2)*T
# #     denom = n*b*Q
# #     return numerater/denom

# T_s = (2*np.pi*(Q0**2)*T)/(n*H*Qcfd)

# print(f'T_s = {T_s}')



# Lu = T_s + np.log(T_s + np.e)

# print(Lu)

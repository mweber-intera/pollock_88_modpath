import numpy as np
import pandas as pd



# Todd 1980

def ymax(Q,b,k,i):
	return Q/(2*b*k*i)

def stag_dist(Q,b,k,i):
	return -Q / (2 * np.pi * k * b * i)


def make_shape(y,Q,b,k,i):
	x = -y/ np.tan((2*np.pi*k*b*i*y)/Q)
	return x


# from Grubb 1993
def ymax_uc(Q,k,h1,h2,L):
	return (Q*L)/(k*((h1**2)-(h2**2)))

def make_shape_uc(y,Q,k,h1,h2,L):
	x = -y/ np.tan((np.pi*k*((h1**2)-(h2**2))*y)/(Q*L))
	return x

# ---------

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

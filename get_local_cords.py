import pandas as pd
import os
import flopy
import fetter
import numpy as np
import matplotlib.pyplot as plt

dirs = ['test_1_100','test_1_50','test_1_10']
# dirs = ['test_1_10','test_1_50','test_1_100']

well_loc = {'test_1_100':[31050.,19950.],'test_1_50':[31025.,9975.],'test_1_10':[31005.,9995.]}
# sr = 	flopy.utils.reference.SpatialReference()

def calc_local_x(delr,col,x):
	temp_x = delr * (col-1)
	val = x - temp_x
	localX = val / delr
	return localX

def calc_local_y(delc,row,y,nrow):
	temp_y = delc * (nrow - (row-1))
	val = temp_y - y
	# print(temp_y,y,val)
	# exit()
	localY = 1 - (val / delc)
	return localY

for path in dirs:
	print(path)
	model_ws = os.path.join(path,'workspace')
	modelname = 'test_1'
	mf = flopy.modflow.Modflow.load(modelname+'.nam',version='mf2k',model_ws=model_ws,check=False,load_only=['DIS'])
	dis = mf.dis
	delr = dis.delr.array
	delc = dis.delc.array
	nrow, ncol = dis.nrow, dis.ncol

	Lx, Ly = delr.sum(), delc.sum()
	sr = dis.sr

	Qcfd = -2.5 * 192.5
	hk = 10
	h1, h2 = 200, 167.35
	Lx = 40000.
	ymax = fetter.ymax_uc(Qcfd,hk,h1,h2,Lx)
	xstag = fetter.stag_dist_uc(Qcfd,hk,h1,h2,Lx)
	print(ymax,xstag)

	# print(x0,y0)
	x0, y0 = 0, 0
	y = fetter.get_y_vals(ymax, y0)
	# y = np.array(y)
	x = fetter.make_shape_uc(y,Qcfd,hk,h1,h2,Lx,x0)
	
	# print(x,y)


	df = pd.DataFrame({'glob_x':x,'glob_y':y})
	x0, y0 = well_loc[path][0], well_loc[path][1]
	df['glob_x'] += x0
	df['glob_y'] += y0

	df['Row'], df['Column'] = sr.get_rc(df['glob_x'].tolist(),df['glob_y'].tolist())
	df['Row'] = df['Row'] + 1
	df['Column'] = df['Column'] + 1
	df['LocalX'] = df.apply(lambda xy: calc_local_x(delr[0],xy['Column'],xy['glob_x']),axis=1)
	df['LocalY'] = df.apply(lambda xy: calc_local_y(delc[0],xy['Row'],xy['glob_y'],nrow),axis=1)
	# print(df['LocalY'])

	df = df.loc[(df['Column'] > 0) & (df['Column'] <=ncol)]
	df = df.loc[(df['Row'] > 0) & (df['Row'] <=nrow)]


	df['ParticleID'] = np.arange(1,len(df)+1)
	df['GroupNumber'] = 1
	df['Grid'] = 1
	df['Layer'] = 1
	df['LocalZ'] = .5
	df['ReleaseTime'] = 0
	df['Label'] = 'GP01'
	# fig, ax = plt.subplots()

	# ax.plot(df['glob_x'],df['glob_y'])

	# df['Column'] = df['Column'] + 1

	df = df[['ParticleID','GroupNumber','Grid','Layer','Row','Column','LocalX','LocalY','LocalZ','ReleaseTime','Label','glob_x','glob_y']]
	df.to_csv(path+'starting_locs.csv',index=False)
	# modelmap = flopy.plot.ModelMap(model=mf, layer=0)
	# # lc = modelmap.plot_grid()
	# ax.scatter(well_loc[path][0],well_loc[path][1],color='r')


	# ax.set_ylim([0,delc.sum()])
	# ax.set_xlim([0,delr.sum()])

	# plt.show()




	# exit()




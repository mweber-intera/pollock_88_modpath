import flopy
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

modelname = 'test_case_3'
exe = os.path.join('gw_codes','mf2k-chprc08spl.exe') # moved the exes here for clean up, RKK
mp6_exe = os.path.join('..','gw_codes','mp6.exe')
model_ws = os.path.join('workspace') # moved model here to keep things orginized, RKK
mf = flopy.modflow.Modflow.load('test_case_3.nam',model_ws=model_ws)


def write_loc_file(file_nam,strt_time=0,input_style=1,backwards=True):
    if backwards:
        df = pd.read_csv('particle_starting_locs_backwards.csv')
    else:
        df = pd.read_csv('test_1_50starting_locs.csv')
    columns = ['ParticleID', 'GroupNumber', 'Grid', 'Layer', 'Row', 'Column', 'LocalX', 'LocalY', 'LocalZ',
             'ReleaseTime', 'Label']
    grps = df['GroupNumber'].unique().tolist()

    # print(grps)

    file = open(file_nam,'w')
    file.write(f'1\n{len(grps)}\n')
    for grp in grps:
        tempDF = df[df['GroupNumber'] == grp]
        grp_nam = tempDF.iloc[0]['Label']
        file.write(f'{grp_nam}'+'\n')
        file.write(f'{len(tempDF)}\n')
    for grp in grps:
        tempDF = df[df['GroupNumber'] == grp]
        grp_nam = tempDF.iloc[0]['Label']
        for z in range(len(tempDF)):
            for j in columns:
                file.write(f'{tempDF.iloc[z][j]}  ')
            file.write('\n')


starting_loc = os.path.join(model_ws,'starting_pts.loc')




mp = flopy.modpath.Modpath('test_case_3',exe_name=mp6_exe,modflowmodel=mf,model_ws=model_ws,dis_file = mf.name+'.dis',head_file=mf.name+'.hds',budget_file=mf.name+'.cbc')
mp_ibound = mf.bas6.ibound.array # use ibound from modflow model
mpb = flopy.modpath.ModpathBas(mp,-1e30,ibound=mp_ibound,prsity =.3) # make modpath bas object


backwards = True
write_loc_file(starting_loc,backwards=backwards)


if backwards:
    sim = mp.create_mpsim(trackdir='backward', simtype='pathline', packages='starting_pts.loc', start_time=(0, 0, 0)) # create simulation file
else:
    sim = mp.create_mpsim(trackdir='forward', simtype='pathline', packages='starting_pts.loc', start_time=(0, 0, 0)) # create simulation file


mp.write_input()
mp.run_model(silent=False)
Qgpm = 100
Qcfd = Qgpm * (60*24) / 7.48052
b = 178.6 #175.25
hk = mf.lpf.hk.array.mean()
h1, h2 = 200, 199.048
L = 40000*2.
grad = (199.5-200)/(40000)

import fetter

ymax = fetter.ymax_uc(Qcfd,hk,h1,h2,L)

xstag = -fetter.stag_dist(Qcfd,b,hk,grad)

y = fetter.get_y_vals(ymax)
y = np.array(y)
yinv = np.array(y) * -1



x = -fetter.make_shape_uc(y,Qcfd,hk,h1,h2,L)
# exit()

import flopy.utils.binaryfile as bf

cbb = bf.CellBudgetFile(os.path.join(model_ws,modelname+'.cbc'))
times = cbb.get_times()

frf = cbb.get_data(text='FLOW RIGHT FACE', totim=times[-1])[0]



pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'test_case_3.mppth')) # create pathline object
epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'test_case_3.mpend')) # create endpoint object


fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(1, 1, 1,adjustable='box')

hds = bf.HeadFile(os.path.join(model_ws,modelname+'.hds'))
head = hds.get_data(totim=times[-1])
levels = np.linspace(0, 10, 11)

kstpkper_list = cbb.get_kstpkper()
frf = cbb.get_data(text='FLOW RIGHT FACE', totim=times[-1])[0]
fff = cbb.get_data(text='FLOW FRONT FACE', totim=times[-1])[0]

modelmap = flopy.plot.ModelMap(model=mf, layer=0)
qm = modelmap.plot_ibound()
# lc = modelmap.plot_grid()
# cs = modelmap.contour_array(head, levels=levels)
# quiver = modelmap.plot_discharge(frf, fff, head=head)

well_epd = epdobj.get_alldata()
well_pathlines = pthobj.get_alldata()
# ax.plot(x+53350+25,y+20000-25,lw=4,color='g')
# ax.plot(x+53350+25,yinv+20000-25,lw=4,color='g',label='Analytical Solution')

ax.scatter(x+53350+25,y+20000-25,s=40,color='g',zorder=5)
ax.scatter(x+53350+25,yinv+20000-25,s=40,color='g',label='Analytical Solution',zorder=4)

modelmap.plot_pathline(well_pathlines, travel_time=None, layer='all', colors='red',zorder=2,lw=5) # plot pathline <= time
modelmap.plot_endpoint(well_epd, direction='starting', colorbar=False) # can only plot starting of ending, not as dynamic as pathlines
modelmap.plot_bc('wel',color='k')

ax.scatter([53350-25],[20000-25],color='k',label='Well',s=200,zorder=3)

ax.plot([0,1],[0,1],'r',label='Modpath Pathlines')
# ax.adjustable='datalim'
ax.legend(fancybox=True,framealpha=1,loc='upper left')
ax.set_aspect(1)#, 'datalim')
ax.set_ylim([0,40000])
ax.set_xlim([20000,60000])
ax.grid()
ax.set_ylabel('feet')
ax.set_xlabel('feet')
fig.tight_layout()

output = 'output'
if not os.path.exists(output): os.mkdir(os.path.join('output'))


if backwards:
    plt.title('Backward Simulation')
    fig.tight_layout()
    fig.savefig(os.path.join(output,'backwards.png'))
else:
    plt.title('Forward Simulation')
    fig.tight_layout()
    fig.savefig(os.path.join(output,'forwards.png'))
# plt.savefig('test_1_mp.png')








plt.close('all')

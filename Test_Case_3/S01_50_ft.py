import flopy
import numpy as np
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf
import os

#note: change the version from modflow 2005 to mf2k. Guessed at the version code, because I couldn't figure out the help
modelname = 'test_1'
exe = os.path.join("..","gw_codes",'mf2k-chprc08spl.exe') # moved the exes here for clean up, RKK
model_ws = os.path.join('workspace') # moved model here to keep things orginized, RKK
mf = flopy.modflow.Modflow(modelname, version='mf2k', exe_name =exe,model_ws=model_ws)
#m = flopy.modflow.Modflow.add_output_file(self=mf, unit=50, fname=modelname, extension='.cbb', binflag=True)

#DIS
Lx = 40000.*2
Ly = 40000.2
ztop = 200.
zbot = 0
nlay = 1
nrow = int(400*2)
ncol = 400*4
delr = Lx/ncol
delc = Ly/nrow
delv = (ztop - zbot) / nlay
botm = np.linspace(ztop, zbot, nlay + 1)
nper = 5 # lets add some more stress periods, RKK
perlen = 1

print(ncol)
dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc, top=ztop, botm=botm[1:],nper=nper,perlen=perlen)

#BAS for 64-bit
ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
ibound[:, :, 0] = -1
ibound[:, :, -1] = -1
strt = np.ones((nlay, nrow, ncol), dtype=np.float32)
strt[:, :, 0] = 200.
strt[:, :, -1] = 199.048
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)

#LPF change hydraulic conductivity here
lpf = flopy.modflow.ModflowLpf(mf, hk=1000, vka=5000., ipakcb=53)

#OC
spd = {} # slight change to oc so we can save heads and budget for all stress periods
for sp in range(nper):
    spd[(sp, 0)] = ['save head', 'save budget']
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True)
#, extension=['oc', 'hds', 'ddn', 'cbb', 'ibo']

#PCG
#I've seen examples of all three solvers being used
pcg = flopy.modflow.ModflowPcg(mf)

#WEL
Qgpm = -100
Qcfd = Qgpm * (60*24) / 7.4018
wel_spd = {0:[0,int(nrow/2),int(ncol*2/3),Qcfd]}
print(nrow/2)
wel = flopy.modflow.ModflowWel(mf,stress_period_data=wel_spd,ipakcb=53)

#write the modflow input files
mf.write_input()

# Run the MODFLOW model
success, buff = mf.run_model(silent=False)
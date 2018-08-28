import flopy
import os
import pandas as pd
import math as math
import numpy as np


model_ws = os.path.join('pollock_model_ex1')
if not os.path.exists(model_ws): os.mkdir(model_ws)
gw_codes = os.path.join('gw_codes')
exe = os.path.join(gw_codes,'mf2k-chprc08spl.exe')
mf = flopy.modflow.Modflow('pollock_88',version='mf2k',exe_name=exe,model_ws=model_ws)

# import digitized data csv
digitized = pd.read_csv('figure_7_distances.csv')


# import modpath results
with open(os.path.join('pollock_model_ex1','pollock_88_mp.mppth'), 'r') as f:
    lines_after_header = f.readlines()[3:]
    step = []
    step2 = []
    step3 = []
    step4 = []
    for line in lines_after_header:
        step4.append(line.split()[0])
        step.append(float(line.split()[4]))
        step2.append(float(line.split()[5]))
        step3.append(float(line.split()[6]))
df = pd.DataFrame({'ParticleID':step4,
                   'Time':step,
                   'GlobalX':step2,
                   'GlobalY':step3})



# equation for calculating the line length
def calc_line_length(x1, x2, y1, y2):
    line_length = np.sqrt(((x2-x1)**2)+((y2-y1)**2))
    return line_length

all=[]

# get the 0 day average from mppth
xlist0d = df.loc[(df['Time']==0.000000000000000E+00), ['ParticleID','Time','GlobalX','GlobalY']]
xlist0d=xlist0d.drop(xlist0d.index[11:])
#print(xlist0d)


# get the 2500 day average from mppth
xlist25h = df.loc[(df['Time']==0.250000000000000E+04), ['ParticleID','Time','GlobalX','GlobalY']]
xlist25h=xlist25h.drop(xlist25h.index[11:])
xlist25h=xlist25h.rename(index=str, columns={'Time':'Time_25', 'GlobalX':'GlobalX_25', 'GlobalY':'GlobalY_25'})
all=pd.merge(xlist0d,xlist25h,on='ParticleID')
all['length_25']=all.apply(lambda row: calc_line_length(x1=row['GlobalX'], x2=row['GlobalX_25'], y1=row['GlobalY'], y2=row['GlobalY_25']), axis=1)
# av_len_25h = np.average(xlist25h['length'])
print(all)
out_csv = 'ugh.csv'
all.to_csv(out_csv)
#
# # get the 5000 day average from mppth
# xlist5k = df.loc[(df['Time']==0.500000000000000E+04), ['ParticleID','Time','GlobalX','GlobalY']]
# xlist5k['length50']=np.sqrt((xlist5k['GlobalX50']**2)+(xlist5k['GlobalY50']**2))
# av_len_5k = np.average(xlist5k['length'])
# print(av_len_5k)
#
# # get the 7500 day average from mppth
# xlist75h = df.loc[(df['Time']==0.750000000000000E+04), ['ParticleID','Time','GlobalX','GlobalY']]
# xlist75h['length']=np.sqrt((xlist75h['GlobalX']**2)+(xlist75h['GlobalY']**2))
# av_len_75h = np.average(xlist75h['length'])
# print(av_len_75h)
#
# mppth_all = [av_len_25h, av_len_5k, av_len_75h]
#
# # get the 2500 day average from digitized file
# dig_xlist25h = digitized.loc[(digitized['days']==2500), ['distance']]
# dig_av_len_25h = np.average(dig_xlist25h['distance'])
# print(dig_av_len_25h)
#
# # get the 5000 day average from digitized file
# dig_xlist5k = digitized.loc[(digitized['days']==5000), ['distance']]
# dig_av_len_5k = np.average(dig_xlist5k['distance'])
# print(dig_av_len_5k)
#
# # get the 7500 day average from digitized file
# dig_xlist75h = digitized.loc[(digitized['days']==7500), ['distance']]
# dig_av_len_75h = np.average(dig_xlist75h['distance'])
# print(dig_av_len_75h)
#
# dig_all = [dig_av_len_25h, dig_av_len_5k, dig_av_len_75h]
#
# # calculate percent difference
# perd_tc1 = []
# perdl=[perd_tc1.append(((dig_all[i] - mppth_all[i])/(dig_all[i]+mppth_all[i]/2))*100) for i in range(0,len(mppth_all))]
# print(perd_tc1)
#
# # determine pass/fail
#
# pf_tc1 = []
#
# for item in perd_tc1:
#     if abs(item) > 10.:
#         pf_tc1.append('fail')
#     else:
#         pf_tc1.append('pass')
#
# # compile everything
#
# dictionary = {'Time':[2500, 5000, 7500], 'digitized':dig_all, 'this_run':mppth_all, 'Percent_difference':perd_tc1, 'Pass/Fail':pf_tc1}
# output=pd.DataFrame(dictionary)
# print(output)
# out_csv = 'tc1_results.csv'
# output.to_csv(out_csv)






# post proccesing

# import flopy.utils.binaryfile as bf
#
# headobj = bf.HeadFile(os.path.join(model_ws,'pollock_88.hds')) # make head object with hds file
# times = [0] + headobj.get_times() # get the times (we made this in the begining with the dis)
# print(times) # should be every 500 days, but I added "0" to the begging so we can see when there is no pumping
#
# pthobj = flopy.utils.PathlineFile(os.path.join(model_ws,'pollock_88_mp.mppth')) # create pathline object
# epdobj = flopy.utils.EndpointFile(os.path.join(model_ws,'pollock_88_mp.mpend')) # create endpoint object
#
# fig_list = [] # initialize list of figure paths we will use to make a gif
# for time in times:
#     fig, ax = plt.subplots(figsize=(8,8))
#     extent=(0,Lx,0,Ly)
#     if time != 0:
#         head = headobj.get_data(totim=times[-1])
#         CS = plt.contour(np.flipud(head[0]), extent=extent, color='k')
#         plt.clabel(CS, inline=1, fontsize=10)
#         # plt.imshow(head[0],cmap='cubehelix',extent=extent)
#         # plt.colorbar()
#
#     modelmap = flopy.plot.ModelMap(model=mf, layer=0, ax=ax)
#     lc = modelmap.plot_grid(color='c',alpha=.25)
#     qm = modelmap.plot_bc('CHD', alpha=0.5)
#
#     well_epd = epdobj.get_alldata()
#     well_pathlines = pthobj.get_alldata()
#     modelmap.plot_pathline(well_pathlines, travel_time=f'<={time}', layer='all', colors='red') # plot pathline <= time
#     modelmap.plot_endpoint(well_epd, direction='starting', colorbar=False) # can only plot starting of ending, not as dynamic as pathlines
#     fig_name = os.path.join('figures',f'{int(time)}_days.png') # figure path to save to
#     fig.text(0.15, 0.85,
#              f'Day = {int(time)}',
#              fontsize=16, color='k',
#              ha='left', va='bottom', alpha=1)
#     plt.title('Pollock 1988 Ex. 1')
#     # ax.set_ylim([0,delc*2])
#     # ax.set_xlim([0,delc*2])
#     fig.tight_layout()
#     fig.savefig(fig_name)
#     fig_list.append(imageio.imread(fig_name)) # append imagio.imread() for each figure path
#     plt.close()
#
#
# imageio.mimsave(os.path.join('figures','final_gif.gif'),fig_list,duration=.25) # now save a gif of all the figures in fig_list
#




# floaty = [float(x) for x in step]
# print(floaty)
# maxy = max(floaty)
# print(maxy)


# dictionary = dict(zip(step, step2))
# print(dictionary)

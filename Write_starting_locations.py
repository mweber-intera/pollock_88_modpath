import pandas as pd
import os
import numpy as np

def PointsInCircum(x,y, r,n=8):
    a = [[np.cos(2*np.pi/n*i)*r,np.sin(2*np.pi/n*i)*r] for i in range(0,n+1)]
    x0 = np.array([i[0] for i in a])
    y0 = np.array([i[1] for i in a])
    return x0+x, y0+y



def create_pt_df(dis,strt_time,n=8):
    locx, locy = [], []
    pg,gp_num = [], []
    locr, locc = [], []
    loclay = []
    gp_n = 1
    rt = []

    nrow,ncol,delr,delc = dis.nrow,dis.ncol,dis.delr.array,dis.delc.array
    Lx,Ly = delc.sum(), delr.sum()
    # for something in rows # old way
    x, y = PointsInCircum(.5, .5, .5, n)


    # print(x,y)
    # exit()
    for j in range(n):
        locx.append(x[j])
        locy.append(y[j])
        pg.append(f'GP{gp_n+1:02}')
        locr.append(int(nrow/2)+1)
        locc.append(int(ncol/2)+1)
        loclay.append(1)
        gp_num.append(gp_n)

        rt.append(strt_time[0])
    gp_n += 1
    #ParticleID, GroupNumber, Grid, Layer, Row, Column, LocalX, LocalY, LocalZ, ReleaseTime, Label
    data = {'ParticleID':np.arange(1,len(pg)+1),'GroupNumber':gp_num,'Grid':np.ones(len(locr)).astype(int),'Layer':loclay,
            'Row':locr,'Column':locc,'LocalX':locx,'LocalY':locy,'LocalZ':.5*np.ones(len(locx)),
            'ReleaseTime':rt,'Label':pg}
    # for key in data.keys():
        # print(key, len(data[key]))

    df = pd.DataFrame(data)
    df['Row'] = df['Row'].astype(int)
    df['Column'] = df['Column'].astype(int)
    df['LocalX'] = round(df['LocalX'],4)
    df['LocalY'] = round(df['LocalY'],4)

    df = df[['ParticleID', 'GroupNumber', 'Grid', 'Layer', 'Row', 'Column', 'LocalX', 'LocalY', 'LocalZ',
             'ReleaseTime', 'Label']]

    return df



def write_file(file_nam,dis,strt_time,n,input_style=1):
    df = create_pt_df(dis,strt_time,n)
    columns = ['ParticleID', 'GroupNumber', 'Grid', 'Layer', 'Row', 'Column', 'LocalX', 'LocalY', 'LocalZ',
             'ReleaseTime', 'Label']
    grps = df['GroupNumber'].unique().tolist()
    # print(grps)

    file = open(file_nam,'w')
    file.write(f'1\n{len(grps)}\n')
    for grp in grps:
        tempDF = df[df['GroupNumber'] == grp]
        grp_nam = tempDF.iloc[0]['Label']
        file.write(grp_nam+'\n')
        file.write(f'{len(tempDF)}\n')
    for grp in grps:
        tempDF = df[df['GroupNumber'] == grp]
        grp_nam = tempDF.iloc[0]['Label']
        for z in range(len(tempDF)):
            for j in columns:
                file.write(f'{tempDF.iloc[z][j]}  ')
            file.write('\n')
import pandas as pd
import os
import numpy as np

model_ws = os.path.join('pollock_model_ex1')
mppth = os.path.join(model_ws, 'pollock_88_mp.mppth')
header = ['ParticleID', 'Particle_Group', 'Time_Point_Index', 'Cumulative_TimeStep', 'Tracking_Time', 'Global_X',
          'Global_y', 'Global_Z', 'Layer', 'Row', 'Column', 'Grid', 'Local_X', 'Local_Y', 'Local_Z',
          'Line_Segment_Index']
mppthDF = pd.read_csv(mppth, delim_whitespace=True, skiprows=3, names=header)

print(mppthDF.head())
stress_periods = mppthDF['Cumulative_TimeStep'].unique().tolist()
print(stress_periods)
times = np.array(stress_periods) * 500
print(times)
def dist(x1,y1,x2,y2): # distance formula
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

mean_rd = {}
for sp in [5,10,15]:
    tempDF = mppthDF[mppthDF['Cumulative_TimeStep'] == sp]
    # tempDF.drop_duplicates(subset='ParticleID', keep='first', inplace=True)
    tempDF['dif'] = (tempDF['Tracking_Time'] - 500*sp).abs()
    tempDF = tempDF.loc[tempDF.groupby('ParticleID')['dif'].idxmin()]

    tempDF['rad_dist'] = tempDF.apply(lambda xy: dist(xy['Global_X'],xy['Global_y'],0,0),axis=1)
    print(tempDF)
    mean_rd[sp*500] = tempDF['rad_dist'].mean()
print(mean_rd)
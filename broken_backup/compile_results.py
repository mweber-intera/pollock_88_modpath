# This script should be run after easch test case has been ran
import os
import pandas as pd


folders = os.listdir()
folders = [item for item in folders if item.startswith('Test_Case_')]


writer = pd.ExcelWriter('All_tc_results.xlsx')

for folder in folders:
	cdir = os.path.join(folder,'output')
	i = folder[-1]
	temp_df = pd.read_csv(os.path.join(cdir, f'tc{i}_results.csv'))
	temp_df.to_excel(writer,folder,index=False)

writer.save()

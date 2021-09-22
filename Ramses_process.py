import os
import glob
import pandas as pd
import scipy
from scipy import interpolate
import numpy as np
import re
import datetime

__author__   = 'Thomas Heggem'
__email__    = 'teg@niva.no'
__created__  = datetime.datetime(2021, 9, 17)
__version__  = "1.0"
__status__   = "Development"

def to_rename_columns(df,old_name, new_name):
    if old_name in df.columns:
        df = df.rename(columns={old_name : new_name})
    return df

def calc_spectrum_coeff(df):
    df_coeff=df[["DateTime", "Lat", "Lon", "Pressure", "Wavelength"]]
    E0Ez=df["Deck_int_cal"]/df["LookingUp_int_cal"]

    df_coeff["Kd"]=np.log(E0Ez)/df["Pressure"]

    return df_coeff


def split_cast(df):
    max_idx = np.argmax(df["Pressure"])
    wl=len(df.Wavelength.unique()) #number of unique wavelengths for each timestep
    df_downcast = df[0:max_idx + wl]
    df_upcast = df[max_idx + wl:]
    return [df_downcast, df_upcast]


def rename_intensity(df_downcast, df_upcast):
    list_cols = df_downcast.columns.str.contains(pat='_Intensity_cal')
    int_col = df_downcast.columns[list_cols]
    instr_order = df_downcast[int_col].mean().sort_values(ascending=False)
    df_downcast = df_downcast.rename(columns={instr_order.index[0]: "Deck_int_cal", instr_order.index[1]: "LookingUp_int_cal"})
    df_upcast = df_upcast.rename(columns={instr_order.index[0]: "Deck_int_cal", instr_order.index[1]: "LookingUp_int_cal"})

    if len(instr_order) == 3:
        df_downcast = df_downcast.rename(columns={instr_order.index[2]: "LookingDown_int_cal"})
        df_upcast = df_downcast.rename(columns={instr_order.index[2]: "LookingDown_int_cal"})

    return [df_downcast, df_upcast]

Directory=r"K:\Prosjekter\Sjøvann\KYSTOVERVÅKING ØKOKYST\KYSTOVERVÅKING ØKOKYST 2021-2025\felles\hydrografi\lysdata\NorskehavetNord VR54 VR58\VR58\VR58 2021-06-03"
filename="merged.dat"
fid = os.path.join(Directory, filename)
#dep_start=datetime.datetime(2021, 9, 17)
#dep_stop=datetime.datetime(2021, 9, 17)

df = pd.read_csv(fid, delimiter="\t")
print(df.columns.tolist())
print(fid)

Pressure=df.columns[df.columns.str.contains(pat = '_Pressure')]
df=to_rename_columns(df,Pressure[0], 'Pressure')
df.drop(list(df.filter(regex = 'Error')), axis = 1, inplace = True)
df.drop(list(df.filter(regex = 'Status')), axis = 1, inplace = True)
indexNames = df[ df['Pressure'] < 0 ].index
df.drop(indexNames , inplace=True)

[df_downcast, df_upcast]=split_cast(df)
[df_downcast, df_upcast]=rename_intensity(df_downcast, df_upcast)

df_downcast.to_csv(r"C:\Users\TEG\PycharmProjects\log.csv", sep="\t")
df_coeff =df_downcast.groupby(["DateTime", "Pressure"]).apply(calc_spectrum_coeff)
df_coeff.to_csv(r"C:\Users\TEG\PycharmProjects\check.csv", sep="\t")









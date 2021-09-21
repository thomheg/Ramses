import os
import glob
import pandas as pd
import scipy
from scipy import interpolate
import re
import datetime

__author__   = 'Thomas Heggem'
__email__    = 'teg@niva.no'
__created__  = datetime.datetime(2021, 9, 15)
__version__  = "1.0"
__status__   = "Development"

Directory = "//niva-of5/osl-userdata$/TEG/Documents/RANSES test data/"
Calibration = "C:/Users/TEG/PycharmProjects/ramses/calib_trios_2021/"


def read_calibration(ID,Dir):
    print(Dir)
    s = os.listdir(Dir)
    for f in s:
        if not re.search(ID, f) == None:
            path_cal=os.path.join(Dir,f)
    cal = pd.read_csv(path_cal, delimiter="\t", names=["Wavelength", "coeff"], skiprows=71, engine="python")
    return cal


def read_samip(SAMIP, path_cal, ID):
    df_SAMIP = pd.DataFrame()
    cal = read_calibration(ID, path_cal)

    for fid in SAMIP:
        df_intpl = pd.DataFrame()
        df_specIP=pd.read_csv(fid,delimiter=" ",names=["col1","Wavelength","Intensity","Error","Status"],skiprows=50, skipfooter=65,engine="python")
        df_specIP=df_specIP.drop("col1", axis=1)
        freq_new = list(range(320, 951, 1))
        int_new=interpolate.interp1d(df_specIP.Wavelength, df_specIP.Intensity)
        err_new = interpolate.interp1d(df_specIP.Wavelength, df_specIP.Error)
        stat_new = interpolate.interp1d(df_specIP.Wavelength, df_specIP.Status)
        df_intpl["Wavelength"]=freq_new
        df_intpl[ID+"_Intensity"]=int_new(freq_new)
        df_intpl[ID + "_Intensity_cal"] = df_intpl[ID + "_Intensity"] * cal.coeff.values
        df_intpl[ID+"_Error"] = err_new(freq_new)
        df_intpl[ID+"_Status"] = stat_new(freq_new)

        df_headerIP=pd.read_csv(fid,delimiter="= ",names=["col1","col2"],engine="python")
        df_intpl["DateTime"]=df_headerIP.col2[8]
        df_intpl["Lat"]=df_headerIP.col2[9]
        df_intpl["Lon"]=df_headerIP.col2[10]
        df_intpl[ID+"_Pressure"]=df_headerIP.col2[35]
        df_intpl[ID+"_InclV"]=df_headerIP.col2[25]
        df_intpl[ID+"_InclX"]=df_headerIP.col2[27]
        df_intpl[ID+"_InclY"]=df_headerIP.col2[28]

        df_SAMIP=df_SAMIP.append(df_intpl)
    return df_SAMIP


def read_sam(SAM, path_cal, ID):
    df_SAM = pd.DataFrame()
    cal = read_calibration(ID, path_cal)

    for fid in SAM:
        df_intpl = pd.DataFrame()
        df_spec=pd.read_csv(fid,delimiter=" ",names=["col1","Wavelength","Intensity","Error","Status"],skiprows=44, skipfooter=60,engine="python")
        df_spec=df_spec.drop("col1", axis=1)
        freq_new = list(range(320, 951, 1))
        int_new = interpolate.interp1d(df_spec.Wavelength, df_spec.Intensity)
        err_new = interpolate.interp1d(df_spec.Wavelength, df_spec.Error)
        stat_new = interpolate.interp1d(df_spec.Wavelength, df_spec.Status)
        df_intpl["Wavelength"] = freq_new
        df_intpl[ID+"_Intensity"] = int_new(freq_new)
        df_intpl[ID + "_Intensity_cal"]=df_intpl[ID+"_Intensity"] *cal.coeff.values
        df_intpl[ID+"_Error"] = err_new(freq_new)
        df_intpl[ID+"_Status"] = stat_new(freq_new)

        df_header=pd.read_csv(fid,delimiter="= ",names=["col1","col2"],engine="python")
        df_intpl["DateTime"]=df_header.col2[8]

        df_SAM=df_SAM.append(df_intpl)
    return df_SAM


def read_files(ID, Directory, Calibration):
    file_samip="SAMIP_"+str(ID)+"*Spectrum_Calibrated*"
    file_sam="SAM_"+str(ID)+"*Spectrum_Calibrated*"

    path_samIP = glob.glob(os.path.join(Directory, file_samip))
    path_sam = glob.glob(os.path.join(Directory, file_sam))
    if len(path_samIP):
        df_sam=read_samip(path_samIP,Calibration, ID)
        print(4)
    elif len(path_sam):
        df_sam = read_sam(path_sam,Calibration, ID)
        print(5)
    else:
        df_sam = []
    return df_sam

s= os.listdir(Directory)
matches = []
instruments = []
for f in s:
    if not re.search("_Spectrum_Calibrated_", f) == None:
        matches.append(f)
        instruments.append(re.split('_',f)[1])
instruments=list(set(set(instruments)))
print(instruments)
temp=1
for ID in instruments:
    df_sam = read_files(ID, Directory, Calibration)
    print(df_sam.shape)
    print(df_sam.tail())
    if temp==1:
        df_origin=df_sam
        temp=2
    elif temp==2:
         df_merged=pd.merge(df_origin,df_sam, on=["DateTime", "Wavelength"])
         df_origin=df_merged
df_merged.drop_duplicates()
col = df_merged.pop("DateTime")
df_merged.insert(0, col.name, col)
col = df_merged.pop("Lat")
df_merged.insert(1, col.name, col)
col = df_merged.pop("Lon")
df_merged.insert(2, col.name, col)
print(df_merged.columns.tolist())
#print(df_sam.shape, df_samip.shape,df_merged.shape)
#print(df_samip.tail(),df_sam.tail(),df_merged.tail())
merged_path = os.path.join(Directory, "merged.dat")
df_merged.to_csv(merged_path, index=False, sep="\t")
#df_samip.to_csv(r"\\niva-of5\osl-userdata$\TEG\Documents\RANSES test data\samip.csv")
#df_sam.to_csv(r"\\niva-of5\osl-userdata$\TEG\Documents\RANSES test data\sam.csv")

""""
    path_samip = glob()
    df_sampip = read_samip(path_samip)
    # merge by datetime


SAMIP2 = glob.glob(os.path.join(Directory, "SAMIP_511C*Spectrum_Calibrated*"))
read_samip(SAMIP2)
read_samip()

"""
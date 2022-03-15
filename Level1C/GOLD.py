import xarray as xr
import numpy as np 
import cartopy.crs as ccrs
import cartopy.feature as cf
import pandas as pd

def bytes_string(a):
    func = np.vectorize(lambda a: pd.to_datetime(a.decode("utf-8")))
    return xr.apply_ufunc(func, a)

def features_of_map(ax):

    ax.set_global()
    ax.gridlines(color = 'grey', linestyle = '--', crs=ccrs.PlateCarree())

    ax.add_feature(cf.NaturalEarthFeature(
                   category='cultural',
                   name='admin_1_states_provinces_lines',
                   scale='50m',
                   facecolor='none'))


    ax.add_feature(cf.COASTLINE, edgecolor='black', lw = 2) 
    ax.add_feature(cf.BORDERS, linestyle='-', edgecolor='black')
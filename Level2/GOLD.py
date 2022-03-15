import xarray as xr
import numpy as np 
import cartopy.crs as ccrs
import cartopy.feature as cf
import pandas as pd

def bytes_string(a):
    func = np.vectorize(lambda a: pd.to_datetime(a.decode("utf-8")))
                   
    return xr.apply_ufunc(func, a)

def window(data, step = 4):
    
    mrows, mcols = data.shape

    for i in range(mrows - step):
        for j in range(mcols - step):
            
            values = data[i:i+step, j:j+step]
            values[~np.isnan(values)] = np.nanmean(values)
            data[i:i+step, j:j+step] = values
            
    return data

def figure_name(files, emission):
    
    emission = emission.replace(' ', '_')
    
    if isinstance(files, list):
        
        if len(files) == 2:
            first, second = files[0], files[1]
        else:
            first, second = files[0], files[-1]
            
        start = split_filename(first)
        end = split_filename(second)
        time_start, time_end = start.time().replace(':',''), end.time().replace(':','')
        date = str(start.date(extent = False)).replace('-', '_')
        
        return f"GOLD_{start.product}_{emission}_{date}_{time_start}_{time_end}"
    else:
        start = split_filename(filename)
        if start.level == 'L2':
             return f"GOLD_{emission.upper()}_{start.level}_{str(start.date(extent = False)).replace('-', '_')}"
        


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
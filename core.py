import pandas as pd
import xarray as xr
import numpy as np 
from GOLD.utils import split_filename
import os


class GOLD:
    
    def __init__(self, filename, infile = None):
        
        self.infile = infile 
        self.filename = filename
        
        rank = split_filename(self.filename)


        self.dataset = xr.open_dataset(self.infile + self.filename)
        
        if rank.product == 'LIM':
            self.dims = ['n_lat', 'n_alt']
            
            self.dataset.coords['n_alt'] = self.dataset['GRID_ALT'].values
            self.dataset.coords['n_lat'] = self.dataset['GRID_LAT'].values

        else:
            self.dims = ['n_ns', 'n_ew']
        
        self.dataset.coords['n_wavelength'] = self.dataset['WAVELENGTH'].mean(dim = self.dims)
    

    def maximum_value(self, parameter = 'RADIANCE'):

        radiance_avg = self.dataset[
            parameter
            ].mean(dim = self.dims).values

        wavelength_avg = self.dataset['WAVELENGTH'].mean(dim = self.dims).values
        
        argmax = wavelength_avg[np.argmax(radiance_avg)]

        return self.dataset.sel(n_wavelength = argmax)
    
 
    
    def get_1356(self, mean = True):
        """
        1356 brightness map (in Rayleighs) integrates the signal from 133 to 137 nm
        """
        arr = self.dataset['n_wavelength'].values
        
        cond = (arr > 133) & (arr < 137)
        
        result_1356 = np.where(cond, arr, np.nan)
        
        result_1356 = result_1356[~np.isnan(result_1356)]
        
        self.ds = self.dataset.sel(n_wavelength = result_1356)
        
        if mean:
            return self.ds.mean(dim = 'n_wavelength', skipna = True)
        else:
            return self.ds

    
    def get_LBH(self, band = 'total'):
        """
        Individual files:
            Total LBH brightness map (in Rayleighs) integrates the signal from 137 to 155 nm
            with 148.5 to 150.0 nm masked;
        Combined files:
            LBH band 1 brightness map (in Rayleighs) integrates the signal from 140 to 148 nm; 
            LBH band 2 brightness map (in Rayleighs) integrates the signal from 150 to 160 nm. 
        """
        wavelength_values = self.dataset['n_wavelength'].values
        
        if band == 'total':
            start, end = 137, 155
        elif band == 1:
            start, end = 140, 148
        else:
            start, end = 150, 160
        
        cond = (wavelength_values > start) & (wavelength_values < end)
        
        result_LHB = np.where(cond, wavelength_values, np.nan)
        
        result_LHB = result_LHB[~np.isnan(result_LHB)]

        return self.dataset.sel(n_wavelength = result_LHB)
    
    def get_atributes(self):
    
        mirror = self.dataset.attrs['MIRROR_HEMISPHERE']

        if mirror == 'S':
            self.mirror = 'South'
        else:
            self.mirror = 'North'

        self.time_start = pd.to_datetime(self.dataset.attrs['DATE_START']).strftime("%H:%M")

        channel = self.dataset.attrs['INSTRUMENT']

        if channel == 'CHB':
            self.channel = 'Channel B'
        else:
            self.channel = 'Channel A'

        return list((self.mirror, self.time_start, self.channel))



def sep_hemispheres(infile):
    
    """
    Function which sorted files of night disk observations.
    Where combine the channels A and B in each same time 
    """
    files = os.listdir(infile)

    diff_channel = [] 

    for i in files:
        for j in files:
            date = split_filename(i).datetime == split_filename(j).datetime
            channel = split_filename(i).channel != split_filename(j).channel
            if date and channel:
                diff_channel.append([j, i])


    equal_files = files[6:19]
    equal_channel = [[equal_files[i], equal_files[i + 1]] for i in range(len(equal_files) - 1)]
    
    return equal_channel[::2] + diff_channel[:6]



def make_table(ax, filenames, infile):
    
    """
    create a table plot (bellow of map) with the informations of 
    hemisphere, TIME UTC of satellite and channel (A or B)
    
    """
    
    #columns names
    columns = ('Hemisphere', 'GOLD UTC', 'Status')

    cell_text = []

    for attrs in filenames:
        ds = GOLD(attrs, infile)
        cell_text.append(ds.get_atributes()) #get_atributes from dataset: hemisphere, time UTC and status

    tab = ax.table(cellText = cell_text, 
                   colLabels = columns, 
                   bbox = (0, -.22, 1, .21)) #xposition, yposition, width, height
    
    tab.set_fontsize(25)
    
    #remove lines from table
    for key, cell in tab.get_celld().items():
            cell.set_linewidth(0)
            
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
    


def magnetic_equator(filename = 'mag_inclination_2021.txt'):
    
    df = pd.read_csv(filename, delim_whitespace = True)

    df = pd.pivot_table(df, columns = 'lon', index = 'lat', values = 'B')
    
    return df.columns.values, df.index.values,  df.values


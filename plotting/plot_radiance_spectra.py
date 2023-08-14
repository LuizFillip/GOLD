import numpy as np
import matplotlib.pyplot as plt
from GOLD.core import GOLD
import matplotlib.gridspec as gridspec
from GOLD.utils import split_filename

def get_radiance_times(infile, files):
    rad = []
    times = []
    
    for i in range(len(files)):
        
        ds = GOLD(files[i], infile)  
        data = ds.dataset.mean(dim = ['n_ns', 'n_ew'])
        
        times.append(split_filename(files[i]).datetime)
        rad.append(data['RADIANCE'].values)
        
    wave_cont = ds.dataset.coords['n_wavelength'].values

    dat =  np.log10(np.vstack(rad))

    dat[dat < 0] = np.nan
    
    return dat, wave_cont, times

def plot_radiance_spectra(infile, files):
    
    dat, wave_cont, times = get_radiance_times(infile, files)
    fig = plt.figure(figsize = (12, 8))
    
    G = gridspec.GridSpec(4, 3)
    
    ax2 = plt.subplot(G[1:3, :])
    
    data['RADIANCE'].plot(ax = ax2, color = 'black', lw = 2)
    
    ax11 = ax2.twinx()
    
    data['CORRECTED_COUNT'].plot(ax = ax11, color = 'red', lw = 1)
    
    ax11.set(ylabel = 'Count')
    
    wavelength = [(135, 137), (140, 148), (150, 160)]
    
    colors = ['grey', 'green', 'darkgreen']
    
    labels = ['OI 1356', 'LBH band 1', 'LBH band 2']
    
    for wave, color, label in zip(wavelength, colors, labels):
        
        ax2.axvspan(wave[0], wave[1],  color = color, alpha=0.3, label = label)
    
    ax2.legend()
    
    ax2.set(ylabel = 'Radiance (rayleighs)', xlabel = 'Wavelength (nm)', 
            xticks = np.arange(min(wave_cont), max(wave_cont), 3))
    
    ax1 = plt.subplot(G[0, :], sharex=ax2)
    
    img = ax1.contourf(wave_cont, times, dat,
                       45, vmin = -1, cmap = 'coolwarm')
    
    ax1.yaxis.set_major_formatter(dates.DateFormatter('%H'))
    ax1.yaxis.set_major_locator(dates.HourLocator(interval = 2))
    
    cbar_ax = fig.add_axes([.93, 0.725, 0.015, 0.15])
    
    cb = fig.colorbar(img, ticks = np.arange(0, 5, 1), cax = cbar_ax)
    
    cb.set_label('log10 Radiance (R)')
    
    ax1.set(ylabel = 'Time UTC', title = 'GOLD 11, november 2019')
    
    plt.setp(ax1.get_xticklabels(), visible=False)
    
    plt.rcParams.update({'font.size': 12}) 
    
    
    plt.show()
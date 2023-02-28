import matplotlib.pyplot as plt
import cartopy.feature as cf
import cartopy.crs as ccrs
from core import sep_hemispheres
from utils import split_filename


fig, axes = plt.subplots(
    figsize = (10, 8),  
    subplot_kw={'projection': ccrs.Orthographic(
        central_longitude= - 47.5)}
    )


plt.subplots_adjust(wspace=0., hspace=0.1)

def plot(infile):
    
    sorted_files = sep_hemispheres(infile)[2:-2]
    
    title_date = split_filename(sorted_files[0][0]).date()
    
    emission = 'OI 1356'
    
    for ax, files in zip(axes.flat, sorted_files):
        
        features_of_map(ax)
        
        cols, idx, dat = magnetic_equator()
    
        ax.contour(cols, idx, dat, 1, linewidths = 2, color = 'k',
                           transform = ccrs.PlateCarree())
    
        for filename in files:
    
            ds = GOLD(filename, infile).get_1356()
    
            lats = ds['REFERENCE_POINT_LAT'].values
            lons = ds['REFERENCE_POINT_LON'].values
            data = ds['RADIANCE'].values 
    
    
            data[(lats > 50) | (lats < -27)] = np.nan
    
            cmap = 'seismic'
            values = 50
    
            img  = ax.contourf(lons, lats, data, values,
                                   cmap = cmap, transform = ccrs.PlateCarree())
    
         
            cbar_ax = fig.add_axes([.08, 0.2, 0.02, 0.6]) #xposition, yposition, ticknness, height
    
            cb = fig.colorbar(img, cax=cbar_ax, ticklocation='left') 
    
            cb.set_label(f'{emission} (Rayleighs/nm)') 
    
            make_table(ax, files, infile)
    
    fig.suptitle('GOLD \n' + title_date, y = .92)    
    
    

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs 
import GEO as gg 
from pathlib import Path
from tqdm import tqdm 

def decode_time_coord(ds: xr.Dataset, time_var: str = "scan_start_time") -> xr.Dataset:
    if time_var not in ds:
        return ds

    values = ds[time_var].values
    if values.dtype.kind == "S":
        values = np.array([v.decode("utf-8") for v in values])

    scan_time = pd.to_datetime(values)
    return ds.assign_coords(scan_time=("nscans", scan_time))



 
def get_lat_lon2(ds):
    lat_candidates = ["lat", "latitude", "GRID_LAT", "glat"]
    lon_candidates = ["lon", "longitude", "GRID_LON", "glon"]

    lat_name = next((v for v in lat_candidates if v in ds.variables), None)
    lon_name = next((v for v in lon_candidates if v in ds.variables), None)

    if lat_name is None or lon_name is None:
        raise KeyError("Latitude/Longitude não encontradas.")

    return ds[lat_name], ds[lon_name]

def plot_square_area(
        
        ax, 
        lat_min, 
        lon_min,
        lat_max, 
        lon_max, 
        name):
    gg.plot_square_area(
            ax, 
            lat_min, 
            lon_min,
            lat_max, 
            lon_max,  
            center_dot = True
            )
   
    c_lon = (lon_max + lon_min) / 2
    c_lat = (lat_max + lat_min) / 2
    ax.text(c_lon, c_lat, name)


def plot_raw_vs_smoothed(
    ds: xr.Dataset,
    parameter: str,
    scan_index: int = 0,
    smooth_size: int = 6,
    cmap: str = "viridis",
    central_longitude: float = -47.5,
    percentile_limits=(1, 99),
):
    ds = decode_time_coord(ds)

    ds_scan = ds.isel(nscans=scan_index)
    raw_da = ds_scan[parameter]
    raw = np.asarray(raw_da.values, dtype=float)

    # mascara infinitos
    raw[~np.isfinite(raw)] = np.nan

    lat, lon, lat_name, lon_name = get_lat_lon(ds, scan_index=scan_index)
    lat2d, lon2d = ensure_2d_latlon(lat, lon, raw.shape)
 
    p1, p99 = percentile_limits
    vmin = np.nanpercentile(raw, p1)
    vmax = np.nanpercentile(raw, p99)
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

 
    fig, ax = plt.subplots(
        figsize = (10, 10), 
        dpi = 300,  
        subplot_kw = 
        {'projection': ccrs.PlateCarree()}
        )
    
    lat_lims = dict(min = -50, max = 50, stp = 10)
    lon_lims = dict(min = -90, max = -20, stp = 10) 

    gg.map_attrs( 
        ax, 
        lat_lims = lat_lims, 
        lon_lims = lon_lims
        )
    
    ax.contourf(
        lon2d,
        lat2d,
        raw,
        cmap=cmap,
        norm=norm,
        transform=ccrs.PlateCarree(),
  
    )
 

    if "scan_time" in ds.coords:
        t = pd.Timestamp(ds["scan_time"].isel(nscans=scan_index).values)
        fig.suptitle(f"{parameter} | {t:%Y-%m-%d %H:%M:%S UTC}", y=0.98)
    else:
        fig.suptitle(f"{parameter} | scan {scan_index}", y=0.98)

    return ax


 



def get_values_in_sites(ds_scan):
    lat, lon = get_lat_lon2(ds_scan)
    areas = {
        'BOA' : [(-2, 6), (-65, -58)], 
        'SMS' : [(-33, -27), (-58, -50)], 
        'CAJ': [(-25, -19), (-53, -44)], 
        'SLZ': [(-10, 0), (-49, -42)], 
        'CAR': [ (-10, -5), (-39, -34)]
        }
    
    sub_vls = {'mean': [],'max': [], 'site': [] }
    
    index = []
    for name, coord in areas.items():
        
        lat_min, lat_max = coord[0]
        lon_min, lon_max = coord[1]
        
        mask = (
            (lon >= lon_min) & (lon <= lon_max) &
            (lat >= lat_min) & (lat <= lat_max)
        )
    
        subset = ds_scan["on2"].where(mask)
        
        sub_vls['mean'].append(float(subset.mean(skipna=True)))
        sub_vls['max'].append(float(subset.max(skipna=True)))
        sub_vls['site'].append(name.lower())
        index.append(pd.Timestamp(ds_scan["scan_time"].values))
     
    
    return pd.DataFrame(sub_vls, index = index)

def get_avg_by_day(ds):
    ds = decode_time_coord(ds)
    out = []
    for scan_index in ds.nscans.values:
    
        out.append(get_values_in_sites(ds.isel(nscans=scan_index)))
        
        
    return pd.concat(out).dropna()
    
def run_gold_on2():
    infile = Path(r"D:\database\gold")
    files = sorted(infile.glob("*.nc"))
    
    out = []
    for file in tqdm(files):
        try:
            out.append(get_avg_by_day(xr.open_dataset(file)))
        except:
            continue
    return pd.concat(out)
    

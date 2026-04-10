import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import GEO as gg 
from pathlib import Path
from scipy.ndimage import generic_filter


def decode_time_coord(ds: xr.Dataset, time_var: str = "scan_start_time") -> xr.Dataset:
    if time_var not in ds:
        return ds

    values = ds[time_var].values
    if values.dtype.kind == "S":
        values = np.array([v.decode("utf-8") for v in values])

    scan_time = pd.to_datetime(values)
    return ds.assign_coords(scan_time=("nscans", scan_time))


def smooth_boxmean(arr2d: np.ndarray, size: int = 6) -> np.ndarray:
    arr = np.asarray(arr2d, dtype=float)

    if arr.ndim != 2:
        raise ValueError("A suavização espera um array 2D.")

    if size <= 1:
        return arr.copy()

    return generic_filter(arr, function=np.nanmean, size=size, mode="nearest")


def get_lat_lon(ds: xr.Dataset, scan_index: int = 0):
    """
    Procura automaticamente variáveis plausíveis de latitude/longitude.
    """
    lat_candidates = ["lat", "latitude", "GRID_LAT", "glat", "lats"]
    lon_candidates = ["lon", "longitude", "GRID_LON", "glon", "lons"]

    lat_name = next((v for v in lat_candidates if v in ds.variables), None)
    lon_name = next((v for v in lon_candidates if v in ds.variables), None)

    if lat_name is None or lon_name is None:
        raise KeyError(
            "Não encontrei latitude/longitude reais no arquivo. "
            "Use print(ds.variables) para ver os nomes corretos."
        )

    lat = ds[lat_name]
    lon = ds[lon_name]

    # Se lat/lon dependem de nscans, seleciona o scan
    if "nscans" in lat.dims:
        lat = lat.isel(nscans=scan_index)
    if "nscans" in lon.dims:
        lon = lon.isel(nscans=scan_index)

    return lat.values, lon.values, lat_name, lon_name


def add_map_features(ax):
    ax.coastlines(linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)
    ax.add_feature(cfeature.LAND, alpha=0.15)
    ax.add_feature(cfeature.OCEAN, alpha=0.08)


def ensure_2d_latlon(lat, lon, data_shape):
    """
    Garante que lat/lon fiquem compatíveis com a matriz de dados.
    """
    lat = np.asarray(lat)
    lon = np.asarray(lon)

    if lat.shape == data_shape and lon.shape == data_shape:
        return lat, lon

    if lat.ndim == 1 and lon.ndim == 1:
        lon2d, lat2d = np.meshgrid(lon, lat)
        if lat2d.shape == data_shape and lon2d.shape == data_shape:
            return lat2d, lon2d

    raise ValueError(
        f"Formato incompatível: data={data_shape}, lat={lat.shape}, lon={lon.shape}"
    )

def get_lat_lon2(ds):
    lat_candidates = ["lat", "latitude", "GRID_LAT", "glat"]
    lon_candidates = ["lon", "longitude", "GRID_LON", "glon"]

    lat_name = next((v for v in lat_candidates if v in ds.variables), None)
    lon_name = next((v for v in lon_candidates if v in ds.variables), None)

    if lat_name is None or lon_name is None:
        raise KeyError("Latitude/Longitude não encontradas.")

    return ds[lat_name], ds[lon_name]

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


 
infile = Path(r"D:\database\gold")
files = sorted(infile.glob("*.nc"))

file = files[3]
ds = xr.open_dataset(file)

scan_index = 14
ds_scan = ds.isel(nscans=scan_index)

lat, lon = get_lat_lon2(ds_scan)



ax = plot_raw_vs_smoothed(
    ds=ds,
    parameter="on2",
    scan_index=scan_index,
    smooth_size=6,
    cmap="viridis", 
)

areas = {
    'BOA' : [(-2, 6), (-65, -58)], 
    'SMS' : [(-33, -27), (-58, -50)], 
    'CAJ': [(-25, -19), (-53, -44)], 
    'SLZ': [(-10, 0), (-49, -42)], 
    'CAR': [(-40, -35), (-10, -8)]
    }


for name, coord in areas.items():
    
    lat_min, lat_max = coord[0]
    lon_min, lon_max = coord[1]
    
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
        
    
    mask = (
        (lon >= lon_min) & (lon <= lon_max) &
        (lat >= lat_min) & (lat <= lat_max)
    )

    subset = ds_scan["on2"].where(mask)

    print("Mean:", float(subset.mean(skipna=True)))
    print("Max :", float(subset.max(skipna=True)))
 

ds = decode_time_coord(ds)

t = pd.Timestamp(ds["scan_time"].isel(nscans=scan_index).values)

t 
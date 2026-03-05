# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 09:39:20 2026

@author: Luiz
"""

import numpy as np
import xarray as xr
import matplotlib.dates as mdates
from scipy.ndimage import uniform_filter, generic_filter

def split_hemispheres_mean(ds: xr.Dataset, parameter: str, spatial_dims=("nlats", "nlons")):
    """
    Retorna duas séries (DataArray) com média espacial por scan:
      north = nscans 0,2,4,...
      south = nscans 1,3,5,...
    """
    da = ds[parameter]
    north = da.isel(nscans=slice(0, None, 2)).mean(dim=spatial_dims, skipna=True)
    south = da.isel(nscans=slice(1, None, 2)).mean(dim=spatial_dims, skipna=True)
    return north, south


def plot_hemispheres_timeseries(ax, ds: xr.Dataset, parameter="radiance_oi_1356"):
    north, south = split_hemispheres_mean(ds, parameter)

    # xarray já plota com o coord nscans se for datetime
    north.plot(ax=ax, color="red", lw=2, label="North")
    south.plot(ax=ax, color="black", lw=2, label="South")
    ax.legend(frameon=False)

    attrs = ds[parameter].attrs
    title = attrs.get("FIELDNAM", parameter)
    ylabel = attrs.get("LABLAXIS", attrs.get("UNITS", ""))

    ax.set_title(title)
    ax.set_xlabel("Time UTC")
    ax.set_ylabel(ylabel)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))


def smooth_boxmean(arr2d: np.ndarray, size: int = 6, nan_aware: bool = True) -> np.ndarray:
    """
    Suavização por média em janela size x size.

    - nan_aware=True: usa nanmean via generic_filter (mais caro, mas respeita NaN)
    - nan_aware=False: uniform_filter (muito rápido, mas NaNs contaminam)
    """
    arr = np.asarray(arr2d, dtype=float)

    if size <= 1:
        return arr.copy()

    if nan_aware:
        # aplica nanmean em janelas
        return generic_filter(arr, function=np.nanmean, size=size, mode="nearest")
    else:
        return uniform_filter(arr, size=size, mode="nearest")
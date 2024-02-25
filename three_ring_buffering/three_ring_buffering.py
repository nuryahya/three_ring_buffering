"""Main module."""
#Import libs
from pathlib import Path
import pandas as pd
import geopandas as gp
from pyproj import CRS

def create_three_buffer_rings(gdf,dist_min,dist_mid,dist_max,per_min,per_mid,per_max):
    '''Creates Three buffer rings around a Polyline 
    and assign score value to each ring .
    Parameters:
    ===========
    gdf = Geopandas GeoDataframe full path (Geometry Type = Line)
    dist_min = the inner layer distance from center line, 
    dist_mid = The Second Layer Distance from center line,
    dist_max = The Third Layer Distance from center line,
    per_min = Value to be given for the inner layer ,
    per_mid = Value to be given for the second layer,
    per_max = Value to be given for the third layer'''
    
    # Exclude both MISSING VALUES and EMPTY FEOMETRY
    gdf = gdf.loc[gdf.geometry.isna()== False] # missing values will be excluded
    gdf = gdf.loc[gdf.geometry.is_empty== False] # Empty geometries will be excluded
    
    # Buffer the inner ring 
    a0 = gdf['geometry'].buffer(distance = dist_min)
    a0 = gp.GeoDataFrame(a0)
    a0['geometry']  =  a0[0]
    a0.set_crs(epsg=20137, inplace=True)
    a0['D0_COL']= dist_min
    a0['V0_COL'] = per_min
    a0['D'] = 1
    a0 = a0.dissolve(by = 'D',aggfunc='first', as_index=True)
    
    # Buffer the first ring 
    a1 = gdf['geometry'].buffer(distance = dist_mid)
    a1 = gp.GeoDataFrame(a1)
    a1['geometry']  =  a1[0]
    a1.set_crs(epsg=20137, inplace=True)
    a1['D'] = 1
    a1 = a1.dissolve(by = 'D',aggfunc='first', as_index=True)
    
    # Buffer the second ring 
    a2 = gdf['geometry'].buffer(distance = dist_max)
    a2 = gp.GeoDataFrame(a2)
    a2['geometry']  =  a2[0]
    a2.set_crs(epsg=20137, inplace=True)
    a2['D'] = 1
    a2 = a2.dissolve(by = 'D',aggfunc='first', as_index=True)
    
    a0_symmDiff_a1 = gp.overlay(a0,a1,how='symmetric_difference') #.... R1
    a0_symmDiff_a1['D1_COL']= dist_mid 
    a0_symmDiff_a1['V1_COL'] = per_mid

    a1_symmDiff_a2 = gp.overlay(a1,a2,how='symmetric_difference') #.... R2
    a1_symmDiff_a2['D2_COL']= dist_max  
    a1_symmDiff_a2['V2_COL'] = per_max

    a0_r1 = gp.overlay(a0,a0_symmDiff_a1,how = 'union' , keep_geom_type=True )
    a0_r1_r2 = gp.overlay(a0_r1,a1_symmDiff_a2,how = 'union', keep_geom_type=True )
    
    three_buffer_rings = a0_r1_r2.loc[a0_r1_r2.index[:],['D0_COL_1','V0_COL_1','D1_COL','V1_COL','D2_COL','V2_COL','geometry']]
    three_buffer_rings = three_buffer_rings.explode()

    three_buffer_rings.loc[three_buffer_rings.V0_COL_1.isna()== True,'V0_COL_1'] = 0
    three_buffer_rings.loc[three_buffer_rings.V1_COL.isna()== True,'V1_COL'] = 0
    three_buffer_rings.loc[three_buffer_rings.V2_COL.isna()== True,'V2_COL'] = 0

    three_buffer_rings['V_COL'] = three_buffer_rings.V2_COL
    three_buffer_rings.loc[three_buffer_rings.V1_COL != 0,'V_COL'] = three_buffer_rings.V1_COL
    three_buffer_rings.loc[three_buffer_rings.V0_COL_1 != 0,'V_COL'] = three_buffer_rings.V0_COL_1
    
    return three_buffer_rings
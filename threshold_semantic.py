import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import substring


def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i + 1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]


def cut_piece(line, distance, lgth):
    """ From a linestring, this cuts a piece of length lgth at distance.
    Needs cut(line,distance) func from above ;-)
    """
    precut = cut(line, distance)[1]
    result = cut(precut, lgth)[0]
    return result


def thresh_length(run_width):
    if run_width == 60.96:
        return 45.9
    else:
        return 46.472

def thresh_spacing_vert(run_width):
    if run_width == 60.96:
        return 6.2
    else:
        return 5.8

def thresh_spacing_horiz(run_width):
    if run_width == 60.96:
        return 2.4
    else:
        return 1.8


if __name__ == '__main__':
    # centerline
    # rnw_centerlines = gpd.GeoDataFrame.from_file(
    # r"C:\Users\sridene\Desktop\touchdownLights\Blackshark_20210301_01\AMDB\KSJC\shapefiles"
    # "\AM_PaintedCenterline.shp")
    rnw_centerlines = gpd.GeoDataFrame.from_file(r"C:\20220329_7airports\AM_PaintedCenterline.shp")

    rnw_element = gpd.GeoDataFrame.from_file(r"C:\20220329_7airports\AM_RunwayElement.shp")
    rnw_elmnt = rnw_element.drop_duplicates(subset=['idrwy'], keep='first')
    listp = []
    listp1 = []
    listp2 = []
    listp3 = []
    rnw_centerlines.to_crs(32616, inplace=True)
    rnw_element.to_crs(32616, inplace=True)
    # get line coords
    for row in rnw_centerlines.itertuples():
        # width runway
        run_width = rnw_elmnt[rnw_elmnt['idrwy'] == row.idrwy]['width'].item()
        par = (run_width/2) - thresh_spacing_horiz(run_width)
        coords = [coords for coords in list(row.geometry.coords)]
        first_coord, last_coord = [coords[i] for i in (0, -1)]
        sp = Point(first_coord)
        ep = Point(last_coord)
        linec = LineString([sp, ep])
        # create offsets
        line = LineString(linec.parallel_offset(par, 'right'))
        line1 = LineString(reversed(linec.parallel_offset(par, 'right').coords[:]))
        linerev = LineString(reversed(linec.parallel_offset(par, 'left').coords[:]))
        linerev1 = LineString(linec.parallel_offset(par, 'left'))
        # lines.append(gdf)
        print('thresh length ', thresh_length(run_width))
        line_cut = cut_piece(line, thresh_spacing_vert(run_width), thresh_length(run_width))
        line_cut1 = cut_piece(line1, thresh_spacing_vert(run_width), thresh_length(run_width))
        linerev_cut = cut_piece(linerev, thresh_spacing_vert(run_width), thresh_length(run_width))
        linerev_cut1 = cut_piece(linerev1, thresh_spacing_vert(run_width), thresh_length(run_width))
        offsets = [line_cut, linerev_cut, line_cut1, linerev_cut1]
        '''for i in offsets:
            gdf = gpd.GeoDataFrame(index=[0], crs='epsg:32610', geometry=[i])
            lines.append(gdf)'''
        pointList = list(linerev_cut.coords) + list(reversed(line_cut.coords))
        ptslst1 = list(linerev_cut1.coords) + list(reversed(line_cut1.coords))
        p = Polygon([[p[0], p[1]] for p in pointList])
        gdf = gpd.GeoDataFrame(index=[0], crs='epsg:32616', geometry=[p])
        listp.append(gdf)
        p1 = Polygon([[p[0], p[1]] for p in ptslst1])
        gdf1 = gpd.GeoDataFrame(index=[0], crs='epsg:32616', geometry=[p1])
        listp1.append(gdf1)

    gdf2 = gpd.GeoDataFrame(pd.concat(listp + listp1 + listp2 + listp3, ignore_index=True))
    gdf2 = gdf2.assign(feattype=1006, source='Blackshark')
    gdf2.to_file('thresh-jepp.shp', driver="ESRI Shapefile")

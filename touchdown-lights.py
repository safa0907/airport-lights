import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, MultiPoint, mapping
from shapely.ops import substring
import itertools


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


if __name__ == '__main__':
    gdf = gpd.GeoDataFrame.from_file(r"C:\Users\sridene\Desktop\touchdownLights\Blackshark_20210301_01\AMDB\KSJC"
                                     r"\shapefiles\AM_PaintedCenterline.shp")
    gdf.to_crs(32610, inplace=True)

    # get line coords
    lines_list = []
    linesrev_list = []
    touchdown_points_right = []
    linesright = []
    touchdown_points_left = []
    linesleft = []
    touchdown_light = []
    centerline_points = []
    for row in gdf.itertuples():
        coords = [coords for coords in list(row.geometry.coords)]
        first_coord, last_coord = [coords[i] for i in (0, -1)]
        sp = Point(first_coord)
        ep = Point(last_coord)
        line = LineString([sp, ep])
        line_rev = LineString([ep, sp])
        linesrev_list.append(line_rev)
        lines_list.append(line)

    for line in lines_list:
        # create offsets right
        linerev1r = LineString(reversed(line.parallel_offset(10.5, 'right').coords[:]))
        linerev2r = LineString(reversed(line.parallel_offset(9, 'right').coords[:]))
        linerev3r = LineString(reversed(line.parallel_offset(12, 'right').coords[:]))

        line1r = LineString(line.parallel_offset(10.5, 'right'))
        line2r = LineString(line.parallel_offset(9, 'right'))
        line3r = LineString(line.parallel_offset(12, 'right'))

        line1_cutr = cut(line1r, 1000)[0]
        line2_cutr = cut(line2r, 1000)[0]
        line3_cutr = cut(line3r, 1000)[0]
        linerev1_cutr = cut(linerev1r, 1000)[0]
        linerev2_cutr = cut(linerev2r, 1000)[0]
        linerev3_cutr = cut(linerev3r, 1000)[0]
        # offsets_cutr = [line1_cutr, line2_cutr, line3_cutr]
        offsets_cutr = [linerev1_cutr, line1_cutr, linerev2_cutr, line2_cutr, linerev3_cutr, line3_cutr]
        # create regular points on a line
        for j in offsets_cutr:
            gdataframe1 = gpd.GeoDataFrame(index=[0], crs='epsg:32610', geometry=[j])
            multip = MultiPoint()
            for i in np.arange(30.4, 900, 30.4):
                sub = substring(j, i, i + 30.4)
                multip = multip.union(sub.boundary)
                gdf = gpd.GeoDataFrame(index=[0], crs='epsg:32610', geometry=[multip])
            touchdown_points_right.append(gdf)
            linesright.append(gdataframe1)
    for line in lines_list:
        # touchdown lights left
        # create offsets left
        line1l = LineString(line.parallel_offset(10.5, 'left'))
        line2l = LineString(line.parallel_offset(9, 'left'))
        line3l = LineString(line.parallel_offset(12, 'left'))

        linerev1l = LineString(reversed(line.parallel_offset(10.5, 'left').coords[:]))
        linerev2l = LineString(reversed(line.parallel_offset(9, 'left').coords[:]))
        linerev3l = LineString(reversed(line.parallel_offset(12, 'left').coords[:]))
        line1_cutl = cut(line1l, 1000)[0]
        line2_cutl = cut(line2l, 1000)[0]
        line3_cutl = cut(line3l, 1000)[0]
        linerev1_cutl = cut(linerev1l, 1000)[0]
        linerev2_cutl = cut(linerev2l, 1000)[0]
        linerev3_cutl = cut(linerev3l, 1000)[0]
        # offsets_cutl = [line1_cutl, line2_cutl, line3_cutl]
        offsets_cutl = [linerev1_cutl, linerev2_cutl, linerev3_cutl, line1_cutl, line2_cutl, line3_cutl]
        # create regular points on a line
        for j in offsets_cutl:
            multip = MultiPoint()
            gdataframe = gpd.GeoDataFrame(index=[0], crs='epsg:32610', geometry=[j])
            for i in np.arange(30, 900, 30):
                sub = substring(j, i, i + 30)
                multip = multip.union(sub.boundary)
                gdf = gpd.GeoDataFrame(index=[0], crs='epsg:32610', geometry=[multip])
            touchdown_points_left.append(gdf)
            linesleft.append(gdataframe)
    # touchdown lights
    # centerline points
    for j in lines_list:
        multip = MultiPoint()
        for i in np.arange(30, 900, 30):
            sub = substring(j, i, i + 30)
            multip = multip.union(sub.boundary)
            gdf = gpd.GeoDataFrame(index=[0], crs='epsg:32610', geometry=[multip])
        centerline_points.append(gdf)
    gdfz = gpd.GeoDataFrame(pd.concat(centerline_points, ignore_index=True))

    touchdown_lights = touchdown_points_left + touchdown_points_right
    lst_lines = linesleft + linesright
    gdf2 = gpd.GeoDataFrame(pd.concat(touchdown_lights, ignore_index=True))
    touchdown_lights = gdf2.explode(ignore_index=True)
    gdf3 = gpd.GeoDataFrame(pd.concat(lst_lines, ignore_index=True))
    # Multipoints to points

    touchdown_lights.to_file('tdz-lights.gpkg', driver="GPKG")
    # gdfz.to_file('centerlinespoints326311.gpkg', driver="GPKG")
    # gdf3.to_file('touchdownlines326311.gpkg', driver="GPKG")

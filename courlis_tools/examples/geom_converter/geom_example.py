from sys import exit

from courlis_tools.core import geom


try:
    # Read ST file
    geometry = geom.Geometry('Bief_1.ST')

    # Save as ST file
    geometry.save_ST('Bief_1_out.ST')

    # Add some deposit layers
    for section in geometry:
        section.add_layer('sable', 1.0)
        section.add_layer('vase', 2.0)

    # Export as georefC
    geometry.save_courlis('Bief_1_with-2-layers.georefC')

    # Export some shapefiles
    geometry.export_trace_shp('traces.shp')
    geometry.export_limits_shp('limits.shp')

except geom.GeometryRequestException as e:
    print(e)
    exit(1)

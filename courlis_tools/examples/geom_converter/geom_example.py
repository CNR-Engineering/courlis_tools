from sys import exit

from courlis_tools.core import geom


try:
    # Read ST file
    geometry = geom.Geometry('Bief_1.ST')

    # Save as ST file
    geometry.save_ST('Bief_1_out.ST')

    # Add some constant deposit layers
    geometry.add_constant_layer('mud', 1.0)
    geometry.add_constant_layer('sand', 2.0)
    geometry.add_linear_interp_layer('gravel', [15200, 154000, 158000], [0.5, 3, 0])

    # Export as georefC
    geometry.save_courlis('Bief_1_with-2-layers.georefC')

    # Export some shapefiles
    geometry.save_shp('Bief_1_with-2-layers.shp')
    geometry.export_trace_shp('traces.shp')
    geometry.export_limits_shp('limits.shp')

except geom.GeometryRequestException as e:
    print(e)
    exit(1)

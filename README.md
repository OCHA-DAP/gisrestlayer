## GISRestLayer

### Short description
It's a tool for managing the transformation process of GIS data files ( geojson, kml, kmz, zipped shapefiles ) into a Postgres / PostGIS database. 
From there, the GIS data can be served by using the [PGRestAPI server ( aka Spatial Server )](https://github.com/spatialdev/PGRestAPI).
The gained advantages is that the PGRestAPI can serve:

*  [Mapbox Vector Tiles](https://github.com/mapbox/vector-tile-spec)   
*  simplfied geometries depending on zoom level

### How it works

1.  User uploads GIS data file on CKAN
1.  GISRestLayer is asynchronously notified about the new file
1.  GISRestLayer then delegates all the import process tasks to Redis Queue ( and it’s workers )
The worker code is part of this repository in: `importapi.tasks.create_preview`
1.  The worker downloads the data
1.  Uses [ogr2ogr](http://www.gdal.org/ogr2ogr.html) to import it in PostGIS
  *  after this is finished PGRestAPI can already start serving tiles 
1.  Notifies CKAN that the task is complete. If successful, CKAN can show the user a preview of the data
  
  
### Notes

*  We're using a slightly modified fork of PGRestAPI <https://bitbucket.org/agartner/hdx-pgrestapi> . 
It allows serving new layers without restarting the server
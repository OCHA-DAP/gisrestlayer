|Tests with docker-compose|

.. |Tests with docker-compose| image:: https://github.com/OCHA-DAP/gisrestlayer/workflows/Tests%20with%20docker-compose/badge.svg

README - HDX JOB PROCESSOR
==========================

Name
----
HDX JOB PROCESSOR, formerly known as "GISRestLayer" or "Gislayer"

Short description
-----------------

This tool is evolving from just providing a way to asynchronously run the Geopreview process to a more general tool for
asynchronously executing tasks for HDX (CKAN).
For now it just deals with 2 tasks:

   #. `Geopreview Processing`_
   #. `Sending Analytics Events`_


The tools is based on `Redis Queue <http://python-rq.org/>`_

Geopreview Processing
---------------------

This manages the transformation process of GIS data files ( geojson, kml, kmz, zipped shapefiles ) into a Postgres / PostGIS database.
From there, the GIS data can be served by using the `PGRestAPI server ( aka Spatial Server ) <https://github.com/spatialdev/PGRestAPI>`_.
The gained advantages is that the PGRestAPI can serve:

* `Mapbox Vector Tiles <https://github.com/mapbox/vector-tile-spec>`_
* simplfied geometries depending on zoom level

How geopreview works
++++++++++++++++++++

#. User uploads GIS data file on CKAN
#. HDX JOB PROCESSOR is notified about the new file
#. | GISRestLayer then delegates all the import process tasks to Redis Queue ( and it’s workers ). The name of the queue **geo_q** .
     The worker code is part of this repository in: :code:`importapi.tasks.create_preview`
#. The worker downloads the data
#. Uses `ogr2ogr <http://www.gdal.org/ogr2ogr.html>`_ to import it in PostGIS
    *  after this is finished PGRestAPI can already start serving tiles
#. Notifies CKAN that the task is complete. If successful, CKAN can show the user a preview of the data


Notes
+++++

* We're using a slightly modified fork of PGRestAPI `<https://bitbucket.org/agartner/hdx-pgrestapi>`_
  It allows serving new layers without restarting the server

Running the redis queue worker for geopreview
+++++++++++++++++++++++++++++++++++++++++++++

The code below needs to be run in the folder where the python code is

.. code-block:: bash

   ./hdxrq.py worker --url redis://redis_ip:redis_port/1 --worker-ttl 600 geo_q

Please note that *rqworker* was replaced by *./hdxrq.py worker*. More info can be found `here <LOGGING.rst>`_

Sending Analytics Events
------------------------

This manages the sending of data to analytics servers like Mixpanel or Google Analytics.

How analytics work
++++++++++++++++++

#. CKAN sends all the event metadata to HDX JOB PROCESSOR
#. HDX JOB PROCESSOR then creates tasks in Redis Queue in a queue called **analytics_q** .
#. Workers then send the information to analytics servers.
   The worker code is part of this repository in: :code:`analyticsapi.tasks.send_event`

Running the redis queue worker for analytics
++++++++++++++++++++++++++++++++++++++++++++

The code below needs to be run in the folder where the python code is

.. code-block:: bash

   ./hdxrq.py worker --url redis://redis_ip:redis_port/1 --worker-ttl 600 analytics_q

Please note that *rqworker* was replaced by *./hdxrq.py worker*. More info can be found `here <LOGGING.rst>`_

Generating events for the event bus
+++++++++++++++++++++++++++++++++++

The "events" API is used for detecting changes in datasets and transforming them in events which are pushed to the event bus.
Read more about this `here <eventapi/README.rst>`_

Scheduling feature (deprecated)
+++++++++++++++++++++++++++++++

The HDX Job Processor has support for scheduling (though it's unused at the moment). To read more about it go
`here <schedulerapi/docs/README.rst>`_


Logging
+++++++

To read more about how logging is configured, look
`here <LOGGING.rst>`_
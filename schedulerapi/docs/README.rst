SCHEDULING JOBS
===============

#. `Introduction`_
#. `Usage`_
#. `Setup`_

Introduction
------------
The project now supports scheduling jobs via the `Python Redis Queue (RQ) <http://python-rq.org/>`_. While RQ doesn't support job scheduling by itself there is the `RQ Scheduler <https://github.com/ui/rq-scheduler>`_  project that adds scheduling support.

Usage
-----

For now there are 2 main API endpoints for using this:

* /api/scheduler/add_job - schedules a job. Please see :func:`~schedulerapi.scheduler_api.add_job`
* /api/scheduler/list_jobs - lists existing jobs that are waiting to be scheduled. Please see :func:`~schedulerapi.scheduler_api.list_jobs`


Setup
-----

#. rw-scheduler was added as a dependency to the project so make sure that `pip install -r requirements.txt` is run in both the layer container and in the worker container.
#. The scheduler module needs a daemon that can connect to redis.
    * :code:`rqscheduler --host 172.17.42.1 --port 9016 --db 1`
#. Changes to the the configuration **app.conf** / **GIS_REST_LAYER_CONF**:
    *  CKAN_API_BASE_URL = 'http://CKAN_SERVER:PORT/api/action'
    *  RESOURCE_ID_LIST_API and RESOURCE_UPDATE_API need to be removed from the configuration file
#. changes to **logging.conf** to include schedulerapi
#. a worker needs to listen on a new task queue: **default_scheduler_q**
LOGGING
=======

There are actually 2 processes that start from the same code base:

#. The flask app that just puts jobs in redis queue

   *  configured by deafult via `logging.conf <logging.conf>`_
   *  can be overridden from the applications configuration file via the *LOGGING_CONF_FILE* property

#. The redis worker

   *  configured by default via `logging.conf <logging.conf>`_
   *  can be overridden via *LOGGING_CONF_FILE* env variable
   *  we created a **new wrapper script** `hdxrq.py <hdxrq.py>`_ for starting the worker: **./hdxrq.py worker** instead of **rqworker**.
      This allows us to configure logging before the worker starts. The 

By default, as specified in *logging.conf*, the logs are stored in */var/log/gis.log* in both of the above cases.

Below is a sample line from the log:

.. code-block:: bash

   2020-07-09 11:05:10,791 INFO  [rq.worker:468] RQ worker 'rq:worker:hdx-local-gisworker.169' started, version 0.13.0
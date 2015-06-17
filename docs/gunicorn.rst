Gunicorn
========

Starting from v0.0.6, `Burp-UI`_ supports `Gunicorn`_ in
order to handle multiple users simultaneously.

You need to install ``gunicorn`` and ``eventlet``:

::

    pip install eventlet
    pip install gunicorn

You will then be able to launch `Burp-UI`_ this way:

::

    gunicorn -k eventlet -w 4 'burpui:init(conf="/path/to/burpui.cfg")'

When using ``gunicorn``, the command line options are not available. Instead,
run the `Burp-UI`_ ``init`` method directly. Here are the parameters you can
play with:

- conf: Path to the `Burp-UI`_ configuration file
- debug: Whether to run `Burp-UI`_ in debug mode or not to get some extra logging
- logfile: Path to a logfile in order to log `Burp-UI`_ internal messages


.. _Gunicorn: http://gunicorn.org/
.. _Burp-UI: https://git.ziirish.me/ziirish/burp-ui
=============
exec-wrappers
=============

.. image:: https://travis-ci.org/gqmelo/exec-wrappers.svg?branch=master
    :target: https://travis-ci.org/gqmelo/exec-wrappers
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/gqmelo/exec-wrappers?branch=master
    :target: https://ci.appveyor.com/project/gqmelo/exec-wrappers/branch/master
    :alt: See Build Status on AppVeyor

A tool to create wrappers around executable files

``exec-wrappers`` is useful whenever you need a single executable file, but have to do some setup
before executing it.


Features
--------

* TODO


Requirements
------------

* TODO


Installation
------------


Usage
-----

There are some built-in templates to create wrappers.

Creating `conda`_ wrappers:

.. code-block:: bash

    $ create_wrappers  -t conda -b ~/miniconda/envs/test/bin -d /tmp/conda_wrappers
    --conda-env-dir ~/miniconda/envs/test

This will create in ``/tmp/conda_wrappers`` a wrapper for each executable found in
``~/miniconda/envs/test/bin``.
So if you run the python wrapper:

.. code-block:: bash

    $ /tmp/conda_wrappers/python -c "import sys; print(sys.executable)"
    /home/username/miniconda/envs/test/bin/python

It will actually activate the conda environment and set necessary variables, and then execute the
real ``python`` interpreter. So you can use the wrapper to configure you IDE, for example.

Also a ``run-in`` script will be created, which you can use to run any arbitrary command:

.. code-block:: bash

    $ /tmp/conda_wrappers/run-in bash -c 'echo $CONDA_DEFAULT_ENV'
    /home/username/miniconda/envs/test

It is also possible to chain different wrappers:

.. code-block:: bash

    $ create-wrappers -b /tmp/conda_wrappers -d /tmp/schroot_wrappers --schroot-name centos5-session -t schroot

This will create wrappers that will enter the specified schroot and run the conda wrapper, which
will activate the environment and execute the given command. Of course you need to have an
existing schroot properly configured and the right mount points.


License
-------

Distributed under the terms of the `MIT`_ license, "exec-wrappers" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/gqmelo/exec-wrappers/issues
.. _`conda`: http://conda.pydata.org/miniconda.html

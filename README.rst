=============
exec-wrappers
=============

.. image:: https://travis-ci.org/gqmelo/exec-wrappers.svg?branch=master
    :target: https://travis-ci.org/gqmelo/exec-wrappers
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/gqmelo/exec-wrappers?branch=master
    :target: https://ci.appveyor.com/project/gqmelo/exec-wrappers/branch/master
    :alt: See Build Status on AppVeyor

A command line tool to create wrappers around executable files

Rationale
---------

``exec-wrappers`` is useful whenever you need a single executable file, but have to do some setup
before executing it.

If you develop using some kind of environment isolation like ``conda``, ``schroot``,
``virtualenv`` you probably wanted to configure a GUI application like an IDE to use the executables
available inside these environments.

But you normally have to create a script that do some setup/activation step and then run the command
but creating such a script for each executable is tedious.

``exec-wrappers`` helps automating that as it detects executable files and create a wrapper for each
of them. It also already provides some wrappers for common tools.

Also, as the wrappers are intended to be used non-interactively, they are normally much simpler than
the interactive counterpart.

For example, the conda wrappers are much faster than doing an activate and executing the command:

- Regular activate:

.. code-block:: bash

    $ echo 'source activate test 2> /dev/null; "$@"' > /tmp/activate-and-run && chmod a+x /tmp/activate-and-run
    $ time /tmp/activate-and-run python --version
    Python 2.7.11 :: Continuum Analytics, Inc.
    
    real    0m0.354s
    user    0m0.288s
    sys 0m0.040s

- Using python wrapper created by ``exec-wrappers``:

.. code-block:: bash

    $ time /tmp/conda_wrappers/python --version
    Python 2.7.11 :: Continuum Analytics, Inc.
    
    real    0m0.003s
    user    0m0.000s
    sys 0m0.000s

Having a low overhead is very important if you are executing the command non-interactively.

Features
--------

- automatically detect executables in a given directory
- wrappers written in plain shell and batch scripts
- low overhead (as low as possible)
- built-in wrappers for common tools


Requirements
------------

``python`` is the only dependency to create wrappers.
To properly use the generated wrappers you need the tool used by the wrapper (conda, schroot, etc.).


Installation
------------

.. code-block::

    $ python setup.py install


How it works
------------

Creating `conda`_ wrappers:

.. code-block:: bash

    $ create-wrappers  -t conda --bin-dir ~/miniconda/envs/test/bin --dest-dir /tmp/conda_wrappers --conda-env-dir ~/miniconda/envs/test

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


Examples
--------

- conda:

.. code-block:: bash

    $ create-wrappers  -t conda -b ~/miniconda/envs/test/bin -d /tmp/conda_wrappers --conda-env-dir ~/miniconda/envs/test


- virtualenv:

.. code-block:: bash

    $ create-wrappers  -t virtualenv -b ~/python3-env/bin -d /tmp/virtualenv_wrappers --virtual-env-dir ~/python3-env


- schroot:

.. code-block:: bash

    $ create-wrappers  -t schroot -b ~/chroots/centos5/bin -d /tmp/schroot_wrappers --schroot-name centos5

.. code-block:: bash

    $ create-wrappers  -t schroot -b ~/chroots/centos5/bin -d /tmp/schroot_wrappers --schroot-name centos5 --schroot-options="-p -d /"


- custom:

.. code-block:: bash

    $ echo -e '#!/bin/sh\necho "$@"' > /tmp/custom-script && chmod a+x /tmp/custom-script
    $ create-wrappers  -t custom --custom-script=/tmp/custom-script -b /usr/bin -d /tmp/custom_wrappers


- wrap only specified files:

.. code-block:: bash

    $ create-wrappers  -t schroot -f gcc:gdb -d /tmp/schroot_wrappers --schroot-name centos5


- chain multiple wrappers:

.. code-block:: bash

    $ create-wrappers  -t conda -b ~/miniconda/envs/test/bin -d /tmp/conda_wrappers --conda-env-dir ~/miniconda/envs/test
    $ create-wrappers  -t schroot -b /tmp/conda_wrappers -d /tmp/schroot_wrappers --schroot-name centos5


License
-------

Distributed under the terms of the `MIT`_ license, ``exec-wrappers`` is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/gqmelo/exec-wrappers/issues
.. _`conda`: http://conda.pydata.org/miniconda.html

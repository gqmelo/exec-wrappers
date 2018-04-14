1.1.1
=========

**Bug fixes**

* Set wrappers as executable for group and others

1.1.0
=========

**Features**

* Option --use-exec to create wrappers using exec on Linux and MacOS

**Bug fixes**

* Convert conda and virtualenv paths to absolute
* Convert --bin-dir to absolute
* Quote commands executed by the wrappers so the path can contain spaces

1.0.3
=========

**Bug fixes**

* Set CONDA_PATH_BACKUP and CONDA_PS1_BACKUP variables used by conda 4.2

1.0.2
=========

**Bug fixes**

* Set CONDA_PREFIX variable. This variable is set by conda >= 4.1

1.0.1
=========

**Bug fixes**

* Fix run-in script when the option --inline is not passed. The placeholder __COMMAND__ was not being replaced

1.0.0
=========

**Features**

* Add option --inline for not creating a run-in script 

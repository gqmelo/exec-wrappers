#!/usr/bin/env bash -xe

if [ $(uname) == "Darwin" ]; then
  MINICONDA_INSTALLER=Miniconda3-latest-MacOSX-x86_64.sh;
else
  MINICONDA_INSTALLER=Miniconda3-latest-Linux-x86_64.sh;
fi
if ! "$HOME/miniconda/bin/conda" --version 2>/dev/null; then
  wget https://repo.continuum.io/miniconda/$MINICONDA_INSTALLER -O miniconda.sh;
  rmdir $HOME/miniconda;
  bash miniconda.sh -b -p $HOME/miniconda;
fi
mkdir -p "$HOME/bin"
ln -s $HOME/miniconda/bin/conda* $HOME/bin/
ln -s $HOME/miniconda/bin/activate $HOME/bin/
ln -s $HOME/miniconda/bin/deactivate $HOME/bin/
ls -l $HOME/bin
export PATH="$HOME/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
# Useful for debugging any issues with conda
conda info -a

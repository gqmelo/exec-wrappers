#!/bin/bash

if [ -z "$CONDA_ENV_PATH" ]; then
    ENV_DIR="`conda info --root`"
    echo ''
    echo 'CONDA_ENV_PATH is not set. Assuming conda root env'
else
    ENV_DIR="$CONDA_ENV_PATH"
fi

BIN_DIR="$ENV_DIR/bin"
WRAPPERS_DIR="$BIN_DIR/wrappers/conda"

echo "Creating wrappers from $BIN_DIR to $WRAPPERS_DIR"
create-wrappers \
    -t conda \
    -b "$BIN_DIR" \
    -d "$WRAPPERS_DIR" \
    --conda-env-dir "$ENV_DIR"

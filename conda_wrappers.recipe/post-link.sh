#!/bin/bash

echo 'Creating wrappers...'

if [ -z "$CONDA_ENV_PATH" ]; then
    echo 'CONDA_ENV_PATH is not set'
    exit 0
fi

CONDA_BIN_DIR="$CONDA_ENV_PATH/bin"
CONDA_WRAPPERS_DIR="$CONDA_ENV_PATH/bin/wrappers/conda"
mkdir -p $CONDA_WRAPPERS_DIR
for f in `ls "$CONDA_ENV_PATH/bin"`; do
    echo "Creating wrapper $CONDA_WRAPPERS_DIR/$f  ->  $CONDA_BIN_DIR/$f"
    echo "#!/bin/sh
$CONDA_BIN_DIR/exec-wrapper $f \"\$@\"
" > $CONDA_WRAPPERS_DIR/$f
    chmod a+x $CONDA_WRAPPERS_DIR/$f
done

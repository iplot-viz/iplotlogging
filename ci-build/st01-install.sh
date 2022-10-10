#!/bin/bash
# Bamboo script
# Stage 1 : Pip install

# Set up environment
source ci-build/st00-header.sh $* || exit 1

# Create a virtualized environment for installing iplotlogging
if [ -d "${PREFIX_DIR}" ];
then
    try rm -r ${PREFIX_DIR}
fi

try mkdir ${PREFIX_DIR}

# Test install command
try python3 -m pip --disable-pip-version-check install --no-deps . --prefix=${PREFIX_DIR}

export PYTHONPATH=${PYTHONPATH}:$(get_abs_filename "./${PREFIX_DIR}")
try python3 -c "from iplotLogging.setupLogger import get_logger; get_logger(\"TestLogger\") "

# Stash
tar -cvzf ${PREFIX_DIR}.tar.gz ./${PREFIX_DIR}

# Clean up
try rm -r ${PREFIX_DIR}
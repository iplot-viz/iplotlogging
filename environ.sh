#!/bin/bash

# 3-fingered-claw 
function yell () 
{ 
  echo "$0: $*" >&2
}

function die () 
{ 
  yell "$*"; exit 1
}

function try () 
{ 
  "$@" || die "cannot $*" 
}

# Default to foss toolchain
if [[ "$1" == "foss" || -z $1 ]];
then
    toolchain=foss
elif [[ "$1" == "intel" ]];
then
    toolchain=intel
fi
echo "Toolchain: $toolchain"

# Default to production config. (Will use idv components from system instead of sources.)
if [[ "$2" == "prod" || -z $2 ]];
then
    config=prod
elif [[ "$2" == "dev" ]];
then
    config=dev
fi
echo "Configuration: $config"

# Testing/Coverage requirements
try module load coverage Python-bundle-PyPI

try module -t list 2>&1 | sort

export HOME=$PWD
echo "HOME was set to $HOME"

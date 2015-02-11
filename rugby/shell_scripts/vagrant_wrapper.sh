#!/bin/bash

# This script is a wrapper around the `vagrant` command
# which sets VAGRANT_CWD before executing `vagrant`.
# This allows us to run a `Vagrantfile` from an arbitrary
# directory.
#
# USAGE: vagrant_wrapper.sh <VAGRANTFILE_DIR> (up|destroy|...)
# EXAMPLE: vagrant_wrapper.sh /home/user/ up
#
# Script produces no other output other than what `vagrant` outputs

# Exit on command failure
set -e

# Need at least 2 arguments
if [ $# -lt 2 ]; then
    exit 1
fi

# Directory path
DIR="$1"
# Remaining arguments to be fed to `vagrant`
shift
ARGS="$@"

# Sanity checks
[ ! -d "$DIR" ] && exit 1
[ ! -f "${DIR}/Vagrantfile" ] && exit 1

# Run `vagrant`
export VAGRANT_CWD="$DIR"
vagrant "$@"

exit 0


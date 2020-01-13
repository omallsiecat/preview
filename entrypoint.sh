#!/bin/sh

set -e

# add secrets to current env
. decrypt

exec "$@"


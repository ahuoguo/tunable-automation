#! /bin/bash

VERUS_DIR="$1"

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

pushd "$VERUS_DIR/source"
./tools/get-z3.sh > /dev/null 2>&1
source ../tools/activate > /dev/null 2>&1
vargo build --release --vstd-no-verify > /dev/null 2>&1
popd
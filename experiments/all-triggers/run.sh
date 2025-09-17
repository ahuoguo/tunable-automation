#! /bin/bash

VERUS=verus # TODO: make this more configurable
NTHREADS=9 # TODO: add this flag on all the commands

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

# Install verus
../build-verus.sh ../../verus/minimizer
pushd ../../verus/minimizer/source
VERUS="$(pwd)/target-verus/release/verus"
popd

# get runtime for minimized all triggers
pushd ./verified-ironkv-min/ironsht/src
$VERUS --crate-type=lib lib.rs --rlimit 50 --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./verified-ironkv-min/ironsht/src/output.json ./ironkv_at_min.json

sample failure for ironkv
../build-verus.sh ../../verus/sample-failure
pushd ../../verus/minimizer/source
VERUS="$(pwd)/target-verus/release/verus"
popd

../build-verus.sh ../../verus/sample-failure/
pushd ../../verus/sample-failure/source/tools/minimize
rm -rf ./tmp
cargo run --release -- -s -d ./tmp ../../../../../experiments/all-triggers/verified-ironkv-min/ironsht/src/lib.d > ironkv_at.log
popd
mv ../../verus/sample-failure/source/tools/minimize/*.json ../../failure-sample/ironkv_at/
mv ../../verus/sample-failure/source/tools/minimize/ironkv_at.log ../../failure-sample/ironkv_at/
 
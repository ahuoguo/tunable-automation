#! /bin/bash

# This script runs all verus experiments (original/minimized/braodcast-from/main)
# and generates the `.d` file

# TODO: this script depends on `cargo` installed by TODO 
# (it should recognize rust-toolchain.toml and switch to rust 1.88.0)

NTHREADS=9 # TODO: add this flag on all the commands

pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

# Install verus
./build-verus.sh ../verus/verus
pushd ../verus/verus/source
VERUS="$(pwd)/target-verus/release/verus"
popd

# this one also captures the number of warnings...
# $VERUS --crate-type=lib ./original/verified-ironkv/ironsht/src/lib.rs --emit=dep-info --time --time-expanded --output-json > output.json 2>&1 | tail -n 3

# IRONKV
pushd ./original/verified-ironkv/ironsht/src
$VERUS --crate-type=lib lib.rs --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./original/verified-ironkv/ironsht/src/output.json ./original/ironkv.json

pushd ./minimized/verified-ironkv/ironsht/src
$VERUS --crate-type=lib lib.rs --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./minimized/verified-ironkv/ironsht/src/output.json ./minimized/ironkv.json

pushd ./broadcast-from-main/verified-ironkv/ironsht/src
$VERUS --crate-type=lib lib.rs --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./broadcast-from-main/verified-ironkv/ironsht/src/output.json ./broadcast-from-main/ironkv.json

# SPLINTER
pushd ./original/verified-betrfs/Splinter/src
$VERUS --crate-type=lib lib.rs --rlimit 90 --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./original/verified-betrfs/Splinter/src/output.json ./original/splinter.json

pushd ./minimized/verified-betrfs/Splinter/src
$VERUS --crate-type=lib lib.rs --rlimit 90 --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./minimized/verified-betrfs/Splinter/src/output.json ./minimized/splinter.json

pushd ./broadcast-from-main/verified-betrfs/Splinter/src
$VERUS --crate-type=lib lib.rs --rlimit 90 --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./broadcast-from-main/verified-betrfs/Splinter/src/output.json ./broadcast-from-main/splinter.json

# ANVIL
pushd ./original/anvil/src/deps_hack
cargo build > /dev/null 2>&1
popd
pushd ./original/anvil/src
$VERUS -L dependency=deps_hack/target/debug/deps --extern=deps_hack=deps_hack/target/debug/libdeps_hack.rlib anvil.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./original/anvil/src/output.json ./original/anvil.json

pushd ./minimized/anvil/src/deps_hack
cargo build > /dev/null 2>&1
popd
pushd ./minimized/anvil/src
$VERUS -L dependency=deps_hack/target/debug/deps --extern=deps_hack=deps_hack/target/debug/libdeps_hack.rlib anvil.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./minimized/anvil/src/output.json ./minimized/anvil.json

pushd ./broadcast-from-main/anvil/src/deps_hack
cargo build > /dev/null 2>&1
popd
pushd ./broadcast-from-main/anvil/src
$VERUS -L dependency=deps_hack/target/debug/deps --extern=deps_hack=deps_hack/target/debug/libdeps_hack.rlib anvil.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./broadcast-from-main/anvil/src/output.json ./broadcast-from-main/anvil.json

# CAPYBARA
# TODO: I might permanently move the deps_hack directory in `src` to have consistency with minimization code
pushd ./original/verified-storage/osdi25/capybaraKV/deps_hack/
cargo build > /dev/null 2>&1
popd
pushd ./original/verified-storage/osdi25/capybaraKV/capybarakv/src
$VERUS -L dependency=../../deps_hack/target/debug/deps --extern=deps_hack=../../deps_hack/target/debug/libdeps_hack.rlib lib.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./original/verified-storage/osdi25/capybaraKV/capybarakv/src/output.json ./original/capybara.json

pushd ./minimized/verified-storage/osdi25/capybaraKV/deps_hack/
cargo build > /dev/null 2>&1
popd
pushd ./minimized/verified-storage/osdi25/capybaraKV/capybarakv/src
$VERUS -L dependency=../../deps_hack/target/debug/deps --extern=deps_hack=../../deps_hack/target/debug/libdeps_hack.rlib lib.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./minimized/verified-storage/osdi25/capybaraKV/capybarakv/src/output.json ./minimized/capybara.json

pushd ./broadcast-from-main/verified-storage/osdi25/capybaraKV/deps_hack/
cargo build > /dev/null 2>&1
popd
pushd ./broadcast-from-main/verified-storage/osdi25/capybaraKV/capybarakv/src
$VERUS -L dependency=../../deps_hack/target/debug/deps --extern=deps_hack=../../deps_hack/target/debug/libdeps_hack.rlib lib.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --emit=dep-info --time --time-expanded --output-json > output.json 2> /dev/null
popd
mv ./broadcast-from-main/verified-storage/osdi25/capybaraKV/capybarakv/src/output.json ./broadcast-from-main/capybara.json

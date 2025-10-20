#! /bin/bash

NTHREADS=9
PYTHON=python3 # Note: it's python3.10 on my laptop

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

# remove all the logs previously generated
rm -rf ./original/logs/ironkv/
rm -rf ./minimized/logs/ironkv/
rm -rf ./broadcast-from-main/logs/ironkv/
rm -rf ./all-triggers/logs/ironkv/
rm -rf ./all-triggers/logs/ironkv_min/

rm -rf ../mariposa/data/dbs/ironkv_original
rm -rf ../mariposa/data/dbs/ironkv_minimized
rm -rf ../mariposa/data/dbs/ironkv_broadcast
rm -rf ../mariposa/data/dbs/ironkv_all_triggers
rm -rf ../mariposa/data/dbs/ironkv_all_triggers_minimized

rm -rf ../mariposa/data/dbs/splinter_original
rm -rf ../mariposa/data/dbs/splinter_minimized
rm -rf ../mariposa/data/dbs/splinter_broadcast

rm -rf ../mariposa/data/dbs/anvil_original
rm -rf ../mariposa/data/dbs/anvil_minimized
rm -rf ../mariposa/data/dbs/anvil_broadcast

rm -rf ../mariposa/data/dbs/capybara_original
rm -rf ../mariposa/data/dbs/capybara_minimized
rm -rf ../mariposa/data/dbs/capybara_broadcast

# mkdir
mkdir -p ./original/logs/ironkv/
mkdir -p ./minimized/logs/ironkv/
mkdir -p ./broadcast-from-main/logs/ironkv/
mkdir -p ./all-triggers/logs/ironkv/
mkdir -p ./all-triggers/logs/ironkv_min/

mkdir -p ./original/logs/splinter/
mkdir -p ./minimized/logs/splinter/
mkdir -p ./broadcast-from-main/logs/splinter/

mkdir -p ./original/logs/anvil/
mkdir -p ./minimized/logs/anvil/
mkdir -p ./broadcast-from-main/logs/anvil/

mkdir -p ./original/logs/capybara/
mkdir -p ./minimized/logs/capybara/
mkdir -p ./broadcast-from-main/logs/capybara/

# IRONKV
pushd ./original/verified-ironkv/ironsht/src
$VERUS --crate-type=lib lib.rs --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./original/verified-ironkv/ironsht/src/.verus-log/ ./original/logs/ironkv/

pushd ./minimized/verified-ironkv/ironsht/src
$VERUS --crate-type=lib lib.rs --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./minimized/verified-ironkv/ironsht/src/.verus-log/ ./minimized/logs/ironkv/

pushd ./broadcast-from-main/verified-ironkv/ironsht/src
$VERUS --crate-type=lib lib.rs --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./broadcast-from-main/verified-ironkv/ironsht/src/.verus-log/ ./broadcast-from-main/logs/ironkv/

# Note IRONKV with all_triggers still fails one task with default rlimit
pushd ./all-triggers/verified-ironkv/ironsht/src
$VERUS --crate-type=lib lib.rs --num-threads=$NTHREADS --rlimit 50 --log smt 2> /dev/null
popd
mv ./all-triggers/verified-ironkv/ironsht/src/.verus-log/ ./all-triggers/logs/ironkv/

pushd ./all-triggers/verified-ironkv-min/ironsht/src
$VERUS --crate-type=lib lib.rs --num-threads=$NTHREADS --rlimit 50 --log smt 2> /dev/null
popd
mv ./all-triggers/verified-ironkv-min/ironsht/src/.verus-log/ ./all-triggers/logs/ironkv_min/

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/original/logs/ironkv/ --new-project-name ironkv_original
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/ironkv_original/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/minimized/logs/ironkv/ --new-project-name ironkv_minimized
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/ironkv_minimized/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/broadcast-from-main/logs/ironkv/ --new-project-name ironkv_broadcast
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/ironkv_broadcast/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/all-triggers/logs/ironkv/ --new-project-name ironkv_all_triggers
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/ironkv_all_triggers/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/all-triggers/logs/ironkv_min/ --new-project-name ironkv_all_triggers_minimized
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/ironkv_all_triggers_minimized/base.z3/ -e debug
popd

# Splinter
pushd ./original/verified-betrfs/Splinter/src
$VERUS --crate-type=lib lib.rs --rlimit 90 --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./original/verified-betrfs/Splinter/src/.verus-log/ ./original/logs/splinter/

pushd ./minimized/verified-betrfs/Splinter/src
$VERUS --crate-type=lib lib.rs --rlimit 90 --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./minimized/verified-betrfs/Splinter/src/.verus-log/ ./minimized/logs/splinter/

pushd ./broadcast-from-main/verified-betrfs/Splinter/src
$VERUS --crate-type=lib lib.rs --rlimit 90 --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./broadcast-from-main/verified-betrfs/Splinter/src/.verus-log/ ./broadcast-from-main/logs/splinter/

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/original/logs/splinter/ --new-project-name splinter_original
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/splinter_original/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/minimized/logs/splinter/ --new-project-name splinter_minimized
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/splinter_minimized/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/broadcast-from-main/logs/splinter/ --new-project-name splinter_broadcast
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/splinter_broadcast/base.z3/ -e debug
popd

# Anvil

pushd ./original/anvil/src/deps_hack
cargo build > /dev/null 2>&1
popd
pushd ./original/anvil/src
$VERUS -L dependency=deps_hack/target/debug/deps --extern=deps_hack=deps_hack/target/debug/libdeps_hack.rlib anvil.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./original/anvil/src/.verus-log/ ./original/logs/anvil/

pushd ./minimized/anvil/src/deps_hack
cargo build > /dev/null 2>&1
popd
pushd ./minimized/anvil/src
$VERUS -L dependency=deps_hack/target/debug/deps --extern=deps_hack=deps_hack/target/debug/libdeps_hack.rlib anvil.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./minimized/anvil/src/.verus-log/ ./minimized/logs/anvil/

pushd ./broadcast-from-main/anvil/src/deps_hack
cargo build > /dev/null 2>&1
popd
pushd ./broadcast-from-main/anvil/src
$VERUS -L dependency=deps_hack/target/debug/deps --extern=deps_hack=deps_hack/target/debug/libdeps_hack.rlib anvil.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./broadcast-from-main/anvil/src/.verus-log/ ./broadcast-from-main/logs/anvil/

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/original/logs/anvil/ --new-project-name anvil_original
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/anvil_original/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/minimized/logs/anvil/ --new-project-name anvil_minimized
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/anvil_minimized/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/broadcast-from-main/logs/anvil/ --new-project-name anvil_broadcast
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/anvil_broadcast/base.z3/ -e debug
popd

# Capybara

pushd ./original/verified-storage/osdi25/capybaraKV/deps_hack/
cargo build > /dev/null 2>&1
popd
pushd ./original/verified-storage/osdi25/capybaraKV/capybarakv/src
$VERUS -L dependency=../../deps_hack/target/debug/deps --extern=deps_hack=../../deps_hack/target/debug/libdeps_hack.rlib lib.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./original/verified-storage/osdi25/capybaraKV/capybarakv/src/.verus-log/ ./original/logs/capybara/

pushd ./minimized/verified-storage/osdi25/capybaraKV/deps_hack/
cargo build > /dev/null 2>&1
popd
pushd ./minimized/verified-storage/osdi25/capybaraKV/capybarakv/src
$VERUS -L dependency=../../deps_hack/target/debug/deps --extern=deps_hack=../../deps_hack/target/debug/libdeps_hack.rlib lib.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./minimized/verified-storage/osdi25/capybaraKV/capybarakv/src/.verus-log/ ./minimized/logs/capybara/

pushd ./broadcast-from-main/verified-storage/osdi25/capybaraKV/deps_hack/
cargo build > /dev/null 2>&1
popd
pushd ./broadcast-from-main/verified-storage/osdi25/capybaraKV/capybarakv/src
$VERUS -L dependency=../../deps_hack/target/debug/deps --extern=deps_hack=../../deps_hack/target/debug/libdeps_hack.rlib lib.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --log smt 2> /dev/null
popd
mv ./broadcast-from-main/verified-storage/osdi25/capybaraKV/capybarakv/src/.verus-log/ ./broadcast-from-main/logs/capybara/

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/original/logs/capybara/ --new-project-name capybara_original
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/capybara_original/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/minimized/logs/capybara/ --new-project-name capybara_minimized
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/capybara_minimized/base.z3/ -e debug
popd

pushd ../mariposa
source ./myenv/bin/activate
pip install networkx
$PYTHON ./src/proj_wizard.py create -i ../experiments/broadcast-from-main/logs/capybara/ --new-project-name capybara_broadcast
$PYTHON ./src/exper_wizard.py multiple -s z3_4_12_5 -i data/projs/capybara_broadcast/base.z3/ -e debug
popd

# pushd ./original/verified-storage/osdi25/capybaraKV/deps_hack/
# cargo build > /dev/null 2>&1
# popd
# pushd ./original/verified-storage/osdi25/capybaraKV/capybarakv/src
# $VERUS -L dependency=../../deps_hack/target/debug/deps --extern=deps_hack=../../deps_hack/target/debug/libdeps_hack.rlib lib.rs --rlimit 50 --crate-type=lib --num-threads=$NTHREADS --log smt
# popd
# mv ./original/verified-storage/osdi25/capybaraKV/capybarakv/src/.verus-log/ ./original/logs/capybaraKV/


# History of commands for mariposa, most req are downloaded using python 3.10
# git clone --filter=blob:none https://github.com/secure-foundations/mariposa.git
# cd src/smt2action/
# cargo build --release
# cd -
# python3.10 ./src/proj_wizard.py create -i ../experiments/original/logs/ironkv/ --new-project-name ironkv_original
# python3.10 ./src/exper_wizard.py multiple -s z3_4_12_2_arm_osx -i data/projs/ironkv_original/base.z3/ -e debug

# on pinky:
# all previous steps are the same, but need to use venv
# python3 -m venv myenv
# source myenv/bin/activate
# pip3 install -r requirements.txt
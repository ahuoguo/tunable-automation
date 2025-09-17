#!/bin/bash

# figure of all benchmarks, brd-from-main.json versus original.json
python plot_all.py \
    ../experiments/broadcast-from-main/ironkv.json ../experiments/original/ironkv.json \
    ../experiments/broadcast-from-main/splinter.json ../experiments/original/splinter.json \
    ../experiments/broadcast-from-main/anvil.json ../experiments/original/anvil.json \
    ../experiments/broadcast-from-main/capybara.json ../experiments/original/capybara.json
    

# TODO: finish script

python plot.py ../experiments/all-triggers/ironkv_at_min.json ../experiments/original/ironkv.json

#! /bin/bash

# python plot.py ./ironkv ironkv
# python plot.py ./splinter splinter
# python plot.py ./anvil anvil
# python plot.py ./capybara capybara

# python plot.py ./ironkv_at ironkv_at

python ./plot-all-scatter.py . broadcast broadcast 
python ./plot-all-scatter.py . all_triggers all_triggers

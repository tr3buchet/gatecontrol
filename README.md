## install
```
git clone https://github.com/tr3buchet/gatecontrol.git
# make/activate a venv if you wish
cd gatecontrol
# and because I am the suck at python packaging install doesnt work, so..
python setup.py develop
mkdir -p ~/.gatecontrol && mv gatecontrol.conf ~/.gatecontrol
# edit ~/.gatecontrol/gatecontrol for your setup
```

## run
run `gatecontrol` or `gatecontrol &` from the commandline

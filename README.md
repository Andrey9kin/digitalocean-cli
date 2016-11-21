# Usage

```
Digital Ocean command line client

Usage:
  digitalocean-cli.py [ options ] create [--image=IMAGE] [--region=REGION]
  [--ssh=SSH] [--size=SIZE] [--num=NUM]
  digitalocean-cli.py [ options ] list
  digitalocean-cli.py [ options ] power_off ( <name>... | <id>... )
  digitalocean-cli.py [ options ] power_on  ( <name>... | <id>... )
  digitalocean-cli.py [ options ] reboot    ( <name>... | <id>... )
  digitalocean-cli.py [ options ] destroy   ( <name>... | <id>... )
  digitalocean-cli.py --help

Options:
  --debug        Print debug info
  --help         Print this message
  --token=TOKEN  Env var to read Digital Ocean API token from [default: TOKEN]

Arguments:
  create     Create droplet
  list       List droplets
  power_off  Power off droplet or droplets
  power_on   Power on droplet or droplets
  reboot     Reboot droplet or droplets
  destroy    Destroy droplet or droplets
  name       Droplet name. Could be mixed with ids in the same command
  id         Droplet id. Could be mixed with names in the same command

Create command options:
  --image=IMAGE    Image version [default: ubuntu-16-04-x64]
  --region=REGION  Region [default: ams3]
  --ssh=SSH        SSH key to add [default: ~/.ssh/id_rsa.pub]
  --size=SIZE      Droplet size [default: 512mb]
  --num=NUM        Number of droplets to create [default: 1]
```

# Build executable

```
# This will prepare virtual env and pull in all necessary libs
bash prepare_env.sh 

# Activate virtual env; On Windows, it must be something like - env/Scripts/activate.exe
source env/bin/activate

# Now you are ready to go
pyinstaller --onefile digitalocean-cli.py

# Executable should be in the build dir
dist/digitalocean-cli -h
```

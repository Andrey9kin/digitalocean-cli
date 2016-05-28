# Usage

```
Digital Ocean command line client

Usage:
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] create [ --image=ubuntu-16-04-x64 ] [ --region=ams3 ] [ --ssh=~/.ssh/id_rsa.pub ] [ --size=512mb ] [ --num=1 ]
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] list
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] power_off ( <name>... | <id>... )
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] power_on  ( <name>... | <id>... )
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] reboot    ( <name>... | <id>... )
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] destroy   ( <name>... | <id>... )

Make sure to set env variable TOKEN (or define your own name using --token) with you know what as a value
```

# Build executable

```
pyinstaller --onefile digitalocean-cli.py
```

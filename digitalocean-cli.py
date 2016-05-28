#!/usr/bin/env python

"""
Digital Ocean command line client

Usage:
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] create [ --image=ubuntu-16-04-x64 ] [ --region=ams3 ] [ --ssh=~/.ssh/id_rsa.pub ] [ --size=512mb ] [ --num=1 ]
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] list
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] power_off ( <name>... | <id>... )
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] power_on  ( <name>... | <id>... )
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] reboot    ( <name>... | <id>... )
  digitalocean-cli.py [ --debug ] [ --token=TOKEN ] destroy   ( <name>... | <id>... )

Make sure to set env variable TOKEN (or define your own name using --token) with you know what as a value

"""
from docopt import docopt
import logging
import petname
import digitalocean
import sshpubkeys
import os

TOKEN_VAR = "TOKEN"

def read_file(path):
  abs_path = os.path.expandvars(os.path.expanduser(path))
  if os.path.isfile(abs_path):
    with open(abs_path) as f:
      return f.read().replace('\n', '')
  else:
    raise IOError("File {} doesn't exists".format(abs_path))

def names_to_ids(token, names):
  manager = digitalocean.Manager(token=token)
  result = []
  for name in names:
    if name.isdigit():
      result.append(name)
      continue
    for droplet in manager.get_all_droplets():
      if droplet.name == name:
        result.append(droplet.id)
        break
    else:
      raise IOError("Droplet {} doesn't exists".format(name))
  return result

def get_droplet(token, id):
  manager = digitalocean.Manager(token=token)
  return manager.get_droplet(id)

def get_token(args):
  token = args["--token"] if "--token" in args and args["--token"] else TOKEN_VAR
  if token in os.environ:
    return os.environ[token]
  raise EnvironmentError("Can't read env variable {}".format(token))

def get_options(args):
  result = {}
  for key, value in args.items():
    if (key.startswith("--") or key.startswith("<")) and value is not None and value != []:
      result[key.lstrip("--").lstrip("<").rstrip(">")] = value
  # Clean up utility options
  for key in "tf", "te", "debug":
    if key in result.keys():
      del result[key]
  logging.debug("Extracted options: {}".format(result))
  return result

def get_command(args):
  for key, value in args.items():
    if not key.startswith("--") and not key.startswith("<") and value is True:
      logging.debug("Extracted command: {}".format(key))
      return key

def create(token, ssh="~/.ssh/id_rsa.pub", num=1, image="ubuntu-16-04-x64", region="ams3", size="512mb"):
  logging.info("Create {} {} image(s) of size {} in region {} with ssh key {}".format(num, image, size, region, ssh))
  key = sshpubkeys.SSHKey(read_file(ssh))
  logging.debug("Provided ssh key: {}".format(key.hash_md5()))
  for _ in range(int(num)):
    name = "{}-{}-{}-{}".format(image, size, region, petname.Generate(2, "-"))
    droplet = digitalocean.Droplet(token=token,
                                 number=num,
                                 name=name,
                                 region=region,
                                 image=image,
                                 ssh_keys=[key.hash_md5()],
                                 size_slug=size)
    droplet.create()
    logging.info("{} created".format(name))

def list(token):
  manager = digitalocean.Manager(token=token)
  logging.info("{:<20} {:<60} {:<20} {:<20}".format("id", "name", "ip", "status"))
  for droplet in manager.get_all_droplets():
    logging.info("{:<20} {:<60} {:<20} {:<20}".format(droplet.id,
                                      droplet.name,
                                      droplet.ip_address,
                                      droplet.status))

def generic_droplet_command(command_name, token, name):
  ids = names_to_ids(token, name)
  for droplet_id in ids:
    droplet = get_droplet(token, droplet_id)
    logging.info("{} droplet {} ({})".format(command_name.replace("_", " "),
                                                 droplet.name, droplet.id))
    command = getattr(droplet, command_name)
    command()
    logging.info("Ok")

def power_off(token, name):
  generic_droplet_command("power_off", token, name)

def power_on(token, name):
  generic_droplet_command("power_on", token, name)

def reboot(token, name):
  generic_droplet_command("reboot", token, name)

def destroy(token, name):
  generic_droplet_command("destroy", token, name)

def main():
  arguments = docopt(__doc__)

  if arguments['--debug']:
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(format='%(message)s', level=logging.INFO)

  logging.debug("Arguments: {}".format(arguments))

  token = get_token(arguments)
  command_name = get_command(arguments)
  options = get_options(arguments)
  options['token'] = token

  command = globals().get(command_name, None)
  if not command:
    raise NotImplementedError("Command {} not implemented".format(command_name))

  command(**options)

if __name__ == "__main__":
    main()

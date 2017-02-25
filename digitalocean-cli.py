#!/usr/bin/env python

"""
Digital Ocean command line client

Usage:
  digitalocean-cli.py [ options ] droplet create [--image=IMAGE] [--region=REGION]
  [--ssh=SSH] [--size=SIZE] [--num=NUM]
  digitalocean-cli.py [ options ] droplet list
  digitalocean-cli.py [ options ] droplet power_off ( <name>... | <id>... )
  digitalocean-cli.py [ options ] droplet power_on  ( <name>... | <id>... )
  digitalocean-cli.py [ options ] droplet reboot    ( <name>... | <id>... )
  digitalocean-cli.py [ options ] droplet destroy   ( <name>... | <id>... )
  digitalocean-cli.py [ options ] image   list
  digitalocean-cli.py --help

Options:
  --debug        Print debug info
  --help         Print this message
  --token=TOKEN  Env var to read Digital Ocean API token from [default: TOKEN]

Image arguments:
  list       List images

Droplet arguments:
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
"""
from docopt import docopt
import logging
import petname
import digitalocean
import sshpubkeys
import os


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
    if args["--token"] in os.environ:
        return os.environ[args["--token"]]
    raise EnvironmentError("Can't read env variable {}"
                           "".format(args["--token"]))


def get_options(args):
    result = {}
    for key, value in args.items():
        if ((key.startswith("--") or key.startswith("<")) and
           value is not None and value != []):
            result[key.lstrip("--").lstrip("<").rstrip(">")] = value
    # Clean up utility options
    for key in "tf", "te", "debug":
        if key in result.keys():
            del result[key]
    logging.debug("Extracted options: {}".format(result))
    return result


def get_command(args):
    prefix=""
    if args.get("droplet"):
      prefix = "droplet"
    elif args.get("image"):
      prefix = "image"
    else:
      logging.error("Coundn't indentify command type. " +
                "Supported - droplet, image. Args: {}".format(args))
    for key, value in args.items():
        if (not key == prefix and value is True):
            command = "{}_{}".format(prefix, key)
            logging.debug("Extracted command: {}".format(command))
            return command


def droplet_create(**kwargs):
    logging.info("Create {} {} droplet(s) of size {} in region {} "
                 "with ssh key {}".format(kwargs['num'],
                                          kwargs['image'],
                                          kwargs['size'],
                                          kwargs['region'],
                                          kwargs['ssh']))
    key = sshpubkeys.SSHKey(read_file(kwargs['ssh']))
    logging.debug("Provided ssh key: {}".format(key.hash_md5()))
    for _ in range(int(kwargs['num'])):
        name = "{}-{}-{}-{}".format(kwargs['image'],
                                    kwargs['size'],
                                    kwargs['region'],
                                    petname.Generate(2, "-"))
        droplet = digitalocean.Droplet(token=kwargs['token'],
                                       number=kwargs['num'],
                                       name=name,
                                       region=kwargs['region'],
                                       image=kwargs['image'],
                                       ssh_keys=[key.hash_md5()],
                                       size_slug=kwargs['size'])
        droplet.create()
        logging.info("{} created".format(name))


def droplet_list(**kwargs):
    manager = digitalocean.Manager(token=kwargs['token'])
    logging.info("{:<20} {:<60} {:<20} {:<20}".format("id",
                                                      "name",
                                                      "ip",
                                                      "status"))
    for droplet in manager.get_all_droplets():
        logging.info("{:<20} {:<60} {:<20} {:<20}".format(droplet.id,
                                                          droplet.name,
                                                          droplet.ip_address,
                                                          droplet.status))

def image_list(**kwargs):
    manager = digitalocean.Manager(token=kwargs['token'])
    logging.info("{:<20} {:<60} {:<20} {:<20} {:<20}".format("id",
                                                      "name",
                                                      "size",
                                                      "regions",
                                                      "created_at"))
    for image in manager.get_my_images():
        logging.info("{:<20} {:<60} {:<20} {:<20} {:<20}".format(image.id,
                                                          image.name,
                                                          image.size_gigabytes,
                                                          image.regions,
                                                          image.created_at))

def generic_droplet_command(command_name, token, name):
    ids = names_to_ids(token, name)
    for droplet_id in ids:
        droplet = get_droplet(token, droplet_id)
        logging.info("{} droplet {} ({})"
                     "".format(command_name.replace("_", " "),
                               droplet.name,
                               droplet.id))
        command = getattr(droplet, command_name)
        command()
        logging.info("Ok")


def droplet_power_off(**kwargs):
    generic_droplet_command("power_off", kwargs['token'], kwargs['name'])


def droplet_power_on(**kwargs):
    generic_droplet_command("power_on", kwargs['token'], kwargs['name'])


def droplet_reboot(**kwargs):
    generic_droplet_command("reboot", kwargs['token'], kwargs['name'])


def droplet_destroy(**kwargs):
    generic_droplet_command("destroy", kwargs['token'], kwargs['name'])


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
        message = "Command {} not implemented".format(command_name)
        raise NotImplementedError(message)

    command(**options)


if __name__ == "__main__":
    main()

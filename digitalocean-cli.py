#!/usr/bin/env python

"""
Digital Ocean command line client

Usage:
  digitalocean-cli.py [ options ] droplet create [--image=IMAGE] [--region=REGION]
  [--ssh=SSH] [--size=SIZE] [--num=NUM] [--name=NAME]
  digitalocean-cli.py [ options ] droplet list
  digitalocean-cli.py [ options ] droplet power_off ( <name>... | <id>... )
  digitalocean-cli.py [ options ] droplet power_on  ( <name>... | <id>... )
  digitalocean-cli.py [ options ] droplet reboot    ( <name>... | <id>... )
  digitalocean-cli.py [ options ] droplet destroy   ( <name>... | <id>... )
  digitalocean-cli.py [ options ] image   list
  digitalocean-cli.py [ options ] image   destroy   ( <name>... | <id>... )
  digitalocean-cli.py --help

Options:
  --debug        Print debug info
  --help         Print this message
  --token=TOKEN  Env var to read Digital Ocean API token from [default: TOKEN]

Image arguments:
  list       List images
  destroy    Destroy image

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
  --name=NAME      Prefix to add to generated name [default: ]
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


def names_to_ids(token, names, type):
    logging.debug("Convert {} to id's for object type {}".format(names, type))
    manager = digitalocean.Manager(token=token)
    result = []
    objects = []
    if type == "droplet":
      objects = manager.get_all_droplets()
    elif type == "image":
      objects = manager.get_my_images()
    else:
      logging.error("Internal error. Unsupported object type: {}".format(type))
    for name in names:
        if name.isdigit():
            result.append(name)
            continue
        for object in objects:
            if object.name == name:
                result.append(droplet.id)
                break
        else:
            raise IOError("{} {} doesn't exists".format(type, name))
    return result


def get_object(token, id, type):
    manager = digitalocean.Manager(token=token)
    if type == "droplet":
        return manager.get_droplet(id)
    elif type == "image":
        return manager.get_image(id)
    else:
        logging.error("Internal error. Unsupported object type: {}".format(type))


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
        if (not key == prefix and value is True and not key.startswith("--")):
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
        if kwargs['name'] != "":
            name = "{}-{}".format(kwargs['name'], name)
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
    logging.info("{:<60} {:<20} {:<20} {:<20}".format("name",
                                                      "status",
                                                      "ip",
                                                      "id"))
    for droplet in manager.get_all_droplets():
        logging.info("{:<60} {:<20} {:<20} {:<20}".format(droplet.name,
                                                          droplet.status,
                                                          droplet.ip_address,
                                                          droplet.id))

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

def generic_command(command_name, token, name, type):
    ids = names_to_ids(token, name, type)
    for id in ids:
        object = get_object(token, id, type)
        logging.info("{} {} {} ({})"
                     "".format(command_name.replace("_", " "),
                               type,
                               object.name,
                               object.id))
        command = getattr(object, command_name)
        command()
        logging.info("Ok")


def droplet_power_off(**kwargs):
    generic_command("power_off", kwargs['token'], kwargs['name'], "droplet")


def droplet_power_on(**kwargs):
    generic_command("power_on", kwargs['token'], kwargs['name'], "droplet")


def droplet_reboot(**kwargs):
    generic_command("reboot", kwargs['token'], kwargs['name'], "droplet")


def droplet_destroy(**kwargs):
    generic_command("destroy", kwargs['token'], kwargs['name'], "droplet")

def image_destroy(**kwargs):
    generic_command("destroy", kwargs['token'], kwargs['name'], "image")

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

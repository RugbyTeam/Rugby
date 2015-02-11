import yaml
from jinja2 import Environment, FileSystemLoader


RUGBY_YML = '.rugby.yml'

VAGRANTFILE = 'Vagrantfile'

TEMPLATE_NAME = VAGRANTFILE + '.template'
TEMPLATE_PATH = 'template_path'

"""Parses a yaml config file and outputs a new
Vagrantfile generated from a template.

Args:
    playbook_basepath (str): path where ansible playbooks are located
    config_basepath (str): full path of the yaml config file

Kwargs:
    template_path (str): full path of the template file to generate a Vagrantfile from.
        defaults to playbook_basepath + '/templates + TEMPLATE_NAME

"""
def parse(playbook_basepath, config_basepath, **kwargs):

    if TEMPLATE_PATH in kwargs:
        template_path = kwargs[TEMPLATE_PATH]
        template_path_parts = template_path.split('/')

        template_basepath = '/'.join(template_path_parts[:-1])
        template_name = template_path_parts[-1]
    else:
        # default template path
        template_basepath = playbook_basepath + '/templates'
        template_name = TEMPLATE_NAME

    env = Environment(loader=FileSystemLoader(template_basepath))
    template = env.get_template(template_name)

    config_path = playbook_basepath +'/' + RUGBY_YML
    generated_vagrantfile_path = playbook_basepath + '/' + VAGRANTFILE

    with open(config_path, 'r') as config_file:
        vms = yaml.safe_load(config_file)
        with open(generated_vagrantfile_path, 'w') as generated_vagrantfile:
            template_output = template.render(vms = vms)
            generated_vagrantfile.write(template_output)


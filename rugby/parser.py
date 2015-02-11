import yaml
from jinja2 import Environment, FileSystemLoader

RUGBY_YML = '.rugby.yml'

VAGRANTFILE = 'Vagrantfile'

"""Parses a yaml config file and outputs a new
Vagrantfile generated from a template.

Args:
    template_path (str): full path of the templated Vagrantfile
        to generate a Vagrantfile

    site_yml_path (str): full path where site_yml (and the ansible playbooks) are located
         should not be relative

    config_basepath (str): directory where the yaml config file is located

    output_basepath (str): directory where the final Vagrantfile ends up

Example:

        template_path = '../templates/Vagrantfile.template'
        site_yml_path =  '../Rugby-Playbooks/site.yml'
        config_basepath = '../repos/examples'
        output_basepath = '../vm123'
        parse(template_path, site_yml_path, config_basepath, output_basepath)

"""
def parse(template_path, site_yml_path, config_basepath, output_basepath):
    template_path_parts = template_path.split('/')

    template_basepath = '/'.join(template_path_parts[:-1])
    template_name = template_path_parts[-1]

    env = Environment(loader=FileSystemLoader(template_basepath))
    template = env.get_template(template_name)

    config_path = config_basepath +'/' + RUGBY_YML
    generated_vagrantfile_path = output_basepath + '/' + VAGRANTFILE

    with open(config_path, 'r') as config_file:
        vms = yaml.safe_load(config_file)
        with open(generated_vagrantfile_path, 'w') as generated_vagrantfile:
            template_output = template.render(vms = vms, site_yml_path=site_yml_path)
            generated_vagrantfile.write(template_output)


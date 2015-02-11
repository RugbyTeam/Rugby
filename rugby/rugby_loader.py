# internal
import config

# external 
import yaml
from jinja2 import Template

# stdlib
import os

class RugbyLoader:
    """
    Usage:
        rugby_load = RugbyLoader('path/to/.rugby.yml')
        rugby_load.render_vagrant('/opt/VMs')
    
    RugbyLoader globals
        - rugby_conf: path to .rugby.yml
        - rugby_obj: dictionary version of .rugby.yml
    """
    rugby_conf = None
    rugby_obj = None

    def __init__(self, rugby_conf):
        """
        rugby_conf = path to .rugby.yml

        """
        self.rugby_conf = rugby_conf
        
        # Pull VM definitions from rugby_conf
        vms = self._parse()
        # Inject static ip for each VM definition
        for vm in vms:
            vm_group = vm['service']['group']
            vm['ip'] = config.VM_STATIC_IPS[vm_group]
        
        self.rugby_obj = vms

    def render_vagrant(self, dest_dir):
        """
        dest_dir = path to directory where rendered
                   Vagrantfile should go
        """
        # Where vagrantfile will be generated
        generated_vagrantfile = os.path.join(dest_dir, 'Vagrantfile')
        # Where vagrantfile template is located
        vagrant_template_file = config.VAGRANT_TEMPLATE_FILE
        
        with open(vagrant_template_file) as template_file:
            j2_template = Template(template_file.read())
            # Write resulting Vagrantfile to dest_dir
            with open(generated_vagrantfile, 'w') as output_vagrantfile:
                output_vagrantfile.write(j2_template.render(vms=self.rugby_obj, site_yml_path=config.SITE_YML))
    
    def _parse(self):
        """
        Helper function which parses self.rugby_conf, and returns
        the dict version of it
        """
        parsed_config_obj = {}
        with open(self.rugby_conf) as config_file:
            parsed_config_obj = yaml.safe_load(config_file)
        
        return parsed_config_obj


# internal
import config

# external 
import yaml
import pyrx
import jinja2

# stdlib
import os

# import contants from configuration as global variables
valid_groups = config.GROUPS
valid_types  = config.TYPES
valid_group_to_types = config.GROUP_TO_TYPES

# Where vagrantfile template is located
vagrant_template_file = config.VAGRANT_TEMPLATE_FILE
        
# Exception class that is thrown when Validation fails
class ValidationError(Exception):
	pass

# schemas required for validating rugby conf files
conf_vm_service_schema = {
	'type' : '//rec',
	'required' : {
		'group': {'type': '//str'},
		'type':  {'type': '//str'}
	}
}

conf_vm_schema = {
	'type': '//rec',
	'required' : {
   		'name': { 'type': '//str' },
   		'service': conf_vm_service_schema
	}
}

conf_schema = {
	'type': '//arr',
	'length' : {
    	'min' : 1
	},
	'contents': conf_vm_schema    
}

# global object that validates rugby conf files
rx = pyrx.Factory({'register_core_types': True})
schema =  rx.make_schema(conf_schema)

class RugbyLoader:
    """
    Usage:
        rugby_load = RugbyLoader('path/to/.rugby.yml')
        rugby_load.render_vagrant('/opt/VMs')
    
    RugbyLoader static variables
        - valid_groups: groups e
        - valid_types: dictionary version of .rugby.yml
    """

    def __init__(self, rugby_conf, **kwargs):
	"""
	Args:
		rugby_conf (str) path to .rugby.yml
	Kwargs:
		static_ips (list) optionally pass a list static_ips 
		to use for the provision vms
	"""
	self.rugby_conf = rugby_conf

	if 'static_ips' in kwargs:
		static_ips_list = kwargs['static_ips']
		self.static_ips = dict(zip(valid_groups, static_ips_list))
	else:
		self.static_ips = config.VM_STATIC_IPS	

	# Pull VM definitions from rugby_conf
	vms = self._parse()

	self.rugby_obj = vms

	# Validate VM definitions object 
	if not self._valid_config():
		raise ValidationError(rugby_conf + " failed validation")

	# Inject static ip for each VM definition
	for vm in vms:
		vm_group = vm['service']['group']
		vm['ip'] = self.static_ips[vm_group]

    def render_vagrant(self, dest_dir):
        """
        dest_dir = path to directory where rendered
                   Vagrantfile should go
        """
        # Where vagrantfile will be generated
        generated_vagrantfile = os.path.join(dest_dir, 'Vagrantfile')
        with open(vagrant_template_file) as template_file:
            j2_template = jinja2.Template(template_file.read())
            # Write resulting Vagrantfile to dest_dir
            with open(generated_vagrantfile, 'w') as output_vagrantfile:
                output_vagrantfile.write(j2_template.render(vms=self.rugby_obj, site_yml_path=config.SITE_YML))
    
    def _validate_groups_and_types(self):
	"""
	Helper function which checks to see that valid group and type pair
	in self.rugby_obj, returns True if it is a valid group and type pair
	"""
	for vm in self.rugby_obj:
		vm_service = vm['service']
		vm_group = vm_service['group']
		vm_type = vm_service['type']
		
		valid_group = vm_group in valid_groups
		valid_type = vm_type in valid_types 
		valid_pair = (vm_group in valid_group_to_types and 
					vm_type in valid_group_to_types[vm_group])
		
		if not valid_group or not valid_type or not valid_pair:
			return False
	return True

    def _valid_config(self):
	"""
	Helper function which validates self.rugby_obj based on the
	schema defined
	"""
	return schema.check(self.rugby_obj) and self._validate_groups_and_types()
		
    def _parse(self):
        """
        Helper function which parses self.rugby_conf, and returns
        the dict version of it
        """
        parsed_config_obj = {}
        with open(self.rugby_conf) as config_file:
            parsed_config_obj = yaml.safe_load(config_file)
        
        return parsed_config_obj

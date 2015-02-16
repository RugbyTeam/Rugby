# stdlib
from os.path import dirname, abspath, join

VM_STATIC_IPS = {
    'db'   : '192.168.0.15',
    'lang' : '192.168.0.16'
}

GROUPS = ['lang', 'db']
GROUP_TO_TYPES = { 
    'db'   : ['mongo'],
    'lang' : ['node'] 	   
}
TYPES = sorted({vm_type for vm_types in GROUP_TO_TYPES.itervalues() for vm_type in vm_types})

# Rugby constants
DEBUG_MODE = True
BASE_DIR = '/opt/VMs'
LOG_DIR = '/opt/VM_Logs'
SITE_YML = '/opt/Rugby-Playbooks/site.yml'
TEMPLATES_DIR = abspath(join(dirname(__file__), 'templates'))
VAGRANT_TEMPLATE_FILE = join(TEMPLATES_DIR, 'Vagrantfile.j2')

# Logger constants
LOGGER_NAME = 'rugby-console'


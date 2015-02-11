from os.path import dirname, abspath, join

# Virtual machine related constants
VM_BASE_DIR = '/opt/VMs'
VM_STATIC_IPS = {
    'db'   : '192.168.0.15',
    'lang' : '192.168.0.16'
}

# Rugby constants
SITE_YML = '/opt/Rugby-Playbooks/site.yml'
SCRIPTS_DIR = abspath(join(dirname(__file__), 'shell_scripts'))
TEMPLATES_DIR = abspath(join(dirname(__file__), 'templates'))
VAGRANT_TEMPLATE_FILE = join(TEMPLATES_DIR, 'Vagrantfile.j2')
VAGRANT_WRAPPER_SCRIPT = abspath(join(SCRIPTS_DIR, 'vagrant_wrapper.sh'))


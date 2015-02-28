# Rugby

Rugby is a Continuous Integration platform, suitable for running tests for multi tiered applications in a semi-production environment.

Rugby does the following:

* Brings up a cluster of virtual machines
* Copies your project source code to each virtual machine
* Runs any installation commands you specify
* Runs any test commands you specify
* Logs all output from the virtual machines

## Rugby Config

All projects which wish to use Rugby, must have a `.rugby.yml` file. This is how you interact with Rugby.

### Blocks

A block consists of a `name`, `service`, `install`, and `script` fields. Each block corresponds to one virtual machine that is spawned to do your bidding.

If you were testing a web application, you might have one block for your database and one block for your web server.

### Fields

`name`: A unique name for the block

`service`: Specify a particular set of packages which should be pre-installed on the VM. You do this by specifying `group` and `type`.

`group`: Specify what category of packages you would like to install. Possible choices are `lang` and `db`

`type`: Specify a particular cluster of packages to install from a `group`. For `lang` you could choose `node` for example. For `db` you could choose `mongo`.

`install`: Specify a list of commands you would like to run before running any tests. All commands run have sudo permission.

`script`: Specify a list of commands you would like to run which actually run any tests. All commands run have sudo permission.

Below we show an example Rugby config which has one VM block definition, which will have the `node` language group  preinstalled, `apache2` installed before running any test cases, and will run `npm test` to start the test cases.

```yaml
# .rugby.yml

- name: My App Server
  service:
    group: lang
    type: node
  install:
    - apt-get install apache2
  script:
    - npm test
```

## Example Application

```yaml
# .rugby.yml

- name: MongoDB
  service:
    group: db
    type: mongo

- name: UCRCareer
  service:
    group: lang
    type: node
  install: 
    - apt-get -y install build-essential
    - npm install -g bower nodemon gulp mocha 
    - npm install
    - mkdir /opt/resumes
    - chown -R vagrant:vagrant /opt/resumes
  script:
    - mocha
```

```python
# test.py

from rugby import Rugby

def print_status_callback(commit_id, state):
    print "ID: {} \nState: {}\n".format(commit_id, state)

r = Rugby()
r.start_runner('123123123131', 
               'https://github.com/CrazyWearsPJs/UCRcareer.git', 
               '.rugby.yml', 
               print_status_callback);

while 1:
    # Wait till everything is completed
    pass
```

To start off the build, run `python test.py`. Make sure you have the directories specified in `rugby/config.py` created before running the build.

## Development

### Pre-Requisites

* Install [pip](https://pip.pypa.io/en/latest/installing.html)
* Install [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

### Setting up the environment

* Create a directory named `venv`
* Create a virtualenv by running `virtualenv venv`
* Activate virtualenv by running `. venv/bin/activate`
* Install Rugby's dependancies by running `pip install -r requirements.txt`
* Set your PYTHONPATH environment variable to the root of the Rugby project. `export PYTHONPATH=/path/to/Rugby`

### Applying patches

One of our projects dependancies, `python-vagrant`, has an issue which messes with logging. To apply the patch to fix this issue, run the following

```bash
patch venv/lib/python2.7/site-packages/vagrant/__init__.py < patches/vagrant_quiet_logging_issue.patch
```


### Examples

Examples will be located in the `/example` directory. Run any example by running the corresponding example's `run.py`.

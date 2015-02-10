# Rugby

Rugby is a Continuous Integration platform, suitable for running tests for multi tiered applications in a semi-production environment. 

## Rugby Config

All projects which wish to use Rugby, must have a `.rugby.yml` file in the project's root directory. Below we show an example Rugby config.

```yaml
# .rugby.yml

```

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

### Examples

Examples will be located in the `/example` directory. Run any example by running the corresponding example's `run.py`.

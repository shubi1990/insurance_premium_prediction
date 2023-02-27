from setuptools import find_packages, setup
from typing import List

requirements_file_name = "requirements.txt"
REMOVE_PACKAGE = "-e ."

def get_requirements()->List[str]:
    with open(requirements_file_name) as requirements_file:
        requirements_list = requirements_file.readline()
    requirements_list = [requirements_name.replace("\n","") for requirements_name in requirements_list]

    if REMOVE_PACKAGE in requirements_list:
        requirements_list.remove(REMOVE_PACKAGE)
    return requirements_list


setup(name='Insurance',
      version='0.0.1',
      description='Insurance Premium Project',
      author='Rubeena Parveen',
      author_email='rp01061990@gmail.com',
      packages=find_packages(),
      install_requirements = get_requirements()
     )
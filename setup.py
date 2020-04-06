import re
import os

from setuptools import find_packages, setup


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(os.path.dirname(__file__),
                           'microblog_api', '__init__.py')
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        else:
            msg = 'Cannot find version in aiohttpdemo_polls/__init__.py'
            raise RuntimeError(msg)


setup(name='microblog_api',
      version='0.0.1',
      description='Micro blog test project',
      platforms=['POSIX'],
      packages=find_packages(),
      zip_safe=False)
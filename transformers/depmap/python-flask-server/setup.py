# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "openapi_server"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion>=2.0.2",
    "swagger-ui-bundle>=0.0.2",
    "python_dateutil>=2.6.0"
]

setup(
    name=NAME,
    version=VERSION,
    description="Transformer API for DepMap gene-knockout correlations",
    author_email="translator@broadinstitute.org",
    url="",
    keywords=["OpenAPI", "Transformer API for DepMap gene-knockout correlations"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['openapi/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['openapi_server=openapi_server.__main__:main']},
    long_description="""\
    This site provides an API access to gene-knockout correlations based on  [Cancer Dependency Map (DepMap)](https://depmap.org/portal/download/) data. By using this site, you agree to DepMap&#39;s [Terms and Conditions](https://depmap.org/portal/terms/).
    """
)


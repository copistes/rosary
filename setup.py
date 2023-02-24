import setuptools
from distutils.core import setup

setuptools.setup(
    name='rosary',
    version='0.1',
    author='Jean-Baptiste BESNARD',
    description='This is an application to pray the rosary over the dat inside the console.',
    entry_points = {
        'console_scripts': ['rr=rosary.cli:run'],
    },
    packages=["rosary"],
    package_data={"rosary": ["locales/*", "locales/*/*", "locales/*/*/*"]},
    include_package_data=True,
    install_requires=[
        'pyyaml',
        'rich>13.0.0',
        'openai',
        'pyliturgical',
        'python-gettext'
    ],
    python_requires='>=3.5'
)

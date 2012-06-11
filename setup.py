try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import sys

try:
    import pyfrid.version
except ImportError, err:
    print ("ERROR: PyFRID is not installed")
    sys.exit(1)
    


LONG_DESCRIPTION = '''
'''

DESCRIPTION="Package with base classes of data acquisition module, base detector and counter devices and their GUI"

PACKAGE_NAME="PyFRID-Data"

VERSION="0.0.1"

URL=""

NAMESPACE_PACKAGES=['pyfrid',
                    'pyfrid.devices',
                    'pyfrid.commands',
                    'pyfrid.modules',
                    'pyfrid.webapp',
                    'pyfrid.webapp.commands',
                    'pyfrid.webapp.modules',
                    'pyfrid.management',
                    'pyfrid.management.templates',
                    'pyfrid.management.templates.project_template',
                    'pyfrid.management.templates.project_template.commands',
                    'pyfrid.management.templates.project_template.devices',
                    'pyfrid.management.templates.project_template.devices.dummy',
                    'pyfrid.management.templates.project_template.modules',
                    'pyfrid.management.templates.project_template.webapp',
                    ]

LICENSE="Apache"

AUTHOR= 'Denis Korolkov'

AUTHOR_EMAIL= 'pyfrid@gmail.com'

requires = ['numpy', 'matplotlib']

if pyfrid.version.version_info != (0, 0, 1):
    print('ERROR: PyFRID-JCNS package requires PyFRID 0.0.1 to run.')
    sys.exit(1)

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    namespace_packages = NAMESPACE_PACKAGES,
    url=URL,
    #download_url='http://pypi.python.org/pypi/Sphinx',
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    install_requires=requires,
    include_package_data = True
)

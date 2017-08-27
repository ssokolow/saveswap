"""setup.py for N64-Saveswap"""

import io, os, re
from setuptools import setup

__author__ = "Stephan Sokolow"
__license__ = "MIT"

# Get the version from the program rather than duplicating it here
# Source: https://packaging.python.org/en/latest/single_source_version.html
def read(*names, **kwargs):
    """Convenience wrapper for read()ing a file"""
    with io.open(os.path.join(os.path.dirname(__file__), *names),
              encoding=kwargs.get("encoding", "utf8")) as fobj:
        return fobj.read()

def find_version(*file_paths):
    """Extract the value of __version__ from the given file"""
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='n64_saveswap',
    version=find_version("saveswap.py"),
    author='Stephan Sokolow',
    author_email='http://ssokolow.com/ContactMe',
    description='Utility for byte-swapping Nintendo 64 save data',
    long_description=read("README.rst"),
    url="http://github.com/ssokolow/saveswap/",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
    keywords=('byteswap byteswapping endian endianness dump n64 sram '
              'eeprom flash'),
    license="MIT",
    py_modules=['saveswap'],
    entry_points={
        'console_scripts': [
            'saveswap=saveswap:main',
        ],
    },
)

# vim: set sw=4 sts=4 expandtab :

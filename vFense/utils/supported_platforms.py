#!/usr/bin/env python
import platform
import re
import sys

REDHAT_DISTROS = [
    'fedora', 'centos', 'centos linux',
    'redhat', 'red hat enterprise linux server',
    'scientific linux'
]

DEBIAN_DISTROS = ['debian', 'ubuntu', 'linuxmint', 'elementary os']

SUPPORTED_DISTROS = REDHAT_DISTROS + DEBIAN_DISTROS

current_python_version = platform.python_version
SITE_PACKAGES = [f for f in sys.path if f.endswith('packages')]

def get_platform():
    return platform.system().lower()

def get_distro():
    plat = get_platform()
    if plat == 'darwin':
         return 'darwin'

    elif plat == 'linux':
        try:
            return re.sub('"', '', platform.linux_distribution()[0].lower())
        except Exception:
            return re.sub('"', '', platform.dist()[0].lower())

    return ''

def is_distro_supported():
    if get_distro() in SUPPORTED_DISTROS:
        return(True)
    else:
        return(False)


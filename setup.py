# -*- coding: utf-8 -*-

import os
from distutils.core import setup

setup(  name = "pyMapperGUI",
        author = "Tiago Bortoletto Vaz",
        author_email = "tiago@acaia.ca",
        version = "0.4b",
        description = "Cross-platform GUI for libmapper",
        url = "https://github.com/tiagovaz/pyMapperGUI",
        license = "GPLv3",
        packages = ['pymappergui'],
        scripts = ['pyMapperGUI.py'],
        #package_data={
        #       'pymappgergui': ['PyMapperGUI.ico', 'PyMapperGUI_splash.png'],
        #  }
    )

# -*- coding: utf-8 -*-

import os
from distutils.core import setup



setup(	
	name = "pyMapperGUI",
        author = "Tiago Bortoletto Vaz",
        author_email = "tiago@acaia.ca",
        version = "0.1",
        description = "Cross-platform GUI for libmapper",
        url = "https://github.com/tiagovaz/pyMapperGUI",
        license = "GPLv3",
        packages = ["pymappergui"],
	package_data = {"pymappergui": ["images/*.png"]},
        scripts = ['pyMapperGUI.py']
    )

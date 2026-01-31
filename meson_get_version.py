#!/usr/bin/env python3

import os
exec(open(os.path.join(os.getcwd(), "src", "gridmarthe", "_version.py")).read())
print(__version__)

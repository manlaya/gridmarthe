.. SPDX-License-Identifier: GPL-3.0-or-later

.. gridmarthe documentation master file, created by
   sphinx-quickstart on Mon Dec  2 15:02:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. Add your content using ``reStructuredText`` syntax. See the
   `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
   documentation for details.


   ..  This file is part of gridmarthe.

   ..  gridmarthe is a python library to manage grid files for 
   ..  MARTHE hydrogeological computer code from French Geological Survey (BRGM).
   ..  Copyright (C) 2024  BRGM

   ..  This program is free software: you can redistribute it and/or modify
   ..  it under the terms of the GNU General Public License as published by
   ..  the Free Software Foundation, either version 3 of the License, or
   ..  (at your option) any later version.

   ..  This program is distributed in the hope that it will be useful,
   ..  but WITHOUT ANY WARRANTY; without even the implied warranty of
   ..  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   ..  GNU General Public License for more details.

   ..  You should have received a copy of the GNU General Public License
   ..  along with this program.  If not, see <https://www.gnu.org/licenses/>.


==========
gridmarthe
==========
**Date** : |today| **Version**: |release|


`gridmarthe` is a Python project for (fast) operations on Marthe grid files.

`Marthe <https://www.brgm.fr/en/software/marthe-modelling-software-groundwater-flows>`_
is a hydrogeological modelling code developped at BRGM, French Geological Survey
:cite:`2020:thiery_guidelines`.

This library is open-source and released under the GNU General Public License (v3+).


.. check :doc:`getting_started/install`. // no extension
.. with extension autosectionlabel :ref:`leTitreVisé`
   
 ..  to add image => :img-top: _static/index_getting_started.svg


.. grid:: 1 1 2 2 
   :gutter: 1
   
   .. grid-item-card:: Getting started
      :link: getting_started/index
      :link-type: doc

      Installation procedure, summary of the library

   .. grid-item-card:: User guide
      :link: user_guide/index
      :link-type: doc

      The user guide provides information about the package, and how
      to use it with examples.

   .. grid-item-card:: API reference
      :link: api/index
      :link-type: doc

      Description of the API: functions, methods and arguments expected.

   .. grid-item-card:: About
      :link: references
      :link-type: doc

      Information and references

.. toctree::
   :maxdepth: 1
   :hidden:

   Getting Started <getting_started/index>
   User guide <user_guide/index>
   API Reference <api/index>
   About <references>

.. .. include:: ../../README.md



Index and tables
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
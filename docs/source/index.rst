.. gridmarthe documentation master file, created by
   sphinx-quickstart on Mon Dec  2 15:02:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. Add your content using ``reStructuredText`` syntax. See the
   `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
   documentation for details.

==========
GridMarthe
==========
**Date** : |today| **Version**: |release|


Gridmarthe is a Python project for (fast) operations on Marthe grid files.

`Marthe <https://www.brgm.fr/en/software/marthe-modelling-software-groundwater-flows>`_
is a hydrogeological modelling code developped at BRGM, French Geological Survey
:cite:`2020:thiery_guidelines`.

This library is open-source and released under the GNU General Public License (v3+).


.. check :doc:`getting_started/install`. // no extension
.. with extension autosectionlabel :ref:`leTitreVisé`
   
 ..  to add image => :img-top: _static/index_getting_started.svg

.. warning::
   This documentation and the library itself are under heavy developpement

.. grid:: 1 1 2 2 
   
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
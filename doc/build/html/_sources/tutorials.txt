Tutorials
=========

Importing RockPy
----------------

Before we can use anything in RockPy we have to make sure that it is properly installed on the system and can be imported.
Try importing it in a python console:

.. code-block:: python

   import RockPy

if you get an error message it means that either you do not have RockPy installed or it is not properly set in you
PYTHONPATH variable. To permanently fix this you will have to ask Google, for a temporary fix, locate the folder at
which RockPy is stored. In this test case it is stored at ``~/PycharmsProjects/RockPy``.

What we have to do is manually append it to the PYTHONPATH. You can copy/paste the following.

.. code-block:: python

   import sys
   import os.path
   from os.path import join
   home = os.path.expanduser('~')
   RockPy_folder = 'PycharmProjects' # here you can change it to the path you have stored RockPy in
   sys.path.append(join(home, RockPy_path))

try importing it again, it should work now.

**Welcome to RockPy**


The Sample
----------

This tutorial is about how to create a sample and what we can do with a sample.

Creating a sample
+++++++++++++++++

The sample is the most basic structure in rockpy. It contains all measurements and series. It also contains some
functionality that I will show you a little later. Lets start making a sample. We will be using the test data that is
included in RockPy but of course you can use whatever sample you want.

.. code-block:: python

   Sample = RockPy.Sample(name='pyrrhotite')

This is the most basic way of defining a sample - just a name. We can also become a little more sophisticated.

.. code-block:: python

   Sample = RockPy.Sample(name='pyrrhotite', mass=54.2, mass_unit='mg', height=3.21, diamter = 5.43, length_unit = 'mm')

You can see there are lost of options you can give to a sample. In this case we are telling RockPy that we are dealing with
a sample that is named *pyrrhotite* and weighs 54.2 mg etc.

We succesfully created a sample. We can now start adding measurements.

Adding a measurement
++++++++++++++++++++

You can add as man measurements to a sample as you like. We will start with a simple hysteresis measurement. For this,
we have measured a hysteresis at room temperature with a Princeton Instruments VSM. The data file is located in RockPys
testdata folder and can be accessed with ``RockPy.test_data_path``.

A measurement is always added using the ``yoursample.add_measurement`` method. There are several things you have to tell
RockPy in order to get it to work.

**mandatory**
# *machine:* the file format or machine, in this case ``machine = 'vsm'``
# *mfile:* the location of the file, here the file is located in the ``RockPy.test_data_path`` under ``vsm``.
Therefore ``mfile=os.path.join(RockPy.test_data_path, 'vsm', 'LTPY_527,1a_HYS_VSM#XX[mg]___#TEMP_300_K#STD000.000')``[#f1]_
# *mtype:* the type of measurement. In this case ``mtype='hys'``

.. code-block:: python

   Sample.add_measurement()

There are a few extra arguments you can add to give RockPy a little more information on your measuremnt.
#todo link to advanced tutorial where these things will be explained

.. rubric:: Footnotes

.. [#f1] os.path.join is a builtin python function. It combines folders depending on your operating system. You have
to import it first in order to use it. This doen by typeing: ``import os.path``. Now you can use ``os.path.join()``
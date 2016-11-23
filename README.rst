==============
migrations4neo
==============
:Info: Easy migrations for neo4j 
:Repository: https://github.com/turkus/migrations4neo
:Author: Wojciech Rola 
:Maintainer: Wojciech Rola 

How to start?
-------------

We need to create basics:

.. code-block:: console

    mig4neo init mig4neo ./

It will create ``mig4neo`` folder and subfolder called versions, where your migrations will land.
You have to provide directory where ``mig4neo`` folder should be created.

Then you have to edit ``mig4neo.ini`` according your needs.
If necessary change its location. When do that just point where your ``mig4neo.ini`` lands
using config option:

.. code-block:: console

    mig4neo -c ../mig4neo.ini

What's next?
------------

Create revision:

.. code-block:: console

    mig4neo revision -m 'This is my revision'
  
Then adjust it by editing revision's file (*.py).

With config option:

.. code-block:: console

    mig4neo -c ../mig4neo.ini revision -m 'This is my revision'


Make it happen
--------------

Upgrade db:

.. code-block:: console

    mig4neo upgrade --revisions 4asvg34,3fadg4

You can also downgrade:

.. code-block:: console

    mig4neo downgrade --revisions 4asvg34,3fadg4e

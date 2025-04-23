Usage
=====

Run third-party library tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

django-allauth
++++++++++++++

.. warning::

   If you install ``lxml`` and ``xmlsec`` via ``pip`` instead of
   ``just install`` :ref:`as described here <additional-installation-steps>`
   you may encounter test failures due to `issues like this one
   <https://github.com/xmlsec/python-xmlsec/issues/320>`_.

::

    dm repo test django-allauth


When completed successfully the output should look something like this:

.. image:: _static/images/django-allauth.png

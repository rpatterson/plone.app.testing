.. -*-doctest-*-

===================
Plone's Testing API
===================

The Plone Testing API provides a set of testing fixtures as well as
layer base classes and test case base classes which provide the same
methods to manipulate the test environment.


Fixtures
========

A fixture is just the specific environment in which a test is run.
IOW, a given set of tests may require certain content and
configuration to be in place for the test to run.  That set of content
and configuration is the fixture for those tests.

The plone testing API provides a few different test fixtures against
which you can run your tests.  These fixtures aim to satisfy the needs
most common to tests for Plone itself and Plone add-ons.


Layers
======

If your tests have more specific needs, you may need to define your
own test fixture.  If a test fixture is particularly full-featured, as
most Plone test fixtures are, they can take significant time to set
up, especially if they're set up for each individual test.

The test runner provided by `zope.tesrunner`_ supports defining test
fixtures in layers which can be shared between individual tests.  As
such, they can greatly reduce the test run time when many tests are
run against expensive fixtures.  It can, however, also be very hard to
guarantee isolation between individual tests when using layers such
that one test doesn't affect the environment of another test causing a
false failure.  This is probably the most important service provided
by `plone.testing`_, a framework for defining layers with test
isolation you can count on.


TestCase Classes
================

Test fixture should only be put into layers when you're sure you will
be running many tests against that fixture.  It is also best to resist
the urge to put a bit of test fixture needed by one test into the
layer because you already have code doing what you need in the layer.

To that end, the Plone Testing API provides `unittest.TestCase`_ base
classes with helper methods and functions identical to those used to
build custom layers.  IOW, it should be the same and just as easy to
add test fixture to individual tests as it is to layers.


Common Conveniences
===================

When using the plone.app.testing.api.PLONE_DEFAULT_FIXTURE layer then
a few commonly useful things will be set up.

    >>> portal = layer.portal

Unauthorized or NotFound exceptions can sometimes hide root problems
when doing functional testing.  As such, only Redirect remains ignored
by the error_log.

    >>> portal.error_log.getProperties()['ignored_exceptions']
    ('Redirect',)

The resource registries are placed in debug mode to make it easier to
inspect the individual CSS, JavaScript, and KSS resources in the HTML
output for functional testing.

    >>> portal.portal_css.getDebugMode()
    True
    >>> portal.portal_javascripts.getDebugMode()
    True
    >>> portal.portal_kss.getDebugMode()
    True


Migrating From PloneTestCase
============================

Simple tests using PloneTestCase and/or the layers there should be
fairly easy to migrate to ``plone.app.testing.api`` requiring only
small changes for docfile tests:

* Remove all imports from ``Products.PloneTestCase`` and the Zope2
  ``Testing`` module, including ``Testing.ZopeTestCase``.  Replace
  them with the appropriate imports from ``plone.app.testing.api``,
  specific details for common cases below.

* For layers based on ``collective.testcaselayer``, convert all layer
  classes to use just the ``plone.app.testing.api.PloneTestLayer``
  base class.

* Your layers may be instantiated without any bases if the
  ``plone.app.testing.api.PLONE_DEFAULT_FIXTURE`` is the appropriate
  base layer.

* Convert ``Products.PloneTestCase.ptc.PloneTestCase`` to
  ``plone.app.testing.api.PloneTestCase``>

* There's no longer any need for ``FunctionalTestCase`` variants of
  your test case classes.  Just use the one with a
  ``plone.app.testing.api.PloneTestCase`` base class and the
  appropriate layer based on ``plone.app.testing.api.PloneTestLayer``
  for all your tests.

* Convert ``installPackage`` and ``installProduct`` from
  ``Testing.ZopeTestCase`` to use ``self.installProduct``.

* Wrap your ``DocFileSuites`` in `plone.testing.layerd
  <http://pypi.python.org/pypi/plone.testing#doctest-fixtures-and-layers>`_.


.. _zope.tesrunner: http://pypi.python.org/pypi/zope.testrunner#layers
.. _plone.testing: http://pypi.python.org/pypi/plone.testing
.. _unittest.TestCase: http://docs.python.org/library/unittest.html#unittest.TestCase
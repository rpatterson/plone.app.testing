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

The test runner provided by `zope.tesrunner` supports defining test
fixtures in layers which can be shared between individual tests.  As
such, they can greatly reduce the test run time when many tests are
run against expensive fixtures.  It can, however, also be very hard to
guarantee isolation between individual tests when using layers such
that one test doesn't affect the environment of another test causing a
false failure.  This is probably the most important service provided
by `plone.testing`, a framework for defining layers with test
isolation you can count on.


TestCase Classes
================

Test fixture should only be put into layers when you're sure you will
be running many tests against that fixture.  It is also best to resist
the urge to put a bit of test fixture needed by one test into the
layer because you already have code doing what you need in the layer.

To that end, the Plone Testing API provides `unittest.TestCase` base
classes with helper methods and functions identical to those used to
build custom layers.  IOW, it should be the same and just as easy to
add test fixture to individual tests as it is to layers.


Migrating From PloneTestCase
============================
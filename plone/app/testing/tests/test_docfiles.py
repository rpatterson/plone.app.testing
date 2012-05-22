import unittest2 as unittest
import doctest

from plone.testing import layered
from plone.app import testing
from plone.app.testing import api
from plone.app.testing.tests.test_api import TestPloneTestCase

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


# Dummy handler used in tests
def dummy(context):
    pass


def setUpLayerInstance(test):
    test.globs['self'] = api.PLONE_DEFAULT_TESTING


def setUpCaseInstance(test):
    test.globs['self'] = instance = TestPloneTestCase()
    instance.setUp()
    

def test_suite():
    suite = unittest.TestSuite()
    seltest = doctest.DocFileSuite('selenium.rst', package=testing,
                                   optionflags=OPTIONFLAGS)
    # Run selenium tests on level 2, as it requires a correctly configured
    # Firefox browser
    seltest.level = 2

    suite.addTests([
        doctest.DocFileSuite('cleanup.rst', package=testing,
                             optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('layers.rst', package=testing,
                             optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('helpers.rst', package=testing,
                             optionflags=OPTIONFLAGS),
        layered(doctest.DocFileSuite(
            'api.rst',
            'api_signature.rst',
            'mail.rst',
            package=testing, optionflags=OPTIONFLAGS,
            setUp=setUpCaseInstance),
                layer=api.PLONE_DEFAULT_TESTING),
        layered(doctest.DocFileSuite(
            'api_signature.rst',
            package=testing, optionflags=OPTIONFLAGS,
            setUp=setUpLayerInstance),
                layer=api.PLONE_DEFAULT_TESTING),
        seltest,
    ])
    return suite

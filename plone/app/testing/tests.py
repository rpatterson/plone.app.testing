import unittest2 as unittest
import doctest

from plone.app.testing import api

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE


# Dummy handler used in tests
def dummy(context):
    pass


def setUpLayerInstance(test):
    test.globs['instance'] = api.PLONE_TESTING_FIXTURE


def setUpCaseInstance(test):
    test.globs['instance'] = instance = api.PloneTestCase()
    instance.setUp()
    

def test_suite():
    suite = unittest.TestSuite()
    seltest = doctest.DocFileSuite('selenium.rst', optionflags=OPTIONFLAGS)
    # Run selenium tests on level 2, as it requires a correctly configured
    # Firefox browser
    seltest.level = 2

    api_suite = unittest.TestSuite([
        doctest.DocFileSuite('api_signature.rst', optionflags=OPTIONFLAGS,
                             setUp=setUpLayerInstance),
        doctest.DocFileSuite('api_signature.rst', optionflags=OPTIONFLAGS,
                             setUp=setUpCaseInstance),
        ])
    api_suite.layer = api.PLONE_TESTING_FIXTURE

    suite.addTests([
        doctest.DocFileSuite('cleanup.rst', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('layers.rst', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('helpers.rst', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('api.rst', optionflags=OPTIONFLAGS),
        api_suite,
        seltest,
    ])
    return suite

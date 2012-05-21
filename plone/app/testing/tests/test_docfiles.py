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


class TestPloneTestLayer(api.PloneTestLayer):

    def setUpPloneSite(self, portal):
        """Abuse the setUp to keep convenience attributes around."""
        super(TestPloneTestLayer, self).setUpPloneSite(portal)
        self._portal_context = testing.ploneSite()
        self.setUpAttrs(self._portal_context.__enter__())

    def tearDownPloneSite(self, portal):
        """Clean up the abuse."""
        self.tearDownAttrs()
        self._portal_context.__exit__(None, None, None)
        del self._portal_context
        super(TestPloneTestLayer, self).tearDownPloneSite(portal)

TEST_PLONE_TEST_FIXTURE = TestPloneTestLayer()        


def setUpLayerInstance(test):
    test.globs['self'] = TEST_PLONE_TEST_FIXTURE


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
                layer=api.PLONE_DEFAULT_FIXTURE),
        layered(doctest.DocFileSuite(
            'api_signature.rst',
            package=testing, optionflags=OPTIONFLAGS,
            setUp=setUpLayerInstance),
                layer=TEST_PLONE_TEST_FIXTURE),
        seltest,
    ])
    return suite

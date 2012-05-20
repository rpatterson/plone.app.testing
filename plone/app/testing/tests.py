import unittest2 as unittest
import doctest

from plone.app import testing
from plone.app.testing import api

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
    test.globs['instance'] = TEST_PLONE_TEST_FIXTURE


def setUpCaseInstance(test):
    test.globs['instance'] = instance = api.PloneTestCase()
    instance.setUp()
    

def test_suite():
    suite = unittest.TestSuite()
    seltest = doctest.DocFileSuite('selenium.rst', optionflags=OPTIONFLAGS)
    # Run selenium tests on level 2, as it requires a correctly configured
    # Firefox browser
    seltest.level = 2

    api_signature_layer = doctest.DocFileSuite(
        'api_signature.rst', optionflags=OPTIONFLAGS,
        setUp=setUpLayerInstance)
    api_signature_layer.layer = TEST_PLONE_TEST_FIXTURE
    api_signature_case = doctest.DocFileSuite(
        'api_signature.rst', optionflags=OPTIONFLAGS,
        setUp=setUpCaseInstance)
    api_signature_case.layer = api.PLONE_DEFAULT_FIXTURE

    suite.addTests([
        doctest.DocFileSuite('cleanup.rst', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('layers.rst', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('helpers.rst', optionflags=OPTIONFLAGS),
        doctest.DocFileSuite('api.rst', optionflags=OPTIONFLAGS),
        api_signature_layer,
        api_signature_case,
        seltest,
    ])
    return suite

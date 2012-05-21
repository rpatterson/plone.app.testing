import random
import unittest2 as unittest

import transaction

from plone.testing import z2
from plone.app.testing import api


class TestPloneTestCase(api.PloneTestCase):

    layer = api.PLONE_DEFAULT_FIXTURE

    def runTest(self):
        pass

    def test_plone_test_case(self):
        from Products.CMFPlone.Portal import PloneSite
        self.assertIsInstance(self.portal, PloneSite)
        from OFS.Application import Application
        self.assertIsInstance(self.app, Application)
        from Products.ATContentTypes.content.folder import ATFolder
        self.assertIsInstance(self.folder, ATFolder)


class TestIntegrationLayerPerformance(unittest.TestCase):

    layer = z2.INTEGRATION_TESTING
        
    def test_layer_performance(self):
        with z2.zopeApp() as app:
            setattr(app, str(random.randint(0, 1000000)),
                    random.randint(0, 1000000))

    for idx in xrange(1000):
        locals()['test_layer_performance_%s' % idx] = test_layer_performance


class TestFunctionalLayerPerformance(unittest.TestCase):

    layer = z2.FUNCTIONAL_TESTING
        
    def test_layer_performance(self):
        with z2.zopeApp() as app:
            setattr(app, str(random.randint(0, 1000000)),
                    random.randint(0, 1000000))
        transaction.commit()

    for idx in xrange(1000):
        locals()['test_layer_performance_%s' % idx] = test_layer_performance

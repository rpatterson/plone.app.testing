from plone.app.testing import api


class TestPloneTestCase(api.PloneTestCase):

    layer = api.PLONE_DEFAULT_TESTING

    def runTest(self):
        pass

    def test_plone_test_case(self):
        from Products.CMFPlone.Portal import PloneSite
        self.assertIsInstance(self.portal, PloneSite)
        from OFS.Application import Application
        self.assertIsInstance(self.app, Application)
        from Products.ATContentTypes.content.folder import ATFolder
        self.assertIsInstance(self.folder, ATFolder)

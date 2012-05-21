import unittest

from zope.dottedname.resolve import resolve

from AccessControl import getSecurityManager

from Products.CMFCore.utils import getToolByName

from plone.testing import z2
from plone.app import testing 


class PloneTest(object):

    def afterSetUp(self):
        """
        Called after setUp() has completed.

        May be overridden by subclasses to perform additional test set up.
        """
        pass

    def beforeTearDown(self):
        """
        Called before tearDown() is executed.

        May be overridden by subclasses to perform additional test clean up.
        """
        pass

    def installProduct(self, productName):
        """
        Initialize the Zope 2 product with the given name.

        Also loads its ZCML first.
        """
        package = resolve(productName)
        try:
            self.loadZCML(name='meta.zcml', package=package)
            self.loadZCML(name='configure.zcml', package=package)
            self.loadZCML(name='overrides.zcml', package=package)
        except IOError:
            pass  # Tolerate missing ZCML, not required
        z2.installProduct(self.app, productName)
            
    def setRoles(self, roles, userId=testing.TEST_USER_ID):
        """Set the given user's roles to a tuple of roles."""
        testing.setRoles(self.portal, userId, roles)

    def setGroups(self, groups, userId=testing.TEST_USER_ID):
        """Set the given user's groups to a tuple of groups."""
        uf = self.portal.acl_users
        uf._updateUser(userId, groups=list(groups))
        if userId == getSecurityManager().getUser().getId():
            self.login(userId)

    def login(self, userName=testing.TEST_USER_NAME):
        """Log in to the portal as the given user."""
        testing.login(self.portal, userName)

    def loginAsPortalOwner(self, userName=testing.SITE_OWNER_NAME):
        """Log in to the portal as the user who created it."""
        z2.login(self.app['acl_users'], userName)

    def logout(self):
        """Log out, i.e. become anonymous."""
        testing.logout()

    def addProfile(self, name):
        """Imports an extension profile into the site."""
        testing.applyProfile(self.portal, name)

    def addProduct(self, name):
        """Quickinstalls a product into the site."""
        testing.quickInstallProduct(self.portal, name)


class PloneAPILayer(testing.PloneSandboxLayer, testing.FunctionalTesting,
                    PloneTest):
    # Standardize on FunctionalTesting for simpler testing
    #
    # Some quick performance testing of integration vs functional
    # layers found the run times of these 1000 test to be the same
    # both as reported by the testrunner and as reported by the `time`
    # command.  Given this, just standardize on functional testing
    # since it has no apparent additional cost and is much less
    # surprising when users call `transaction.commit` during tests.


    defaultBases = (testing.PLONE_FIXTURE, )

    @property
    def app(self):
        """Get the Zope 2 app from the layer resource."""
        return self['app']

    @property
    def portal(self):
        """Get the Plone site from the layer resource."""
        return self['portal']

    @property
    def folder(self):
        """Get the default user's folder from the layer resource."""
        return self['folder']

    def setUpFolder(self):
        membership = getToolByName(self.portal, 'portal_membership')
        self['folder'] = membership.getHomeFolder(testing.TEST_USER_ID)
        assert self['folder'] is not None

    def testSetUp(self):
        """Set aside the layer's storage before stacking for the test."""
        self['layer_zodbDB'] = self['zodbDB']
        super(PloneAPILayer, self).testSetUp()
        self.setUpFolder()

    def testTearDown(self):
        """Restore the layer's storage after unstacking for the test."""
        del self['folder']
        super(PloneAPILayer, self).testTearDown()
        self['zodbDB'] = self['layer_zodbDB']
        del self['layer_zodbDB']


class PloneDefaultLayer(PloneAPILayer):
    """Sets up a Plone site closer to the default OOTB Plone site."""

    defaultBases = (testing.PLONE_FIXTURE, )

    def setUpPloneSite(self, portal):
        self['portal'] = portal
        self['app'] = portal.getPhysicalRoot()
        try:
            self.setUpDefaultPlone()
            self.setUpMockMailHost()
            self._setupUser()
            self.login()
            self._setupHomeFolder()
            self.setUpFolder()
        finally:
            del self['portal']
            del self['app']

    def setUpDefaultPlone(self):
        self.installProduct('Products.PythonScripts')
        self.addProfile('Products.CMFPlone:plone')
        self.addProfile('Products.CMFPlone:plone-content')
    
    def _setupUser(self, userId=testing.TEST_USER_ID,
                   password=testing.TEST_USER_PASSWORD):
        """Creates the default user."""
        uf = getToolByName(self.portal, 'acl_users')
        uf.userFolderAddUser(userId, password, ['Member'], [])

    def _setupHomeFolder(self, userId=testing.TEST_USER_ID):
        """Creates the default user's home folder."""
        membership = getToolByName(self.portal, 'portal_membership')
        if not membership.getMemberareaCreationFlag():
            membership.setMemberareaCreationFlag()
        membership.createMemberArea(userId)

    def setUpMockMailHost(self):
        """Gather sent messages in portal.MailHost.messages."""
        self.portal._original_MailHost = self.portal.MailHost
        self.loadZCML('api.zcml', package=testing)
        self.addProfile('plone.app.testing:api')

    def setUpErrorLog(self):
        """
        Don't ignore exceptions so that problems aren't hidden.

        Unauthorized or NotFound exceptions can sometimes hide root
        problems when doing functional testing.  As such, only
        Redirect remains ignored by the error_log.
        """
        error_props = self.portal.error_log.getProperties()
        error_props['ignored_exceptions'] = ('Redirect',)
        error_props = self.portal.error_log.setProperties(
            **error_props)

    def setUpResourceRegistries(self):
        """
        Put resource registries in debug mode.

        This makes it easier to inspect CSS, JavaScript, and KSS in
        the HTML output for functional testing.
        """
        self.portal.portal_css.setDebugMode(True)
        self.portal.portal_javascripts.setDebugMode(True)
        self.portal.portal_kss.setDebugMode(True)

PLONE_DEFAULT_FIXTURE = PloneDefaultLayer()


class PloneTestLayer(PloneAPILayer):

    defaultBases = (PLONE_DEFAULT_FIXTURE, )

    def setUpPloneSite(self, portal):
        """Delegate to the conventional hook method."""
        self.setUpFolder()
        self.afterSetUp()  # TODO cover me!

    def tearDownPloneSite(self, portal):
        """Delegate to the conventional hook method."""
        self.beforeTearDown()  # TODO cover me!
        del self['folder']


class PloneTestCase(unittest.TestCase, PloneTest):

    layer = PLONE_DEFAULT_FIXTURE

    @property
    def app(self):
        """Get the Zope 2 app from the layer resource."""
        return self.layer.app

    @property
    def portal(self):
        """Get the Plone site from the layer resource."""
        return self.layer.portal

    @property
    def folder(self):
        """Get the default user's folder from the layer resource."""
        return self.layer.folder

    def setUp(self):
        """Delegate to the conventional hook method."""
        super(PloneTestCase, self).setUp()
        self.afterSetUp()

    def tearDown(self):
        """Delegate to the conventional hook method."""
        self.beforeTearDown()
        super(PloneTestCase, self).tearDown()
        
    def loadZCML(self, name='configure.zcml', **kw):
        """Load a ZCML file, configure.zcml by default."""
        self.layer.loadZCML(name=name, **kw)

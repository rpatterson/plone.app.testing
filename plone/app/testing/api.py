import contextlib

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

    def setUpAttrs(self, portal):
        """Set up the convenience attributes."""
        self.portal = portal
        self.app = portal.getPhysicalRoot()
        membership = getToolByName(self.portal, 'portal_membership')
        self.folder = membership.getHomeFolder(testing.TEST_USER_ID)

    def tearDownAttrs(self):
        """Tear down the convenience attributes."""
        del self.folder
        del self.app               
        del self.portal

    @contextlib.contextmanager
    def withAttrs(self, portal):
        self.setUpAttrs(portal)
        yield self
        self.tearDownAttrs()


class PloneTestLayer(testing.PloneSandboxLayer, PloneTest):

    def setUpPloneSite(self, portal):
        """Add convenience attributes then delegate to the hook method."""
        with self.withAttrs(portal):
            self.afterSetUp()

    def tearDownPloneSite(self, portal):
        """Delegate to the hook method then clean up convenience attributes."""
        with self.withAttrs(portal):
            self.beforeTearDown()

PLONE_TESTING_FIXTURE = PloneTestLayer()
        

class PloneTestCase(testing.PloneSandboxLayer, PloneTest):

    layer = PLONE_TESTING_FIXTURE

    def setUp(self):
        self._portal_context = testing.ploneSite()
        self.setUpAttrs(self._portal_context.__enter__())
        self.afterSetUp()

    def tearDown(self):
        try:
            self.beforeTearDown()
        finally:
            self.tearDownAttrs()
            self._portal_context.__exit__(None, None, None)
            del self._portal_context
        
    def loadZCML(self, name='configure.zcml', **kw):
        """Load a ZCML file, configure.zcml by default."""
        self.layer.loadZCML(name=name, **kw)

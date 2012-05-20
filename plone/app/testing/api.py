from zope.dottedname.resolve import resolve

from AccessControl import getSecurityManager

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


class PloneTestLayer(testing.PloneSandboxLayer, PloneTest):

    @property
    def app(self):
        return self['app']

    @property
    def portal(self):
        return self['portal']

    def setUpPloneSite(self, portal):
        """Add convenience attributes then delegate to the hook method."""
        with z2.zopeApp() as app:
            self['app'] = app
            with testing.ploneSite() as portal:
                self['portal'] = portal
                self.afterSetUp()
                del self['portal']
            del self['app']                

        import Zope2
        self['app'] = z2.addRequestContainer(Zope2.app())

        # TODO Not happy about this, would be nice to refactor
        # ploneSite() such that the knowledge of what site setup needs
        # to happen could be shared with cases such as this where a
        # context manager can't be used.
        self._portal_context = testing.ploneSite()
        self['portal'] = self._portal_context.__enter__()

    def tearDownPloneSite(self, portal):
        """Delegate to the hook method then clean up convenience attributes."""
        del self['portal']
        self._portal_context.__exit__(None, None, None)
        del self._portal_context

        self.app.REQUEST.close()
        self.app._p_jar.close()
        del self['app']

        with z2.zopeApp() as app:
            self['app'] = app
            with testing.ploneSite() as portal:
                self['portal'] = portal
                self.beforeTearDown()
                del self['portal']
            del self['app']                

PLONE_TESTING_FIXTURE = PloneTestLayer()
        

class PloneTestCase(testing.PloneSandboxLayer, PloneTest):

    layer = PLONE_TESTING_FIXTURE

    def setUp(self):
        self.app = self.layer.app
        self.portal = self.layer.portal

        self.afterSetUp()

    def tearDown(self):
        self.beforeTearDown()

        del self.app
        del self.portal

    def loadZCML(self, name='configure.zcml', **kw):
        """Load a ZCML file, configure.zcml by default."""
        self.layer.loadZCML(name=name, **kw)

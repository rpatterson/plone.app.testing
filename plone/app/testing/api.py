import sys
import contextlib
import unittest

from zope.dottedname.resolve import resolve
from zope.configuration import xmlconfig

from AccessControl import getSecurityManager

from Products.CMFCore.utils import getToolByName

from plone.testing import z2
from plone.app import testing 


class PloneTest(object):

    def beforeSetUp(self):
        """
        Called before the Plone site is created and configured.

        May be overridden by subclasses to perform additional test set
        up before a portal is created, such as using self.loadZCML().
        """
        pass

    def afterSetUp(self):
        """
        Called after the Plone site has been created and configured.

        May be overridden by subclasses to perform additional test set
        up that involves making changes to the Plone site.
        """
        pass

    def beforeTearDown(self):
        """
        Called before the Plone site is removed and cleaned up.

        May be overridden by subclasses to perform additional test
        clean up that needs access to the Plone site.
        """
        pass

    def afterTearDown(self):
        """
        Called after the Plone site has been removed and cleaned up.

        May be overridden by subclasses to perform additional test
        clean up, such as cleaning up any global state change not
        already isolated by plone.testing.
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
    
    def addUser(self, userId=testing.TEST_USER_ID,
                   password=testing.TEST_USER_PASSWORD):
        """Creates a user, plone.app.testing.TEST_USER_ID by default."""
        uf = getToolByName(self.portal, 'acl_users')
        uf.userFolderAddUser(userId, password, ['Member'], [])

    def addHomeFolder(self, userId=testing.TEST_USER_ID):
        """
        Creates a user's home folder.

        Creates plone.app.testing.TEST_USER_ID's by default.
        """
        membership = getToolByName(self.portal, 'portal_membership')
        if not membership.getMemberareaCreationFlag():
            membership.setMemberareaCreationFlag()
        membership.createMemberArea(userId)


class PloneAPILayer(PloneTest):
    # Standardize on FunctionalTesting for simpler testing
    #
    # Some quick performance testing of integration vs functional
    # layers found the run times of these 1000 test to be the same
    # both as reported by the testrunner and as reported by the `time`
    # command.  Given this, just standardize on functional testing
    # since it has no apparent additional cost and is much less
    # surprising when users call `transaction.commit` during tests.


    defaultBases = (testing.PLONE_FIXTURE, )

    def __init__(self, bases=None, name=None, module=None):
        """Automatically name layers, even with bases passed in."""
        if name is None:
            name = self.__class__.__name__
        if module is None:
            # Get the module name of whatever instantiated the layer, not
            # the class, by default
            try:
                module = sys._getframe(1).f_globals['__name__']
            except (ValueError, AttributeError, KeyError,):
                module = self.__class__.__module__
        super(PloneAPILayer, self).__init__(
            bases=bases, name=name, module=module)

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

    def loadZCML(self, name='configure.zcml', **kw):
        """Load a ZCML file, configure.zcml by default."""
        kw.setdefault('context', self['configurationContext'])
        return xmlconfig.file(name, **kw)

    @contextlib.contextmanager
    def withApp(self, app):
        self['app'] = app
        yield app
        del self['app']

    @contextlib.contextmanager
    def withPortal(self, portal):
        self['portal'] = portal
        self['app'] = portal.getPhysicalRoot()
        membership = getToolByName(self.portal, 'portal_membership')
        self['folder'] = membership.getHomeFolder(testing.TEST_USER_ID)

        yield portal

        del self['folder']
        del self['portal']
        del self['app']

    def setUpZope(self, app, configurationContext):
        """Delegate to the conventional hook method."""
        with self.withApp(app) as app:
            self.beforeSetUp()  # TODO cover me!

    def setUpPloneSite(self, portal):
        """Delegate to the conventional hook method."""
        with self.withPortal(portal) as portal:
            self.afterSetUp()  # TODO cover me!

    def tearDownPloneSite(self, portal):
        """Delegate to the conventional hook method."""
        with self.withPortal(portal) as portal:
            self.beforeTearDown()  # TODO cover me!

    def tearDownZope(self, app):
        """Delegate to the conventional hook method."""
        with self.withApp(app) as app:
            self.afterTearDown()  # TODO cover me!


class PloneDefaultLayer(PloneAPILayer, testing.PloneSandboxLayer):
    """Sets up a Plone site closer to the default OOTB Plone site."""

    defaultBases = (testing.PLONE_FIXTURE, )

    def afterSetUp(self):
        self.setUpDefaultPlone()
        self.setUpMockMailHost()
        self.setUpErrorLog()
        self.setUpResourceRegistries()
        self.addUser()
        self.login()
        self.addHomeFolder()

    def setUpDefaultPlone(self):
        self.installProduct('Products.PythonScripts')
        self.addProfile('Products.CMFPlone:plone')
        self.addProfile('Products.CMFPlone:plone-content')

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


class PloneDefaultTesting(testing.FunctionalTesting, PloneAPILayer):
    """Sets up a Plone site closer to the default OOTB Plone site."""

    defaultBases = (PLONE_DEFAULT_FIXTURE, )

    def testSetUp(self):
        """Set aside the layer's storage before stacking for the test."""
        super(PloneDefaultTesting, self).testSetUp()
        membership = getToolByName(self.portal, 'portal_membership')
        self['folder'] = membership.getHomeFolder(testing.TEST_USER_ID)

    def testTearDown(self):
        """Restore the layer's storage after unstacking for the test."""
        del self['folder']
        super(PloneDefaultTesting, self).testTearDown()

PLONE_DEFAULT_TESTING = PloneDefaultTesting()


class PloneTestLayer(PloneAPILayer, testing.PloneSandboxLayer):

    defaultBases = (PLONE_DEFAULT_TESTING, )


class PloneTestCase(unittest.TestCase, PloneTest):

    layer = PLONE_DEFAULT_TESTING

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
        self.beforeSetUp()
        super(PloneTestCase, self).setUp()
        self.afterSetUp()

    def tearDown(self):
        """Delegate to the conventional hook method."""
        self.beforeTearDown()
        super(PloneTestCase, self).tearDown()
        self.afterTearDown()
        
    def loadZCML(self, name='configure.zcml', **kw):
        """Load a ZCML file, configure.zcml by default."""
        self.layer.loadZCML(name=name, **kw)

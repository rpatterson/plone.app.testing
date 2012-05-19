.. -*-doctest-*-

=====================
plone.app.testing.api
=====================

This tests and documents in detail, the signatures common to both
layer and TestCase classes.  Detailed examples of calling the methods
are given in specific sections below.

Start with an instance of one of the classes.  This test is run
against both layers and test cases, so the instance is passed in as a
global, but it doesn't matter which it is for using the signatures.

    >>> help(instance)
    TODO

Useful set up and tear down method hooks are available and may be
overriden in subclasses.  All of the rest of the utility methods and
attributes should only be used inside these methods when overriden.

    >>> help(instance.afterSetUp)
    TODO
    >>> help(instance.beforeTearDown)
    TODO

A method for initializing add-ons, including their ZCML, are provided.
If using `addProfile`_ or `addProduct`_ for a given add-on, it is
often necessary to call the corresponding method here first to that is
it properly initialized before installing into the portal.

    >>> help(instance.installProduct)
    TODO

Another method for loading an arbitrary ZCML file is also provided.

    >>> help(instance.loadZCML)
    TODO

Methods for changing security and the logged in user are provided.

    >>> help(instance.setRoles)
    TODO
    >>> help(instance.setGroups)
    TODO
    >>> help(instance.login)
    TODO
    >>> help(instance.loginAsPortalOwner)
    TODO
    >>> help(instance.logout)
    TODO

The `app`, `portal` and `folder` attributes are also available.

    >>> instance.app
    <Application at >
    >>> instance.portal
    <PloneSite at /Plone>
    >>> instance.folder
    <ATFolder at /Plone/news>

Methods for installing add-ons into the portal are also still
available.

    >>> help(instance.addProfile)
    TODO
    >>> help(instance.addProduct)
    TODO

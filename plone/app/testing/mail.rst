.. -*-doctest-*-

Mock Mailhost
=============

When the plone.testing.api.PLONE_DEFAULT_TESTING layer is used, then
messages sent with the portal.MailHost.send method will be appended
to a list for checking in tests.

Start with an empty MailHost.

    >>> portal = self.portal
    >>> len(portal.MailHost)
    0

Send a message.

    >>> portal.MailHost.send("""\
    ... From: foo@foo.com
    ... To: bar@foo.com
    ... Subject: Foo message subject
    ... 
    ... Foo message body
    ... """)

The MailHost now contains one message.

    >>> len(portal.MailHost)
    1

The message an be removed using the pop method in which case it's
removed from the list.

    >>> print portal.MailHost.pop().as_string()
    From: foo@foo.com
    To: bar@foo.com
    Subject: Foo message subject
    Date: ...    
    Foo message body
    >>> len(portal.MailHost)
    0

The mock mail host can handle more complicated call signatures used in
the wild.

    >>> portal.MailHost.send(
    ...     """\
    ... From: foo@foo.com
    ... To: bar@foo.com
    ... Subject: Qux message subject
    ... 
    ... Qux message body
    ... """, 'bar@foo.com', 'foo@foo.com',
    ...     subject='Qux message subject')

    >>> print portal.MailHost.pop().as_string()
    To: bar@foo.com...
    Qux message body
    >>> len(portal.MailHost)
    0

from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import re
from plone import api
import os.path

from edeposit.user import MessageFactory as _
import itertools
from edeposit.user.producent import IProducent
from edeposit.content.epublicationfolder import IePublicationFolder
from edeposit.content.eperiodicalfolder import IePeriodicalFolder
from edeposit.content.bookfolder import IBookFolder

class IregisteringOfEContent(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IregisteringOfEContent)
    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"E-Deposit: Registering of any eContent")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('registeringofecontent.pt')

    @property
    def available(self):
        if api.user.is_anonymous():
            return False
        userGroups = api.group.get_groups(username=api.user.get_current().id)
        return 'Producent Editors' in [ gg.id for gg in userGroups ]

    def member(self):
        return api.user.get_current()

    def assignedProducents(self):
        user = api.user.get_current()
        username = user.getUserName()
        portal_catalog = api.portal.get_tool(name='portal_catalog')
        brains = portal_catalog({'object_provides': IProducent.__identifier__})

        def userIsAssigned(brain):
            user_local_roles = api.user.get_roles(obj=brain.getObject())
            return 'E-Deposit: Producent Administrator' in user_local_roles \
                or 'E-Deposit: Producent Editor' in user_local_roles \
                or 'E-Deposit: Producent Contributor' in user_local_roles

        producentInfos = [ {'path': brain.getPath(), 'UID': brain['UID'] , 'title': brain['Title'] } 
                           for brain in (brains or []) if userIsAssigned(brain)
                           ]
        
        #/edeposit/producenti/jeste-jeden-od-anonyma/epublications/++add++edeposit.content.epublication
        def getRegisteringPaths(producentPath):
            brains = portal_catalog({'object_provides': [IePublicationFolder.__identifier__,
                                                         IePeriodicalFolder.__identifier__,
                                                         #IBookFolder.__identifier__
                                                     ],
                                     'path': producentPath 
                                     })
            def getRegistrationPath(brain):
                path = brain.getPath()
                url = os.path.join(path,"add-at-once")
                return {'desc': brain['Title'], 'href': url}
            
            return map(getRegistrationPath, brains or [])

        def getOriginalFileContributingPath(producentPath):
            url = os.path.join(producentPath,
                               "originalfile-contributing",
                               "contribute"
            )
            return [{'desc': _("Contribute Original file"), 'href': url}]
            
        return [ {'name': producentInfo['title'],         
                  'path': producentInfo['path'],
                  'links': getRegisteringPaths(producentInfo['path']) +\
                  getOriginalFileContributingPath(producentInfo['path'])} for
                 producentInfo in (producentInfos or [])]
        
# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IregisteringOfEContent)

    def create(self, data):
        return Assignment(**data)


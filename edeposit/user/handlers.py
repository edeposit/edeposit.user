from zope.component import queryUtility
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent,\
    IContainerModifiedEvent
from zope.interface import Interface
from plone import api
from edeposit.user import MessageFactory as _

def added(context,event):
    """When an object is added, create folder for registration of ePublications
    """
    tool = api.portal.get_tool('translation_service')
    title = tool.translate(msgid=u"Registration of ePublications", 
                           domain='edeposit.user',
                           context=context, 
                           target_language='cs')
    context.invokeFactory('edeposit.content.epublicationfolder','epublications', title=title)

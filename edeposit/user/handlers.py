from zope.component import queryUtility
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent,\
    IContainerModifiedEvent
from zope.interface import Interface

from edeposit.user import MessageFactory as _

def added(context,event):
    """When an object is added, create folder for registration of ePublications
    """
    context.invokeFactory('edeposit.content.epublicationfolder','epublications', title=_(u"Registration of ePublications"))

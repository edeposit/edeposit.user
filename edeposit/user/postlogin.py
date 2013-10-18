# Python imports
import logging

# ZODB imports
from ZODB.POSException import ConflictError

# Zope imports
from AccessControl import getSecurityManager
from zope.interface import Interface
from zope.component import getUtility
from plone import api

# CMFCore imports
from Products.CMFCore import permissions
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent

# Caveman imports
from five import grok

# Plone imports
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
import os.path

# Logger output for this module
logger = logging.getLogger(__name__)

#: Site root relative path where we look for the folder with an edit access
CUSTOM_USER_FOLDERS = "dashboard"

def redirect_to_edit_access_folder(user):
    portal = api.portal.get()
    request = getattr(portal, "REQUEST", None)
    if not request:
        # HTTP request is not present e.g.
        # when doing unit testing / calling scripts from command line
        return False
    request.response.redirect(os.path.join(portal.absolute_url(),
                                           "dashboard"))
    return True

def logged_in_handler(event):
    """
    Listen to the event and perform the action accordingly.
    """
    user = event.object
    redirect_to_edit_access_folder(user)
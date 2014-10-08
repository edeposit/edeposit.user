# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from edeposit.user import MessageFactory as _

class IPrepareDescriptiveCataloguing(IPortletDataProvider):
    pass

class IPrepareSubjectCataloguing(IPortletDataProvider):
    pass

class AssignmentForDescriptiveCataloguing(base.Assignment):
    implements(IPrepareDescriptiveCataloguing)
    def __init__(self):
        pass
    @property
    def title(self):
        return _(u"Prepare Descriptive Cataloguing")

class AssignmentForSubjectCataloguing(base.Assignment):
    implements(IPrepareSubjectCataloguing)
    def __init__(self):
        pass
    @property
    def title(self):
        return _(u"Prepare Subject Cataloguing")

class RendererForDescriptiveCataloguing(base.Renderer):
    render = ViewPageTemplateFile('preparecataloguing.pt')

    def header(self):
        return _(u"Waiting for Descriptive Cataloguing Preparing")
        
    def collectionPath(self):
        return '/'.join(api.portal.get().getPhysicalPath() + ('producents','originalfiles-waiting-for-descriptive-cataloguing-preparing'))

    def worklistPath(self):
        return '/'.join(api.portal.get().getPhysicalPath() + ('producents','worklist-waiting-for-descriptive-cataloguing-preparing'))

class RendererForSubjectCataloguing(base.Renderer):
    render = ViewPageTemplateFile('preparecataloguing.pt')

    def header(self):
        return _(u"Waiting for Subject Cataloguing Preparing")
        
    def collectionPath(self):
        return '/'.join(api.portal.get().getPhysicalPath() + ('producents','originalfiles-waiting-for-subject-cataloguing-preparing'))

    def worklistPath(self):
        return '/'.join(api.portal.get().getPhysicalPath() + ('producents','worklist-waiting-for-subject-cataloguing-preparing'))
        

class AddFormForDescriptiveCataloguing(base.AddForm):
    form_fields = form.Fields(IPrepareDescriptiveCataloguing)

    def create(self, data):
        return AssignmentForDescriptiveCataloguing(**data)

class AddFormForSubjectCataloguing(base.AddForm):
    form_fields = form.Fields(IPrepareSubjectCataloguing)

    def create(self, data):
        return AssignmentForSubjectCataloguing(**data)


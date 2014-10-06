# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api

from edeposit.user import MessageFactory as _

class Renderer(base.Renderer):
    groupName = "Administrators"
    portalHeader = "Some Title"

    render = ViewPageTemplateFile('workplans.pt')

    def groupUsers(self):

        users = api.user.get_users(groupname=self.groupName)
        return users
        
    def collectionPath(self, user):
        print str(user)
        collName =  "/producents/originalfiles-waiting-for-user-" + user.id
        return '/'.join(api.portal.get().getPhysicalPath() + ('producents',collName))

    def userFullname(self,user):
        return user.getProperty("fullname")

    def header(self):
        return self.portalHeader

class IWorkPlans(IPortletDataProvider):
    pass

class Assignment(base.Assignment):
    implements(IWorkPlans)
    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Work Plans")

class AddForm(base.AddForm):
    form_fields = form.Fields(IWorkPlans)

    def create(self, data):
        return Assignment(**data)

class RendererForDescriptiveCataloguers(Renderer):
    groupName = "Descriptive Cataloguers"
    portalHeader = u"Práce pro Jmenný popis"



class IWorkPlansForDescriptiveReviewers(IPortletDataProvider):
    pass

class AssignmentForDescriptiveReviewers(base.Assignment):
    implements(IWorkPlansForDescriptiveReviewers)
    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Work Plans For Descriptive Reviewers")

class AddFormForDescriptiveReviewers(base.AddForm):
    form_fields = form.Fields(IWorkPlansForDescriptiveReviewers)

    def create(self, data):
        return AssignmentForDescriptiveReviewers(**data)

class RendererForDescriptiveReviewers(Renderer):
    groupName = "Descriptive Cataloguing Reviewers"
    portalHeader = u"Práce pro Jmennou revizi"

class RendererForSubjectCataloguers(Renderer):
    groupName = "Subject Cataloguers"
    portalHeader = u"Práce pro Věcný popis"

class RendererForSubjectReviewers(Renderer):
    groupName = "Subject Cataloguing Reviewers"
    portalHeader = u"Práce pro Věcnou revizi"

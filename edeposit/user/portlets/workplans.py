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
    groupEmailTransition = "sendEmailToGroupSubjectCataloguers"
    render = ViewPageTemplateFile('workplans.pt')

    def groupUsers(self):
        users = api.user.get_users(groupname=self.groupName)
        return users
        
    def urlOfGroupEmail(self):
        return '/'.join(api.portal.get().getPhysicalPath() + ('producents','content_status_comment')) \
            + "?workflow_action=%s" % (self.groupEmailTransition,)

    def collectionPath(self, user):
        collName =  "/producents/originalfiles-waiting-for-user-" + user.id
        return '/'.join(api.portal.get().getPhysicalPath() + ('producents',collName))

    def userFullname(self,user):
        return user.getProperty("fullname")

    def header(self):
        return self.portalHeader

class RendererForDescriptiveCataloguers(Renderer):
    groupName = "Descriptive Cataloguers"
    portalHeader = u"Práce pro jmenný popis"
    groupEmailTransition = "sendEmailToGroupDescriptiveCataloguers"

class RendererForDescriptiveReviewers(Renderer):
    groupName = "Descriptive Cataloguing Reviewers"
    portalHeader = u"Práce pro revizi jmenného popisu"
    groupEmailTransition = "sendEmailToGroupDescriptiveCataloguingReviewers"

class RendererForSubjectCataloguers(Renderer):
    groupName = "Subject Cataloguers"
    portalHeader = u"Práce pro věcný popis"
    groupEmailTransition = "sendEmailToGroupSubjectCataloguers"

class RendererForSubjectReviewers(Renderer):
    groupName = "Subject Cataloguing Reviewers"
    portalHeader = u"Práce pro revizi věcného popisu"
    groupEmailTransition = "sendEmailToGroupSubjectCataloguingReviewers"


class IWorkPlansForDescriptiveCataloguers(IPortletDataProvider):
    pass

class IWorkPlansForDescriptiveReviewers(IPortletDataProvider):
    pass

class IWorkPlansForSubjectCataloguers(IPortletDataProvider):
    pass

class IWorkPlansForSubjectReviewers(IPortletDataProvider):
    pass

class Assignment(base.Assignment):
    implements(IWorkPlansForDescriptiveCataloguers)
    def __init__(self):
        pass
    @property
    def title(self):
        return _(u"Some Assignment")

class AssignmentForDescriptiveCataloguers(base.Assignment):
    implements(IWorkPlansForDescriptiveCataloguers)
    def __init__(self):
        pass
    @property
    def title(self):
        return _(u"Work Plans for Descriptive Cataloguers")

class AssignmentForDescriptiveReviewers(base.Assignment):
    implements(IWorkPlansForDescriptiveReviewers)
    def __init__(self):
        pass
    @property
    def title(self):
        return _(u"Work Plans for Descriptive Reviewers")

class AssignmentForSubjectCataloguers(base.Assignment):
    implements(IWorkPlansForSubjectCataloguers)
    def __init__(self):
        pass
    @property
    def title(self):
        return _(u"Work Plans for Subject Cataloguers")

class AssignmentForSubjectReviewers(base.Assignment):
    implements(IWorkPlansForSubjectReviewers)
    def __init__(self):
        pass
    @property
    def title(self):
        return _(u"Work Plans for Subject Reviewers")

class AddFormForDescriptiveCataloguers(base.AddForm):
    form_fields = form.Fields(IWorkPlansForDescriptiveCataloguers)
    def create(self, data):
        return AssignmentForDescriptiveCataloguers(**data)

class AddFormForDescriptiveReviewers(base.AddForm):
    form_fields = form.Fields(IWorkPlansForDescriptiveReviewers)
    def create(self, data):
        return AssignmentForDescriptiveReviewers(**data)

class AddFormForSubjectCataloguers(base.AddForm):
    form_fields = form.Fields(IWorkPlansForSubjectCataloguers)
    def create(self, data):
        return AssignmentForSubjectCataloguers(**data)

class AddFormForSubjectReviewers(base.AddForm):
    form_fields = form.Fields(IWorkPlansForSubjectReviewers)
    def create(self, data):
        return AssignmentForSubjectReviewers(**data)



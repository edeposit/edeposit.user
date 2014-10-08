# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface import implements
from itertools import chain
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone import api
from zope import schema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from edeposit.user import MessageFactory as _

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from plone.z3cform.layout import FormWrapper

from z3c.form.interfaces import WidgetActionExecutionError, ActionExecutionError, IObjectFactory
from zope.lifecycleevent import modified
from five import grok
from plone.directives import form
from zope.formlib import form as formlib
from z3c.form import group, field, button

def possibleWorkersFactory(groupName):
    @grok.provider(IContextSourceBinder)
    def possibleWorkers(context):
        acl_users = getToolByName(context, 'acl_users')
        group = acl_users.getGroupById(groupName)
        terms = []
        
        if group is not None:
            for member_id in group.getMemberIds():
                user = acl_users.getUserById(member_id)
                if user is not None:
                    member_name = user.getProperty('fullname') or member_id
                    terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))
                    
        return SimpleVocabulary(terms)
    return possibleWorkers

possibleDescriptiveCataloguers = possibleWorkersFactory('Descriptive Cataloguers')
possibleDescriptiveReviewers = possibleWorkersFactory('Descriptive Cataloguing Reviewers')
possibleSubjectCataloguers = possibleWorkersFactory('Subject Cataloguers')
possibleSubjectReviewers = possibleWorkersFactory('Subject Cataloguing Reviewers')

class IAssignedDescriptiveCataloguer(form.Schema):
    cataloguer = schema.Choice(
        title=_(u"Cataloguer"),
        source=possibleDescriptiveCataloguers,
        required=False,
    )

class IAssignedSubjectCataloguer(form.Schema):
    cataloguer = schema.Choice(
        title=_(u"Cataloguer"),
        source=possibleSubjectCataloguers,
        required=False,
    )

class IAssignedDescriptiveReviewer(form.Schema):
    reviewer = schema.Choice(
        title=_(u"Reviewer"),
        source=possibleDescriptiveReviewers,
        required=False,
    )

class IAssignedSubjectReviewer(form.Schema):
    reviewer = schema.Choice(
        title=_(u"Reviewer"),
        source=possibleSubjectReviewers,
        required=False,
    )
    
class AssignedDescriptiveCataloguerForm(form.SchemaForm):
    schema = IAssignedDescriptiveCataloguer
    ignoreContext = True
    label = u""
    description = u""
    submitAction = 'submitDescriptiveCataloguingPreparing'
    fieldName = 'cataloguer'

    @button.buttonAndHandler(u'Přiřadit')
    def handleOK(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        if data.get(self.fieldName,None):
            api.user.grant_roles(username=data[self.fieldName],
                                 obj=self.context,
                                 roles=('E-Deposit: Descriptive Cataloguer',))
            modified(self.context)
            wft = api.portal.get_tool('portal_workflow')
            wft.doActionFor(self.context, self.submitAction)
        self.status = u"Hotovo!"


class AssignedDescriptiveReviewerForm(AssignedDescriptiveCataloguerForm):
    schema = IAssignedDescriptiveReviewer
    submitAction = 'submitDescriptiveCataloguingReviewPreparing'
    fieldName = 'reviewer'

class AssignedSubjectCataloguerForm(AssignedDescriptiveCataloguerForm):
    schema = IAssignedSubjectCataloguer
    submitAction = 'submitSubjectCataloguingreparing'
    fieldName = 'cataloguer'

class AssignedSubjectReviewerForm(AssignedDescriptiveCataloguerForm):
    schema = IAssignedSubjectReviewer
    submitAction = 'submitSubjectCataloguingReviewPreparing'
    fieldName = 'reviewer'


class PortletFormView(FormWrapper):
     """ Form view which renders z3c.forms embedded in a portlet.
     Subclass FormWrapper so that we can use custom frame template. """
     index = ViewPageTemplateFile("formwrapper.pt")

class IWaitingForWorkAssignment(IPortletDataProvider):
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

    implements(IWaitingForWorkAssignment)

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Waiting for work assignment")

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('waitingforworkassignment.pt')
    
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.form_wrapper = self.createForm()

    def createForm(self):
        """ Create a form instance.

        @return: z3c.form wrapped for Plone 3 view
        """
        context = self.context.aq_inner
        form = AssignedCataloguerForm(context, self.request)

        # Wrap a form in Plone view
        view = PortletFormView(context, self.request)
        view = view.__of__(context) # Make sure acquisition chain is respected
        view.form_instance = form
        return view
    
    @property
    def available(self):
        return 'descriptiveCataloguingPreparing' in api.content.get_state(self.context)


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = formlib.Fields(IWaitingForWorkAssignment)

    def create(self, data):
        return Assignment(**data)


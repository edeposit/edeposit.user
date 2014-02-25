# -*- coding: utf-8 -*-
from zope import schema
import zope
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
import plone.app.users.browser.register
from zope.publisher.browser import BrowserView
from z3c.form.browser.radio import RadioFieldWidget
from plone.directives import form
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
from z3c.form import field, button
from plone import api
from zope.interface import Invalid, Interface
from edeposit.user import MessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import adapts
from zope.component import getUtility
from zope.component import queryUtility
from plone.z3cform.fieldsets import extensible
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from edeposit.user.producent import IProducent
from edeposit.user.producentuser import IProducentUser
from edeposit.user.producentfolder import IProducentFolder
from edeposit.user.producentadministrator import IProducentAdministrator, ProducentAdministrator
from z3c.form.interfaces import WidgetActionExecutionError, ActionExecutionError, IObjectFactory
import os.path
import logging
from plone.dexterity.utils import createContentInContainer, addContentToContainer, createContent
from plone.i18n.normalizer.interfaces import IURLNormalizer, IIDNormalizer
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.supermodel import model
from plone.dexterity.utils import getAdditionalSchemata
from Acquisition import aq_inner, aq_base
from Products.CMFDefault.exceptions import EmailAddressInvalid

# Logger output for this module
logger = logging.getLogger(__name__)

def checkEmailAddress(value):
    reg_tool = api.portal.get_tool(name='portal_registration')
    if value and reg_tool.isValidEmail(value):
        pass
    else:
        raise EmailAddressInvalid
    return True


class IProducentAdministrators(model.Schema):
    administrators = zope.schema.List(
        title = _(u'Producent Administrators'),
        description = u'Přidejte alespoň jednoho administrátora',
        required = True,
        value_type = zope.schema.Object( title=_('Producent Administrator'), schema=IProducentAdministrator ),
        unique = False
    )

class ProducentAddForm(DefaultAddForm):
    label = _(u"Registration of a producent")
    description = _(u"Please fill informations about user and producent.")

    @property
    def additionalSchemata(self):
        schemata = [s for s in getAdditionalSchemata(portal_type=self.portal_type)] + \
                   [IProducentAdministrators,]
        return schemata

    def update(self):
        DefaultAddForm.update(self)
        self.widgets['IBasic.title'].label=u"Producent"
        #import sys,pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()

        # bb=filter(lambda ii: 'continueregistration' in ii[0], self.buttons.items())
        # bb and bb[0][1].title = _"Pokračovat v registraci"
        pass

    def add(self,object):
        DefaultAddForm.add(self,object)
        administratorsFolder = aq_inner(object['producent-administrators'])
        #import sys,pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()

        for administrator in self.administrators:
            addContentToContainer(administratorsFolder, administrator, False)
        return addedObject

    def create(self, data):
        self.administrators = data['IProducentAdministrators.administrators']
        del data['IProducentAdministrators.administrators']
        createdProducent = DefaultAddForm.create(self,data)
        return createdProducent

    def getProducentsFolder(self):
        return self.context
   
    def checkPasswords(self, data, errors):
        #import sys,pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        return (data, errors)

    # def checkPasswords(self, data):
    #     # raise Invalid(
    #     #     PC_("You cannot have a type as a secondary type without "
    #     #         "having it allowed. You have selected ${types}s.",
    #     #         mapping=dict(types=", ".join(missing))))
    #     # error_keys = [error.field_name for error in errors
    #     #               if hasattr(error, 'field_name')]
    #     # if not ('password' in error_keys or 'password_ctl' in error_keys):
    #     #     password = self.widgets['password'].getInputValue()
    #     #     password_ctl = self.widgets['password_ctl'].getInputValue()
    #     #     if password != password_ctl:
    #     #         err_str = _(u'Passwords do not match.')
    #     #         errors.append(WidgetInputError('password',
    #     #                                        u'label_password', err_str))
    #     #         errors.append(WidgetInputError('password_ctl',
    #     #                                        u'label_password', err_str))
    #     #         self.widgets['password'].error = err_str
    #     #         self.widgets['password_ctl'].error = err_str
    #     #         pass
    #     #         # Password field checked against RegistrationTool
    #     #         # Skip this check if password fields already have an error
    #     #         if not 'password' in error_keys:
    #     #             password = self.widgets['password'].getInputValue()
    #     #             if password:
    #     #                 # Use PAS to test validity
    #     #                 err_str = registration.testPasswordValidity(password)
    #     #                 if err_str:
    #     #                     errors.append(WidgetInputError('password',
    #     #                                                    u'label_password', err_str))
    #     #                     self.widgets['password'].error = err_str

    @button.buttonAndHandler(_("ContinueRegistration"))
    def handleContinueRegistration(self, action):
        pass

    @button.buttonAndHandler(_(u"Register"))
    def handleRegister(self, action):
        data, errors = self.checkPasswords(*self.extractData())
        if errors:
            self.status = self.formErrorsMessage
            return

        producentsFolder = self.getProducentsFolder()
        # hack for title and description
        data['title'] = data.get('IBasic.title','')
        data['description'] = data.get('IBasic.description','')
        producent = createContentInContainer(producentsFolder, "edeposit.user.producent", **data)
        administratorsFolder = producent['producent-administrators']
        for administrator in data['IProducentAdministrators.administrators']:
            administrator.title=getattr(administrator,'fullname',None)
            addContentToContainer(administratorsFolder, administrator, False)
        if producent is not None:
            wft = api.portal.get_tool('portal_workflow')
            wft.doActionFor(producent,'submit')
            # mark only as finished if we get the new object
            self._finishedAdd = True
            IStatusMessage(self.request).addStatusMessage(_(u"Item created"), "info")
            url = "%s/%s" % (api.portal.getSite().absolute_url(), 'register-with-producent-successed')
            self.request.response.redirect(url)
    pass

class ProducentAddView(DefaultAddView):
    form = ProducentAddForm

class PostLoginView(BrowserView):
    def update(self):
        portal = api.portal.get()
        dashboard_url = os.path.join(portal.absolute_url(),'producents')
        return self.request.redirect(dashboard_url)

class RegisteredView(BrowserView):
    pass

class ProducentAdministratorFactory(object):
    adapts(Interface, Interface, Interface, Interface)
    zope.interface.implements(IObjectFactory)
    
    def __init__(self, context, request, form, widget):
        self.context = context
        self.request = request
        self.form = form
        self.widget = widget

    def __call__(self, value):
        created=createContent('edeposit.user.producentadministrator',**value)
        return created

class IProducentWithAdministrators(IProducent):
    administrators = zope.schema.List(
        title = _(u'Producent Administrators'),
        description = _(u'Fill in at least one producent administrator'),
        required = True,
        value_type = zope.schema.Object( title=_('Producent Administrator'), schema=IProducentAdministrator ),
        unique = False
    )

def normalizeTitle(title):
    title = u"Cosi českého a. neobratného"
    util = queryUtility(IIDNormalizer)
    result = util.normalize(title)
    result
    return result


class RegistrationForm(ProducentAddForm):
    portal_type = 'edeposit.user.producent'
    template = ViewPageTemplateFile('form.pt')

    def getProducentsFolder(self):
        portal = api.portal.get()
        return portal['producents']

# class RegistrationForm(form.SchemaForm):
#     schema = IProducentWithAdministrators

#     label = _(u"Registration of a producent")
#     description = _(u"Please fill informations about user and producent.")

#     ignoreContext = True
#     enableCSRFProtection = True

#     template = ViewPageTemplateFile('form.pt')
#     prefix = 'producent'

#     def update(self):
#         self.request.set('disable_border', True)
#         super(RegistrationForm, self).update()

#     @button.buttonAndHandler(_(u"Register"))
#     def handleRegister(self, action):
#         data, errors = self.extractData()
#         if errors:
#             self.status = self.formErrorsMessage
#             return
        
#         producentsFolder = api.portal.getSite()['producents']
#         producent = createContentInContainer(producentsFolder, 
#                                              "edeposit.user.producent", 
#                                              **data)
        
#         for administrator in data['administrators']:
#             addContentToContainer(producent['producent-administrators'], 
#                                   administrator,
#                                   False)
#     pass


# class RegistrationForm01(form.SchemaForm):
#     label = _(u"Registration")
#     description = _(u"Please fill informations about user and producent.")

#     ignoreContext = True
#     enableCSRFProtection = True

#     schema = IEnhancedUserDataSchema
#     template = ViewPageTemplateFile('form.pt')

#     def update(self):
#         self.request.set('disable_border', True)
#         super(RegistrationForm, self).update()

#     @button.buttonAndHandler(u"Register")
#     def handleRegister(self, action):
#         data, errors = self.extractData()
#         if errors:
#             self.status = self.formErrorsMessage
#             return

#         properties = dict([ (key,data[key]) for key in schema.getFieldNames(IEnhancedUserDataSchema) 
#                             if key not in ['password','username','password_ctl']])

#         if api.user.get(username=data['username']):
#             raise ActionExecutionError(Invalid(_('Username is already used. Fill in another username.')))

#         user = api.user.create(username=data['username'],
#                                password=data['password'],
#                                properties = properties,
#                                )
#         producent_properties = dict([ (key,data['producent.'+key]) for key in schema.getFieldNames(IProducent) ])
#         if data.get('producent.new_producent',None):
#             portal_catalog = api.portal.get_tool('portal_catalog')
#             brains = portal_catalog({'object_provides': IProducentFolder.__identifier__})
#             if brains:
#                 plone.api.group.add_user(groupname="Producents", user=user)
#                 producentFolder = brains[0].getObject()
#                 with api.env.adopt_user(user=user):
#                     producent = api.content.create(container=producentFolder,type='edeposit.user.producent', title=data['producent.title'],**producent_properties)
#                     plone.api.user.grant_roles(user=user,obj=producent, roles=['E-Deposit: Assigned Producent',])
#                     plone.api.content.transition(obj=producent, transition="submit")
#                 pass
#             pass
#         else:
#             if data['producent']:
#                 plone.api.group.add_user(groupname="Producents", user=user)
#                 producent = plone.api.content.get(UID=data['producent'])
#                 plone.api.user.grant_roles(user=user,obj=producent,roles=['E-Deposit: Assigned Producent',])
#                 producent.reindexObject()
#             pass
#         self.status="Registered!"
#         self.request.response.redirect(os.path.join(api.portal.get().absolute_url(),"@@register-with-producent-successed"))


# @form.validator(field=IEnhancedUserDataSchema['username'])
# def isUnique(value):
#     print "user is already used validation"
#     if api.user.get(username=value):
#         raise Invalid("Your username is already used. Fill in another username.")
#     return True


# class INewProducent(Interface):
#     new_producent = schema.Bool(
#         title=_(u'label_new_producent', default=u'New producent'),
#         description=_(u'help_new_producent',
#                       default=u"Do you wan to create new producent?"),
#         required=False,
#         )

# class IProducentTitle(Interface):
#     title = schema.ASCIILine(
#         title=_(u'label_producent_title', default=u'Producent title'),
#         description=_(u'help_title_producent',
#                       default=_(u"Fill in title of new producent.")),
#         required=False,
#         )

# class RegistrationFormExtender(extensible.FormExtender):
#     adapts(Interface, IDefaultBrowserLayer, RegistrationForm) # context, request, form

#     def __init__(self, context, request, form):
#         self.context = context
#         self.request = request
#         self.form = form
        
#     def update(self):
#         self.add(field.Fields(INewProducent,prefix="producent"), group="producent")
#         self.move('producent.new_producent', before='producent')
#         self.add(field.Fields(IProducent,prefix="producent"), group="producent")
#         self.add(field.Fields(IProducentTitle,prefix="producent"), group="producent")
#         self.move('producent.title', before='producent.home_page')
#         producentFields = [gg for gg in self.form.groups if 'producent' in gg.__name__][0].fields           
#         if 'form.widgets.producent.new_producent' in self.request.form \
#                 and 'selected' in self.request.form['form.widgets.producent.new_producent']:
#             pass
#         else:
#             for ff in producentFields.values():
#                 field_copy = copy.copy(ff.field)
#                 field_copy.required = False
#                 ff.field = field_copy


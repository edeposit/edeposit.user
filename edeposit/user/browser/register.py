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
from z3c.form import field, button, validator
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
from edeposit.user.producenteditor import IProducentEditor, ProducentEditor
from edeposit.user.producentfolder import IProducentFolder
from edeposit.user.producentadministrator import IProducentAdministrator, ProducentAdministrator
from z3c.form.interfaces import WidgetActionExecutionError, ActionExecutionError, IObjectFactory, IValidator, IErrorViewSnippet
import os.path
import logging
import string
from plone.dexterity.utils import createContentInContainer, addContentToContainer, createContent
from plone.i18n.normalizer.interfaces import IURLNormalizer, IIDNormalizer
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.supermodel import model
from plone.dexterity.utils import getAdditionalSchemata
from Acquisition import aq_inner, aq_base
from Products.CMFDefault.exceptions import EmailAddressInvalid
from zope.interface import invariant, Invalid
from itertools import chain

# Logger output for this module
logger = logging.getLogger(__name__)

class IProducentAdministrators(model.Schema):
    administrators = zope.schema.List(
        title = _(u'Producent Administrators'),
        description = u'Přidejte alespoň jednoho administrátora',
        required = True,
        value_type = zope.schema.Object( title=_('Producent Administrator'), schema=IProducentAdministrator ),
        unique = False,
        min_length = 1,
    )

class IAdministrator(model.Schema):
    administrator = zope.schema.Object(
        title = _(u'Producent Administrator'),
        description = u"správce přidává editory, upravuje informace o producentovi.",
        required = True,
        schema=IProducentAdministrator,
    )

def checkEmailAddress(value):
    reg_tool = api.portal.get_tool(name='portal_registration')
    if value and reg_tool.isValidEmail(value):
        pass
    else:
        raise EmailAddressInvalid
    return True

# Interface class; used to define content-type schema.
class IEditor(model.Schema):
    """ a few fields from IProducentAdministrator """
    model.fieldset('editor',
                   label = _(u'Producent Editor'),
                   fields = ['fullname',
                             'email',
                             'phone',
                             'username',
                             'password',
                             'password_ctl',
                         ]
    )

    fullname = schema.TextLine(
        title=u"Příjmení a jméno",
        description=_(u'help_full_name_creation',
                      default=u"Enter full name, e.g. John Smith."),
        required=False)

    email = schema.ASCIILine(
        title=_(u'label_email', default=u'E-mail'),
        description=u'',
        required=False,
    )

    phone = schema.TextLine(
        title=_(u'label_phone', default=u'Telephone number'),
        description=_(u'help_phone',
                      default=u"Leave your phone number so we can reach you."),
        required=False,
    )
    
    username = schema.ASCIILine(
        title=_(u'label_user_name', default=u'User Name'),
        description=_(u'help_user_name_creation_casesensitive',
                      default=u"Enter a user name, usually something "
                      "like 'jsmith'. "
                      "No spaces or special characters. "
                      "Usernames and passwords are case sensitive, "
                      "make sure the caps lock key is not enabled. "
                      "This is the name used to log in."),
        required=False,
    )
    
    password = schema.Password(
        title=_(u'label_password', default=u'Password'),
        description=_(u'help_password_creation',
                      default=u'Enter your new password.'),
        required=False,
    )
    
    password_ctl = schema.Password(
        title=_(u'label_confirm_password',
                default=u'Confirm password'),
        description=_(u'help_confirm_password',
                      default=u"Re-enter the password. "
                      "Make sure the passwords are identical."),
        required=False,
    )

    # @invariant
    # def checkPasswords(data):
    #     password, password_ctl = getattr(data,'password',None),getattr(data,'password_ctl',None)
    #     if password and password_ctl:
    #         if password != password_ctl:
    #             raise Invalid("hesla se musí shodovat")
    #     pass
        
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



class ProducentAddForm(DefaultAddForm):
    label = _(u"Registration of a producent")
    description = _(u"Please fill informations about user and producent.")
    default_fieldset_label = u"Producent"

    @property
    def additionalSchemata(self):
        schemata =       [IAdministrator,] +\
                         [IEditor,] +\
                         [s for s in getAdditionalSchemata(portal_type=self.portal_type)]
        return schemata

    def updateWidgets(self):
        super(ProducentAddForm, self).updateWidgets()
        self.widgets['IBasic.title'].label=u"Název producenta"

    def getProducentsFolder(self):
        return self.context

    def extractData(self):
        data, errors = super(ProducentAddForm,self).extractData()
        # def getErrors(adata, awidget):
        #     password, password_ctl = adata.password, adata.password_ctl
        #     errors = []
        #     print "get errors"
        #     if password != password_ctl:
        #         print "password does not pass"
        #         print awidget.name
        #         widget_password = awidget.subform.widgets['password']
        #         widget_password_ctl = awidget.subform.widgets['password_ctl']
        #         error = zope.interface.Invalid('hesla se musi shodovat')
        #         errors = (getErrorView(widget_password, Invalid('hesla se musi shodovat')),
        #                           getErrorView(widget_password_ctl, Invalid(u'hesla se musí shodovat')))

        #     if api.user.get(username=adata.username):
        #         widget_username = awidget.subform.widgets['username']
        #         errors += (getErrorView(widget_username, 
        #                                 Invalid(u"toto uživatelské jméno je už obsazeno, zvolte jiné")),)
        #     return errors
            
        # names = filter(lambda key: data.get(key,None), ['IAdministrator.administrator',
        #                                            'IProducentEditors.editor1',
        #                                            'IProducentEditors.editor2',
        #                                            'IProducentEditors.editor3',
        #                                        ])
        # def chainErrorViews(listOfList):
        #     for errorViews in listOfList:
        #         for errorView in errorViews:
        #             yield errorView

        # def getWidget(name):
        #     widget = self.widgets.get(name,None) \
        #              or filter(lambda widget: widget, map(lambda group: group.widgets.get(name,None), self.groups))[0]
        #     return widget

        # newErrorViews = filter(lambda errView: errView, 
        #                        chainErrorViews(map(lambda key: getErrors(data[key], getWidget(key)), names)))
        return data, errors


    @button.buttonAndHandler(_(u"Register"))
    def handleRegister(self, action):
        print "handle registrer"
        data, errors = self.extractData()
        if errors:
            print "all errors views names", map(lambda err: err.widget.name, errors)
            print self.formErrorsMessage
            print "self.widgets.errors", self.widgets.errors
            self.status = self.formErrorsMessage
            return

        editorFields = ['fullname','email','phone','username','password','password_ctl']
        editorValues = map(lambda key: data.get('IEditor.'+key,None), editorFields)

        producentsFolder = self.getProducentsFolder()
        # hack for title and description
        data['title'] = data.get('IBasic.title','')
        data['description'] = data.get('IBasic.description','')

        producent = createContentInContainer(producentsFolder, "edeposit.user.producent", **data)

        if filter(lambda value: value, editorValues):
            print "chceme vytvorit editora"
            if False in map(lambda value: bool(value), editorValues):
                raise ActionExecutionError(Invalid(u"Některé položky u editora nejsou vyplněny. Buď vyplňte editorovi všechny položky, nebo je všechny smažte."))
                
            editorData = dict(zip(editorFields, editorValues))
            if editorData['password'] != editorData['password_ctl']:
                raise ActionExecutionError(Invalid(u"U editora se neshodují zadaná hesla. Vyplňte hesla znovu."))
            if api.user.get(username=editorData['username']):
                raise ActionExecutionError(Invalid(u"Uživatelské jméno u editora je již obsazené. Zadejte editorovi jiné uživatelské jméno."))

            editorsFolder = producent['producent-editors']
            editorData['title'] = editorData['fullname']
            editor = createContentInContainer(editorsFolder, "edeposit.user.producenteditor", **editorData)


        administratorsFolder = producent['producent-administrators']
        administrator = data['IAdministrator.administrator']
        administrator.title = getattr(administrator,'fullname',None)
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
    zope.interface.implements(IObjectFactory)
    adapts(Interface, Interface, Interface, Interface)
    
    def __init__(self, context, request, form, widget):
        self.context = context
        self.request = request
        self.form = form
        self.widget = widget

    def __call__(self, value):
        created=createContent('edeposit.user.producentadministrator',**value)
        return created

class ProducentEditorFactory(object):
    zope.interface.implements(IObjectFactory)
    adapts(Interface, Interface, Interface, Interface)
    
    def __init__(self, context, request, form, widget):
        self.context = context
        self.request = request
        self.form = form
        self.widget = widget

    def __call__(self, value):
        print "producent editor factory", value
        created=createContent('edeposit.user.producenteditor',**value)
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


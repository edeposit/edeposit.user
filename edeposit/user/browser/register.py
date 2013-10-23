from zope import schema
import copy

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
import plone.app.users.browser.register
from zope.publisher.browser import BrowserView
from z3c.form.browser.radio import RadioFieldWidget
from plone.directives import form, dexterity

#from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
from z3c.form import field, button
from plone import api
from zope.interface import Invalid, Interface
from edeposit.user import MessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import adapts
from plone.z3cform.fieldsets import extensible
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from edeposit.user.userdataschema import IEnhancedUserDataSchema, EnhancedUserData
from edeposit.user.producent import IProducent
from edeposit.user.producentfolder import IProducentFolder

from z3c.form.interfaces import WidgetActionExecutionError, ActionExecutionError

class RegisteredView(BrowserView):
    pass
    #template = ViewPageTemplateFile('registered.pt')

class RegistrationForm(form.SchemaForm):
    label = _(u"Registration")
    description = _(u"Please fill informations about user and producent.")

    ignoreContext = True
    enableCSRFProtection = True

    schema = IEnhancedUserDataSchema
    template = ViewPageTemplateFile('form.pt')

    def update(self):
        self.request.set('disable_border', True)
        super(RegistrationForm, self).update()

    @button.buttonAndHandler(u"Register")
    def handleRegister(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        properties = dict([ (key,data[key]) for key in schema.getFieldNames(IEnhancedUserDataSchema) if key not in ['password','username','password_ctl']])

        if api.user.get(username=data['username']):
            raise ActionExecutionError(Invalid(_('Username is already used. Fill in another username.')))

        user = api.user.create(username=data['username'],
                               password=data['password'],
                               properties = properties)
        roles_for_user = []
        api.user.grant_roles(user=user,
                             roles=roles_for_user)
        producent_properties = dict([ (key,data['producent.'+key]) for key in schema.getFieldNames(IProducent) ])
        if data.get('producent.new_producent',None):
            portal_catalog = api.portal.get_tool('portal_catalog')
            brains = portal_catalog({'object_provides': IProducentFolder.__identifier__})
            if brains:
                producentFolder = brains[0].getObject()
                producent = api.content.create(container=producentFolder, 
                                               type='edeposit.user.producent',
                                               title=data['producent.title'],
                                               **producent_properties)
                plone.api.user.grant_roles(user=user,obj=producent,roles=['E-Deposit: Assigned Producent',])
                pass
            pass
        else:
            producent = plone.api.content.get(UID=data['producent'])
            plone.api.user.grant_roles(user=user,obj=producent,roles=['E-Deposit: Assigned Producent',])
            pass
        self.status="Registered!"

@form.validator(field=IEnhancedUserDataSchema['username'])
def isUnique(value):
    print "user is already used validation"
    if api.user.get(username=value):
        raise Invalid("Your username is already used. Fill in another username.")
    return True

class INewProducent(Interface):
    new_producent = schema.Bool(
        title=_(u'label_new_producent', default=u'New producent'),
        description=_(u'help_new_producent',
                      default=u"Do you wan to create new producent?"),
        required=False,
        )

class IProducentTitle(Interface):
    title = schema.ASCIILine(
        title=_(u'label_producent_title', default=u'Producent title'),
        description=_(u'help_title_producent',
                      default=_(u"Fill in title of new producent.")),
        required=False,
        )

class RegistrationFormExtender(extensible.FormExtender):
    adapts(Interface, IDefaultBrowserLayer, RegistrationForm) # context, request, form

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form
        
    def update(self):
        self.add(field.Fields(INewProducent,prefix="producent"), group="producent")
        self.move('producent.new_producent', before='producent')
        self.add(field.Fields(IProducent,prefix="producent"), group="producent")
        self.add(field.Fields(IProducentTitle,prefix="producent"), group="producent")
        self.move('producent.title', before='producent.home_page')
        producentFields = [gg for gg in self.form.groups if 'producent' in gg.__name__][0].fields           
        if 'form.widgets.producent.new_producent' in self.request.form \
                and 'selected' in self.request.form['form.widgets.producent.new_producent']:
            pass
        else:
            for ff in producentFields.values():
                field_copy = copy.copy(ff.field)
                field_copy.required = False
                ff.field = field_copy

# continue for RegistrationForm

    # def add(self,object):
    #     print "add"
    #     properties = dict([ (key,getattr(object,key)) for key in ['fullname','location','email','city','home_page','phone','street','country']])
    #     if not object.new_producent and object.producent:
    #         properties['producent'] = object.producent
    #         pass
    #     producent_properties = dict([ (key.replace('producent_',''), getattr(object,key)) \
    #                                       for key in ['producent_title',
    #                                                   'producent_home_page',
    #                                                   'producent_location',
    #                                                   'producent_street',
    #                                                   'producent_city',
    #                                                   'producent_country',
    #                                                   'producent_contact',
    #                                                   'producent_agreement',
    #                                                   ]
    #                                   ])
    #     if object.new_producent:
    #         pass

    #     user = api.user.create(username=object.username,
    #                            password=object.password,
    #                            properties = properties)
    #     import pdb; pdb.set_trace()
    #     roles = ['E-Deposit: Producent with Agreement',
    #              'E-Deposit: Producent without Agreement'
    #              ]
    #     api.user.grant_roles(username=object.username,
    #                          roles = roles)
    #     pass



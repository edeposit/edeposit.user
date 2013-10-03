from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
import plone.app.users.browser.register
from Products.Five import BrowserView
from z3c.form.browser.radio import RadioFieldWidget
from plone.directives import form, dexterity
from edeposit.user.userdataschema import IEnhancedUserDataSchema, EnhancedUserData
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
from edeposit.user.producent import IProducent
from zope import schema
import copy

class RegisteredView(BrowserView):
    template = ViewPageTemplateFile('registered.pt')

@form.validator(field=IEnhancedUserDataSchema['username'])
def isUnique(value):
    if api.user.get(username=value):
        raise Invalid("Your username is already used. Fill in another username.")
    return True

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
            self.status = self.formErorrsMessage
            return

        self.context['Members'].invokeFactory('EnhancedUserData', **data)

        IStatusMessage(self.request).addStatusMessage(
            "Registered! Soon you will receive email.",
            'info')
        self.request.response.redirect(self.context.absolute_url())

class INewProducent(Interface):
    new_producent = schema.Bool(
        title=_(u'label_new_producent', default=u'New producent'),
        description=_(u'help_new_producent',
                      default=u"Do you wan to create new producent?"),
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



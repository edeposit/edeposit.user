from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.z3cform.templates import ZopeTwoFormTemplateFactory
import plone.app.users.browser.register
from Products.Five import BrowserView
from z3c.form.browser.radio import RadioFieldWidget
from plone.directives import form
from plone.autoform.form import AutoExtensibleForm
from edeposit.user.userdataschema import IEnhancedUserDataSchema, EnhancedUserData
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
#from z3c.form import form, field, button
from plone import api
from zope.interface import Invalid
from edeposit.user import MessageFactory as _

class RegisteredView(BrowserView):
    template = ViewPageTemplateFile('registered.pt')

@form.validator(field=IEnhancedUserDataSchema['username'])
def isUnique(value):
    if api.user.get(username=value):
        raise Invalid("Your username is already used. Fill in another username.")
    return True

class RegistrationForm(AutoExtensibleForm, form.AddForm):
    label = _(u"Registration")
    description = _(u"Please fill informations about user and producent.")

    ignoreContext = True
    enableCSRFProtection = True

    schema = IEnhancedUserDataSchema
    template = ViewPageTemplateFile('form.pt')

    def update(self):
        self.request.set('disable_border', True)
        print "update"
        #import pdb; pdb.set_trace()
        return super(RegistrationForm, self).update()
    
    def create(self,data):
        print "create"
        return EnhancedUserData(**data)

    def add(self,object):
        print "add"
        properties = dict([ (key,getattr(object,key)) for key in 'fullname','location','email','city','home_page','phone','street','country'])
        if not object.new_producent and object.producent:
            properties['producent'] = object.producent

        user = api.user.create(username=object.username,
                               password=object.password,
                               properties = properties)
        #import pdb; pdb.set_trace()
        pass

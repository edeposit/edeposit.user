# -*- coding: utf-8 -*-
from z3c.form import group, field, button
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container
from plone.app.textfield import RichText
from plone.directives import dexterity, form
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.formwidget.autocomplete import AutocompleteFieldWidget, AutocompleteMultiFieldWidget

from plone.supermodel import model
from Products.Five import BrowserView
from five import grok
from plone.app.vocabularies import users
from edeposit.user import MessageFactory as _
from plone import api
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import implements
from zope.component import adapts
from Products.statusmessages.interfaces import IStatusMessage

from plone.namedfile.interfaces import INamedBlobFileField, INamedBlobImageField
from plone.namedfile.interfaces import INamedBlobFile, INamedBlobImage

# Interface class; used to define content-type schema.

class IAgreementFileField(INamedBlobFileField):
    pass

class AgreementFile(NamedBlobFile):
    implements(IAgreementFileField)

class IProducent(model.Schema, IImageScaleTraversable):
    """
    E-Deposit Producent
    """
    pravni_forma = schema.TextLine(
        title = u"Právní forma",
        required = False,
    )

    domicile = schema.TextLine(
        title = u"Sídlo (celá adresa)",
        required = False, )

    ico = schema.ASCIILine (
        title = u"IČ",
        required = False )

    dic = schema.ASCIILine (
        title = u"DIČ",
        required = False )

    zastoupen = schema.TextLine (
        title = u"Statutární zástupce organizace",
        required = False )

    agreement = AgreementFile (
        title=_(u'Agreement'),
        description = _(u'Upload file with agreement between National Library and you.'),
        required = False,
    )        
    model.fieldset( 'agreement',
                    label=_(u"Agreement with National Library"),
                    fields = ['agreement',]
    )
    
class Producent(Container):
    # Add your class methods and properties here
    def hasAgreement(self):
        return bool(self.agreement)


def getAssignedPersonFactory(roleName):
    def getAssignedPerson(self):
        local_roles = self.get_local_roles()
        pairs = filter(lambda pair: roleName in pair[1], local_roles)
        return pairs and [ pp[0] for pp in pairs ] or None

    return getAssignedPerson

Producent.getAssignedProducentAdministrators = getAssignedPersonFactory('E-Deposit: Producent Administrator')
Producent.getAssignedProducentEditors = getAssignedPersonFactory('E-Deposit: Producent Editor')


# View class
# The view is configured in configure.zcml. Edit there to change
# its public name. Unless changed, the view will be available
# TTW at content/@@sampleview

class SampleView(BrowserView):
    """ sample view class """
    # Add view methods here
    pass

def getTermFromMember(member):
    return SimpleVocabulary.createTerm(member.id, member.id, "%s (%s)" % (member.getProperty('fullname'),member.id))

class SearchSimpleVocabulary(SimpleVocabulary):
    def search(self, query_string):
        return [v for v in self if query_string.lower() in v.title.lower()]
        
@grok.provider(IContextSourceBinder)
def allProducentAdministrators(context):
    members = api.user.get_users(groupname="Producent Administrators")
    return SearchSimpleVocabulary(map(getTermFromMember, members))
    
@grok.provider(IContextSourceBinder)
def allProducentEditors(context):
    members = api.user.get_users(groupname="Producent Editors")
    return SearchSimpleVocabulary(map(getTermFromMember, members))


class IProducentUsersForm(form.Schema):
    form.widget(administrators=AutocompleteMultiFieldWidget)    
    administrators = schema.Set (
        title = u"Správci",
        value_type = schema.Choice(source = allProducentAdministrators )
        )

    form.widget(editors=AutocompleteMultiFieldWidget)    
    editors = schema.Set (
        title = u"Editoři",
        value_type = schema.Choice(source = allProducentEditors )
        )

class ProducentToProducentUsers(object):
    implements(IProducentUsersForm)
    adapts(IProducent)

    def __init__(self, context):
        self.context = context
        self.administrators = self.context.getAssignedProducentAdministrators()
        self.editors = self.context.getAssignedProducentEditors()
    

class ProducentUsersForm(form.SchemaForm):
    schema = IProducentUsersForm
    ignoreContext = False
    label = u"Vyberte pracovníky"

    @button.buttonAndHandler(u"Nastavit oprávnění",name="save")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        localRoles = self.context.get_local_roles()
        oldAdministrators = map(lambda ii: ii[0],filter(lambda role: 'E-Deposit: Producent Administrator' in role[1],localRoles))
        oldEditors = map(lambda ii: ii[0],filter(lambda role: 'E-Deposit: Producent Editor' in role[1],localRoles))

        for userid in oldAdministrators:
            api.user.revoke_roles(obj=self.context, username=userid, roles=('E-Deposit: Producent Administrator',
                                                                            'Editor','Reader'))
            api.user.revoke_roles(obj=self.context['epublications'],
                                  username=userid,
                                  roles=( 'E-Deposit: Producent Administrator',))

        for userid in oldEditors:
            api.user.revoke_roles(obj=self.context, username=userid, roles=('E-Deposit: Producent Editor',
                                                                            'Editor','Reader'))
            api.user.revoke_roles(obj=self.context['epublications'],
                                  username=userid,
                                  roles=( 'E-Deposit: Producent Editor', 'Contributor'))

        for userid in data['administrators']:
            api.user.grant_roles(username=userid, obj=self.context,
                                 roles = ('E-Deposit: Producent Editor',
                                          'E-Deposit: Producent Administrator',
                                          'Editor', 'Reader'))
            api.user.grant_roles(username=userid, obj=self.context['epublications'],
                                 roles = ('E-Deposit: Producent Editor',
                                          'E-Deposit: Producent Administrator',
                                          'Contributor'))
        for userid in data['editors']:
            api.user.grant_roles(username=userid, obj=self.context,
                                 roles = ('E-Deposit: Producent Editor',
                                          'Editor', 'Reader'))
            api.user.grant_roles(username=userid, obj=self.context['epublications'],
                                 roles = ('E-Deposit: Producent Editor',
                                          'Contributor'))
        IStatusMessage(self.request).addStatusMessage(u"Role byly nastaveny.", "info")
        url = self.context.absolute_url()
        self.request.response.redirect(url)
        self.context.reindexObject()
    pass
    

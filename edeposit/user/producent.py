# -*- coding: utf-8 -*-
from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container
from plone.app.textfield import RichText
from plone.directives import dexterity
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from plone.supermodel import model
from Products.Five import BrowserView
from five import grok
from plone.app.vocabularies import users
from edeposit.user import MessageFactory as _

from z3c.relationfield.schema import RelationChoice, RelationList

# Interface class; used to define content-type schema.

class IProducent(model.Schema, IImageScaleTraversable):
    """
    E-Deposit Producent
    """
    domicile = schema.TextLine(
        title = u"Sídlo",
        required = False,  )

    ico = schema.TextLine (
        title = u"IČ",
        required = False )

    dic = schema.TextLine (
        title = u"DIČ",
        required = False )

    zastoupen = schema.TextLine (
        title = u"Zastoupen",
        required = False )

    agreement = NamedBlobFile(
        title=_(u'Agreement'),
        description = _(u'Upload file with agreement between National Library and you.'),
        required = False,
    )        
    model.fieldset( 'agreement',
                    label=_(u"Agreement with National Library"),
                    fields = ['agreement',]
    )
    
# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class Producent(Container):
    # Add your class methods and properties here
    pass

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

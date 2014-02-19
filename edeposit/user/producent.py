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

from edeposit.user import MessageFactory as _
from .producentadministrator import IProducentAdministrator

# Interface class; used to define content-type schema.

class IProducent(model.Schema, IImageScaleTraversable):
    """
    E-Deposit Producent
    """
    home_page = schema.TextLine(
        title = _(u'Home page'),
        description = _(u'Fill a home page we can find a producent at.'),
        required = False,
        )
    location = schema.TextLine(
        title = _(u'location'),
        description = _(u'Your location - either city and country - or in a company setting, where your office is located'),
        required = False,
        )

    street = schema.TextLine(
        title = _(u'Street'),
        description = _(u'Fill a street with number.'),
        required = True,
        )

    city = schema.TextLine(
        title=_(u'City'),
        description = _(u'Fill a city'),
        required = True,
        )

    psc = schema.ASCIILine(
        title=u'PSČ',
        required = True,
    )
    country = schema.TextLine(
        title=_(u'Country'),
        description = _(u'Fill a country'),
        required = True,
        )
    
    contact = schema.TextLine(
        title=_(u'Contact'),
        description = _(u'Fill a phone, email or name of a person we can contact.'),
        required = False,
        )
    
    agreement = NamedBlobFile(
        title=_(u'Agreement'),
        description = _(u'Upload file with agreement between National Library and you.'),
        required = False,
        )        

    model.fieldset( 'address',
                    label=_(u"Address"),
                    fields = ['street','city','country','psc']
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


# View class
# The view is configured in configure.zcml. Edit there to change
# its public name. Unless changed, the view will be available
# TTW at content/@@sampleview

class SampleView(BrowserView):
    """ sample view class """
    # Add view methods here
    pass

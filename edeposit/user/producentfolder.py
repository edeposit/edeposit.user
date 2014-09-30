# -*- coding: utf-8 -*-
from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from plone.supermodel import model
from Products.Five import BrowserView

from edeposit.user import MessageFactory as _
from plone import api

# Interface class; used to define content-type schema.

class IProducentFolder(model.Schema, IImageScaleTraversable):
    """
    E-Deposit - folder for producents
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/producentfolder.xml to define the content type.

    model.load("models/producentfolder.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class ProducentFolder(Container):
    # Add your class methods and properties here
    pass


# View class
# The view is configured in configure.zcml. Edit there to change
# its public name. Unless changed, the view will be available
# TTW at content/@@sampleview

class WorklistCSV(BrowserView):
    """Export the worklist to CSV as a one-off
    """
    
    filename = ""
    collection_name = ""
    separator = "\t"
    titles = [u"Název", 
              u"Nakladatel/vydavatel",
              u"Linka v E-Deposit "]

    def getRowValues(self,obj):
        row =  [obj.getParentTitle or "", 
                obj.getNakladatelVydavatel or "",
                obj.getURL() or ""]
        return row

    def __call__(self):
        self.request.response.setHeader("Content-type","text/csv")
        self.request.response.setHeader("Content-disposition","attachment;filename=%s.csv" % self.filename)
        header = self.separator.join(self.titles)

        def result(brain):
            return self.separator.join(self.getRowValues(brain))

        results = map(result, self.context[self.collection_name].results(batch=False))
        csvData = "\n".join([header,] + results)
        return csvData

class WorklistForISBNAgencyView(WorklistCSV):
    filename = "worklist-for-isbn-agency"
    collection_name = "originalfiles-for-isbn-agency"

class WorklistWaitingForAleph(WorklistCSV):
    filename = "worklist-waiting-for-aleph"
    collection_name = "originalfiles-waiting-for-aleph"

class WorklistWaitingForAcquisitionView(WorklistCSV):
    filename = "worklist-waiting-for-acquisition"
    collection_name = "originalfiles-waiting-for-acquisition"

class WorklistForCataloguingView(WorklistCSV):
    filename = "worklist-waiting-for-cataloguing"
    collection_name = "originalfiles-waiting-for-cataloguing"

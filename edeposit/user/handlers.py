# -*- coding: utf-8 -*-
from zope.component import queryUtility
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent,\
    IContainerModifiedEvent
from zope.interface import Interface
from plone import api
from edeposit.user import MessageFactory as _
from plone.dexterity.utils import createContentInContainer

def added(context,event):
    """When an object is added, create folder for registration of ePublications
    """
    # tool = api.portal.get_tool('translation_service')
    # title = tool.translate(msgid=u"Registration of ePublications", 
    #                        domain='edeposit.user',
    #                        context=context, 
    #                        target_language='cs')
    context.invokeFactory('edeposit.content.epublicationfolder','epublications', title=u"Ohlášení ePublikací")
    context.invokeFactory('edeposit.content.eperiodicalfolder','eperiodicals', title=u"Ohlášování ePeriodik")
    context.invokeFactory('edeposit.content.bookfolder','books', title=u"Ohlášení tištěných knih")

def addedProducentFolder(context,event):
    portal = api.portal.get()
    def queryForStates(*args):
        return [ {'i': 'portal_type',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['edeposit.content.epublication']},
                 {'i': 'review_state',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': args},
                 {'i': 'path', 
                  'o': 'plone.app.querystring.operation.string.relativePath', 
                  'v': '../'}
                 ]

    collections = [ dict( contexts=[context,],
                          name  = "producents-in-declaring",
                          title = _(u"Producents in declaring"),
                          query = [ {'i': 'portal_type',
                                     'o': 'plone.app.querystring.operation.selection.is',
                                     'v': ['edeposit.user.producent',]},
                                    {'i': 'review_state',
                                     'o': 'plone.app.querystring.operation.selection.is',
                                     'v': ['registration',]},
                                    {'i': 'path', 
                                     'o': 'plone.app.querystring.operation.string.relativePath', 
                                     'v': '../'}
                                    ],
                          roles = ['E-Deposit: Producent','E-Deposit: Acquisitor'],
                          ),
                    dict( contexts=[context,],
                          name = "approved-producents",
                          title=_(u"Approved producents"),
                          query=[{'i': 'portal_type', 
                                  'o': 'plone.app.querystring.operation.selection.is', 
                                  'v': ['edeposit.user.producent',] },
                                 {'i': 'review_state',
                                  'o': 'plone.app.querystring.operation.selection.is',
                                  'v': ['approved',]},
                                 {'i': 'path', 
                                  'o': 'plone.app.querystring.operation.string.relativePath', 
                                  'v': '../'}
                                 ],
                          roles = ['E-Deposit: Producent','E-Deposit: Acquisitor'],
                          ),
                    dict( contexts=[context,],
                          name = "producents-waiting-for-approving",
                          title=_(u"Producents waiting for approving"),
                          query=[{'i': 'portal_type', 
                                  'o': 'plone.app.querystring.operation.selection.is', 
                                  'v': ['edeposit.user.producent',] },
                                 {'i': 'review_state',
                                  'o': 'plone.app.querystring.operation.selection.is',
                                  'v': ['waitingForApproving',]},
                                 {'i': 'path', 
                                  'o': 'plone.app.querystring.operation.string.relativePath', 
                                  'v': '../'}
                                 ],
                          roles = ['E-Deposit: Producent','E-Deposit: Acquisitor'],
                          ),

                    dict( contexts=[portal],
                          name = "ePublications-in-declarating",
                          title=_(u"ePublications in declaring"),
                          query= queryForStates('declaration'),
                          roles = ['E-Deposit: Producent','E-Deposit: Acquisitor'],
                          ),
                    dict( contexts=[portal],
                          name = "ePublications-waiting-for-approving",
                          title = _(u"ePublications waiting for preparing of acquisition"),
                          query= queryForStates('waitingForApproving'),
                          roles = ['E-Deposit: Producent','E-Deposit: Acquisitor'],
                          ),
                    dict( contexts=[portal],
                          name  = "ePublications-with-errors",
                          title = _(u"ePublications with errors"),
                          query = queryForStates('declarationWithError'),
                          roles = ['E-Deposit: Producent','E-Deposit: Acquisitor'],
                          )
                    ]

    for collection in collections:
        name = collection['name']
        for folder in collection['contexts']:
            if name not in folder.keys():
                content = api.content.create (
                    id=name,
                    container=folder,
                    type='Collection', 
                    title=collection['title'],
                    query=collection['query']
                    )
                #api.group.grant_roles(groupname="Producents", roles=['Reader'], obj=content)

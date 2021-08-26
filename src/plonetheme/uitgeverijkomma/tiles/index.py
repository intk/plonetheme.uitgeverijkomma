# -*- coding: utf-8 -*-
from operator import itemgetter
from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.z3cform.widget import QueryStringFieldWidget
from plone.autoform.directives import widget
from plone.registry.interfaces import IRegistry
from plone.supermodel.model import Schema
from plone.tiles import Tile
from plone.tiles.interfaces import ITileType
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.utils import get_top_request
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.interfaces import IValue
from z3c.form.util import getSpecification
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
from zope.schema import getFields
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from plone.app.standardtiles.contentlisting import IContentListingTile
from plone.app.standardtiles.contentlisting import IContentListingTileLayer
from plone.app.standardtiles.contentlisting import ContentListingTile


class IndexTile(ContentListingTile):
    template = ViewPageTemplateFile("index.pt")

    def contents(self):
        """Search results"""
        builder = getMultiAdapter(
            (self.context, self.request),
            name='querybuilderresults'
        )
        accessor = builder(
            query=self.query,
            sort_on=self.sort_on or 'getObjPositionInParent',
            sort_order=self.sort_order,
            limit=self.limit
        )

        view = self.view_template or 'listing_view'
        options = dict(original_context=self.context, data=self.data)
        
        alsoProvides(self.request, IContentListingTileLayer)
        return getMultiAdapter((accessor, self.request), name=view)(**options)

class IIndexTile(IContentListingTile):
    image_format = schema.Choice(
        title=_(u"Choose image format"),
        description=_(u"Square is used by default"),
        values=[_(u'Square'), _(u'Landscape')],
        default=_(u'Square'),
        required=False
    )

    show_authors = schema.Bool(
        title=_(u"Show authors"),
        description=_(u"Show authors by default - according to the design"),
        default=True,
        required=True,
    )

    view_template = schema.Choice(
        title=_(u"Display mode"), source=_(u"Available Index Views"), required=True
    )


class IIndexTileLayer(IContentListingTileLayer):
    pass


@provider(IVocabularyFactory)
def availableIndexViewsVocabulary(context):
    """Get available views for listing content as vocabulary"""

    registry = getUtility(IRegistry)
    listing_views = registry.get("plonetheme.uitgeverijkomma.tiles.listing_views", {})
    if len(listing_views) == 0:
        listing_views = {
            "index_view": u"Index view"
        }
    voc = []
    for key, label in sorted(listing_views.items(), key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(key, key, label))

    return SimpleVocabulary(voc)



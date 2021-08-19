# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import provider
from operator import itemgetter
from plone.registry.interfaces import IRegistry
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.component import getUtility
from plone.app.standardtiles import PloneMessageFactory as _
from plone.autoform import directives as form
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

from plone.app.standardtiles.existingcontent import IExistingContentTile
from plone.app.standardtiles.existingcontent import ExistingContentTile

class IThreecolumnsTile(IExistingContentTile):

    show_text = schema.Bool(title=_(u"Show content text"), default=False)

    show_comments = schema.Bool(
        title=_(u"Show content comments count (if enabled)"),
        default=False,
        required=False,
    )

    show_image = schema.Bool(
        title=_(u"Show content image (if available)"),
        default=True,
        required=False,
    )

    image_scale = schema.Choice(
        title=_(u"Image scale"),
        vocabulary="plone.app.vocabularies.ImagesScales",
        required=False,
        default=u"large"
    )

    tile_class = schema.TextLine(
        title=_(u"Tile additional styles"),
        description=_(
            u"Insert a list of additional CSS classes that will"
            + u" be added to the tile"
        ),
        default=u"",
        required=False
    )

    description_alternative = schema.TextLine(
        title=_(u"Replace the description with a custom text"),
        description=_(
            u"The item's description will be replaced with the text on this field"
        ),
        default=u"",
        required=False
    )

    contact = schema.TextLine(
        title=_(u"Contact"),
        description=_(
            u"Contact"
        ),
        default=u"",
        required=False
    )

    linkedin = schema.TextLine(
        title=_(u"LinkedIn"),
        description=_(
            u"LinkedIn"
        ),
        default=u"",
        required=False
    )

    picture_credits = schema.TextLine(
        title=_(u"Foto credits"),
        description=_(
            u"Foto credits"
        ),
        default=u"",
        required=False
    )

    view_template = schema.Choice(
        title=_(u'Display mode'),
        source=_(u'Available Threecolumns Views'),
        required=True
    )

    form.omitted('show_text')
    form.omitted('show_comments')
    form.omitted('tile_class')

class ThreecolumnsTile(ExistingContentTile):

    def formatted_date(self, item):
        date_provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return date_provider(item)


@provider(IVocabularyFactory)
def availableThreecolumnsViewsVocabulary(context):
    """Get available views for a content as vocabulary"""

    registry = getUtility(IRegistry)
    threecolumns_views = (
        registry.get('plonetheme.uitgeverijkomma.tiles.threecolumns_views', {}) or {}
    )
    voc = [SimpleVocabulary.createTerm('', '', 'Default view')]
    for key, label in sorted(threecolumns_views.items(), key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)
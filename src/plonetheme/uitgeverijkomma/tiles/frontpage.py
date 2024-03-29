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

from plone.tiles.interfaces import ITileDataManager
from plonetheme.uitgeverijkomma.browser.views import get_vimeo_thumb

class IFrontpageTile(IExistingContentTile):

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

    show_author = schema.Bool(
        title=_(u"Show the authors (if item is a Product)"),
        default=True,
        required=False,
    )

    show_price = schema.Bool(
        title=_(u"Show the price (if item is a Product)"),
        default=True,
        required=False,
    )

    show_buttons = schema.Bool(
        title=_(u"Show the buttons (if item is a Product)"),
        default=True,
        required=False,
    )

    show_as_header = schema.Bool(
        title=_(u"Show content has header"),
        default=False,
        required=False,
    )

    show_large_tile = schema.Bool(
        title=_(u"Show as a large tile (needs to be placed on a single row)"),
        default=False,
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

    video_id = schema.TextLine(
        title=_(u"Video ID"),
        description=_(
            u"Item will show a video if an id is added"
        ),
        default=u"",
        required=False
    )

    video_thumb_url = schema.TextLine(
        title=_(u"Video first frame URL"),
        description=_(
            u"The first frame will be shown before the video loads (Automatic). To force a refresh: make the field empty and save changes."
        ),
        default=u"",
        required=False
    )

    view_template = schema.Choice(
        title=_(u'Display mode'),
        source=_(u'Available Frontpage Views'),
        required=True
    )

    form.omitted('show_text')
    form.omitted('show_comments')
    form.omitted('tile_class')

class FrontpageTile(ExistingContentTile):
    def get_video_url(self):
        video_thumb_url = self.data.get('video_thumb_url')

        if not video_thumb_url:
            video_id = self.data.get('video_id')
            if video_id:
                video_thumb = get_vimeo_thumb(vimeo_id=video_id)
                dataManager = ITileDataManager(self)
                self.data['video_thumb_url'] = video_thumb
                dataManager.set(self.data)
                return video_thumb
            else:
                return None
        else:
            return video_thumb_url

    def get_item_price(self, item):
        price = getattr(item, 'price', '99,-')
        if price:
            return "€ %s" %(price)
        else:
            return "€ 99,-"

    def formatted_date(self, item):
        date_provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return date_provider(item)


@provider(IVocabularyFactory)
def availableFrontpageViewsVocabulary(context):
    """Get available views for a content as vocabulary"""

    registry = getUtility(IRegistry)
    frontpage_views = (
        registry.get('plonetheme.uitgeverijkomma.tiles.frontpage_views', {}) or {}
    )
    voc = [SimpleVocabulary.createTerm('', '', 'Default view')]
    for key, label in sorted(frontpage_views.items(), key=itemgetter(1)):
        voc.append(SimpleVocabulary.createTerm(key, key, label))
    return SimpleVocabulary(voc)

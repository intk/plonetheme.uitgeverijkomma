#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plonetheme.uitgeverijkomma import _

from zope.interface import provider
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.textfield import RichText as RichTextField
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.supermodel import model
from zope import schema
from collective import dexteritytextindexer
from urllib.parse import urlparse

class ContextToolsView(BrowserView):

    def get_vimeo_id(self, video_url):
        if video_url:
            try:
                video_id = urlparse(video_url).path.lstrip("/")
                return video_id
            except:
                return None
        else:
            return None

    def get_folder_contents(self, folder):
        return folder.getFolderContents()

    def get_videos_from_folder(self, contents):
        videos = [brain for brain in contents if getattr(brain, 'portal_type', None) in ["WildcardVideo"]]
        return videos

    def get_images_from_folder(self, contents):
        images = [brain for brain in contents if getattr(brain, 'portal_type', None) in ["Image"]]
        return images

    def get_slideshow_folder(self, item):
        for brain in item.getFolderContents():
            if brain.id == "slideshow":
                return brain.getObject()
        
        return None

    def get_slideshow_items(self, item):

        slideshow = self.get_slideshow_folder(item)

        if slideshow:

            results = {}
            contents = self.get_folder_contents(slideshow)
            images = self.get_images_from_folder(contents)
            videos = self.get_videos_from_folder(contents)

            results['videos'] = videos
            results['images'] = images
            return results
        else:
            return {"videos": [], "images": []}


    def trimText(self, text, limit):
        try:
            if text != None:
                if len(text) > limit:
                    res = text[0:limit]
                    lastspace = res.rfind(" ")
                    res = res[0:lastspace] + " ..."
                    return res
                else:
                    return text
            else:
                return ""
        except:
            return text

@provider(IFormFieldProvider)
class IBook(model.Schema):
    """Interface for Books behavior."""

    # exhibition fieldset
    model.fieldset(
        'book',
        label=_(u'Book', default=u'Book'),
        fields=['specs'],
    )

    specs = RichTextField(
        title=_(u'Specs'),
        description=u'',
        required=False,
    )
    form.widget('specs', RichTextFieldWidget)
    dexteritytextindexer.searchable('notes')


    model.fieldset(
        'shop',
        label=_(u'Shop', default=u'Shop'),
        fields=['price', 'soldout'],
    )

    price = schema.TextLine(
        title=_(u"Price"),
        description=_(
            u"Enter the full price"
        ),
        default=u"",
        required=False
    )

    soldout = schema.Bool(
        title=_(u"Item is sold out"),
        default=False,
        required=False,
    )

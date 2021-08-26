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
import urllib.request, json 

import plone.api
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior

def get_vimeo_id(video_url):
    if video_url:
        try:
            video_id = urlparse(video_url).path.lstrip("/")
            return video_id
        except:
            return None
    else:
        return None

def fix_all_videos():

    from wildcard.media.subscribers import video_edited
    import transaction
    all_videos = plone.api.content.find(portal_type="WildcardVideo", Language='nl')
    all_videos_en = plone.api.content.find(portal_type="WildcardVideo", Language='en')

    for v_brain in all_videos:
        v_obj = v_brain.getObject()
        video_edited(v_obj, None)
        v_obj.reindexObject()
        transaction.get().commit()

    for v_brain in all_videos_en:
        v_obj = v_brain.getObject()
        video_edited(v_obj, None)
        v_obj.reindexObject()
        transaction.get().commit()

    return True
    

class ContextToolsView(BrowserView):

    def get_lead_image(self, item):

        if getattr(item, 'portal_type', '') in ['product', 'Product']:
            slideshow = self.get_slideshow_folder(item)

            if slideshow:
                contents = self.get_folder_contents(slideshow)

                for brain in contents:
                    if getattr(brain, 'portal_type', '') in ['Image']:
                        return brain
                        
                return None
            else:
                return None
        else:
            return None

    def get_item_price(self, item):

        soldout = getattr(item, 'soldout', False)

        if soldout:
            if getattr(self.context, 'language', "") == "nl":
                return "Uitverkocht"
            else:
                return "Sold out"

        price = getattr(item, 'price', '99,-')
        if price:
            return "€ %s" %(price)
        else:
            return "€ 99,-"

    def get_listing_item_video_id(self, item):
 
        videos = plone.api.content.find(context=item, portal_type="WildcardVideo")

        if videos:
            video_brain = videos[0]
            video = video_brain.getObject()
            url = getattr(video, 'youtube_url', '')   
            video_thumb_url = getattr(video, 'vimeo_thumb_url', '')
            
            return {"video_id":self.get_vimeo_id(url), "thumb_url": video_thumb_url}
        else:
            return {"video_id":None, "thumb_url": None}

    def get_vimeo_id(self, video_url):
        return get_vimeo_id(video_url)

    def get_folder_contents(self, folder):
        return folder.getFolderContents()

    def get_videos_from_folder(self, contents):
        videos = [brain for brain in contents if getattr(brain, 'portal_type', None) in ["WildcardVideo"]]
        video_thumb_url = None

        if videos:
            video = videos[0].getObject()
            video_thumb_url = getattr(video, 'vimeo_thumb_url', None)

        return videos, video_thumb_url

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
            videos, video_thumb_url = self.get_videos_from_folder(contents)

            results['videos'] = videos
            results['images'] = images
            results['video_thumb_url'] = video_thumb_url
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
        fields=['specs', 'author'],
    )

    specs = RichTextField(
        title=_(u'Specs'),
        description=u'',
        required=False,
    )
    form.widget('specs', RichTextFieldWidget)
    dexteritytextindexer.searchable('notes')


    author = schema.TextLine(
        title=_(u"Author"),
        description=_(
            u"Enter the name of the author(s)"
        ),
        default=u"",
        required=False
    )

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


def get_vimeo_thumb(video_url="https://vimeo.com/578160762"):

    VIMEO_GET_JSON_URL = "https://vimeo.com/api/v2/video/%s.json"

    vimeo_id = get_vimeo_id(video_url)

    if vimeo_id:
        get_json_url = VIMEO_GET_JSON_URL % (vimeo_id)
        with urllib.request.urlopen(get_json_url) as url:
            data = json.loads(url.read().decode())
            if data:
                vimeo_json = data[0]
                thumb_large = vimeo_json.get('thumbnail_large', '')
                if thumb_large:
                    return thumb_large.replace('_640', '')
                else:
                    return None
            else:
                return None
    else:
        return None



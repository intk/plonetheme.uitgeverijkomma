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

class ContextToolsView(BrowserView):

    def get_images_from_folder(self, folder):
        images = [brain for brain in folder.getFolderContents() if getattr(brain, 'portal_type', None) == "Image"]
        return images

    def get_slideshow_folder(self, item):
        for brain in item.getFolderContents():
            if brain.id == "slideshow":
                return brain.getObject()
        
        return None

    def get_slideshow_images(self, item):

        slideshow = self.get_slideshow_folder(item)

        if slideshow:
            images = self.get_images_from_folder(slideshow)
            return images
        else:
            return []


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
        fields=['price'],
    )

    price = schema.TextLine(
        title=_(u"Price"),
        description=_(
            u"Enter the full price"
        ),
        default=u"",
        required=False
    )


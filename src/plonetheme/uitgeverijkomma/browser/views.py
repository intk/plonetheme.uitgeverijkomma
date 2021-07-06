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


#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Products.Five import BrowserView

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


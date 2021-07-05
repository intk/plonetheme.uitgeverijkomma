#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from datetime import date
from DateTime import DateTime
import time


def get_event_date_state(event):
    if event.portal_type != 'Event':
        return False
    else:
        try:
            t = DateTime(time.time())
            if event.end is not None:
                end = DateTime(event.end)
                start = DateTime(event.start)
            
                if end.year() < t.year() or (end.year() == t.year() and end.month() < t.month()) or (end.year() == t.year() and end.month() == t.month() and end.day() < t.day()):
                    return "past"
                elif (start.year() == t.year() and start.month() < t.month()) or (start.year() == t.year() and start.month() == t.month() and start.day() <= t.day()) or (start.year() < t.year() and end.year() >= t.year() and end.month() >= t.month()) or (start.year() < t.year() and end.year() >= t.year() and end.month() == t.month() and t.day() <= end.day()):
                    return "current"
                else:
                    return "future"
            else:
                start = DateTime(event.start)
                if start.year() < t.year() or (start.year() == t.year() and start.month() < t.month()) or(start.year() == t.year() and start.month() == t.month() and start.day() < t.day()):
                    return "past"
                elif (start.year() == t.year() and start.month() < t.month()) or (start.year() == t.year() and start.month() == t.month() and start.day() <= t.day()):
                    return "current"
                else:
                    return "future"
        except:
            return False

    return True


class ContextToolsView(BrowserView):

    def getEventDateState(self, event):
        return get_event_date_state(event)

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


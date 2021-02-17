# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.theme.interfaces import IDefaultPloneLayer

class IPlonethemeModernBaseLayer(IDefaultPloneLayer):
    """Marker interface that defines a browser layer."""

class IuitgeverijkommaSpecific(IDefaultPloneLayer):
	"""Marker interface that defines a Zope 3 browser layer.
	"""
	
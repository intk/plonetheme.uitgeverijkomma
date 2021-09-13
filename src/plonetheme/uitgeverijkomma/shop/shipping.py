# -*- coding: utf-8 -*-
from bda.plone.cart.interfaces import IShippingSettings
from bda.plone.cart.shipping import Shipping
from bda.plone.shop.utils import get_shop_shipping_settings
from bda.plone.cart.cart import get_data_provider
from bda.plone.checkout.interfaces import ICheckoutFormPresets
from zope.component import getMultiAdapter
from bda.plone.cart.interfaces import IShippingItem
import pycountry

from plone import api
from plonetheme.uitgeverijkomma import _
from decimal import Decimal

from pycountry_convert import (
    convert_country_alpha2_to_continent
)

HEXSPOOR_SHIPPING_COSTS = {
    "Europe": {
        "NL": {"<3": Decimal(0), "<15": Decimal(0), ">=15": Decimal(0)},
        "BE": {"<3": Decimal(7.5), "<15": Decimal(9.5), ">=15": Decimal(11.5)},
        "DE": {"<3": Decimal(8.25), "<15": Decimal(9.75), ">=15": Decimal(15.5)},
        "FR": {"<3": Decimal(11.5), "<15": Decimal(13.5), ">=15": Decimal(16.5)},
        "GB": {"<3": Decimal(11.5), "<15": Decimal(13.5), ">=15": Decimal(16.5)},

        "AT": {"<3": Decimal(14.0), "<15": Decimal(15.0), ">=15": Decimal(18.5)},
        "LU": {"<3": Decimal(14.0), "<15": Decimal(15.0), ">=15": Decimal(18.5)},
        "CZ": {"<3": Decimal(14.0), "<15": Decimal(15.0), ">=15": Decimal(18.5)},
        "PL": {"<3": Decimal(14.0), "<15": Decimal(15.0), ">=15": Decimal(18.5)},

        "DK": {"<3": Decimal(14.0), "<15": Decimal(16.5), ">=15": Decimal(18.5)},
        "SE": {"<3": Decimal(14.0), "<15": Decimal(16.5), ">=15": Decimal(18.5)},
        "FI": {"<3": Decimal(14.0), "<15": Decimal(16.5), ">=15": Decimal(18.5)},

        "IT": {"<3": Decimal(14.0), "<15": Decimal(17.5), ">=15": Decimal(20.0)},
        "ES": {"<3": Decimal(14.0), "<15": Decimal(17.5), ">=15": Decimal(20.0)},
        "PT": {"<3": Decimal(14.0), "<15": Decimal(17.5), ">=15": Decimal(20.0)},
        "IE": {"<3": Decimal(14.0), "<15": Decimal(17.5), ">=15": Decimal(20.0)},

        "HU": {"<3": Decimal(14.5), "<15": Decimal(19.5), ">=15": Decimal(20.0)},
        "HR": {"<3": Decimal(14.5), "<15": Decimal(19.5), ">=15": Decimal(20.0)},
        "EE": {"<3": Decimal(14.5), "<15": Decimal(19.5), ">=15": Decimal(20.0)},
        "LT": {"<3": Decimal(14.5), "<15": Decimal(19.5), ">=15": Decimal(20.0)},
        "LV": {"<3": Decimal(14.5), "<15": Decimal(19.5), ">=15": Decimal(20.0)},
        "RO": {"<3": Decimal(14.5), "<15": Decimal(19.5), ">=15": Decimal(20.0)},
        "SI": {"<3": Decimal(14.5), "<15": Decimal(19.5), ">=15": Decimal(20.0)},
        "SK": {"<3": Decimal(14.5), "<15": Decimal(19.5), ">=15": Decimal(20.0)},

        "NO": {"<3": Decimal(20.0), "<15": Decimal(22.5), ">=15": Decimal(25.0)},
        "CH": {"<3": Decimal(20.0), "<15": Decimal(22.5), ">=15": Decimal(25.0)},

        "REST": {"<3": Decimal(20.0), "<15": Decimal(22.5), ">=15": Decimal(25.0)},
    },
    
    "North America": {
        "REST": {"<3": Decimal(38.0), "<15": Decimal(45.0), ">=15": Decimal(56.0)}
    },

    "Asia": {
        "REST": {"<3": Decimal(44.0), "<15": Decimal(55.0), ">=15": Decimal(70.0)}
    },

    "Oceania": {
        "REST": {"<3": Decimal(44.0), "<15": Decimal(55.0), ">=15": Decimal(70.0)}
    },

    "Russia": {
        "REST": {"<3": Decimal(53.0), "<15": Decimal(63.0), ">=15": Decimal(78.0)}
    },

    "South Africa": {
        "REST": {"<3": Decimal(53.0), "<15": Decimal(63.0), ">=15": Decimal(78.0)}
    },

    "South America": {
        "REST": {"<3": Decimal(53.0), "<15": Decimal(63.0), ">=15": Decimal(78.0)}
    },

    "Africa": {
        "REST": {"<3": Decimal(62.0), "<15": Decimal(71.0), ">=15": Decimal(92.0)}
    },
}

UNKNOWN_SHIPPING = Decimal(50)

def get_continent(country_code):
    if country_code == "RU":
        return "Russia"

    if country_code == "ZA":
        return "South Africa"

    try:
        return convert_country_alpha2_to_continent(country_code)
    except:
        return ""

def convert_country_to_alpha2(country_code):
    country = pycountry.countries.get(numeric=country_code)
    return country.alpha_2

def calculate_weight(items):
    total_weight = Decimal(0)

    for uid, count, _ in items:
        try:
            obj = api.content.get(UID=uid)
        except ValueError:
            continue

        shipping = IShippingItem(obj)
        item_weight = shipping.weight
        if item_weight:
            total_weight += Decimal(item_weight) * count

    return total_weight
    
def get_costs_by_weight(country_costs, weight, country):
    continent = get_continent(country)
    minimum = 3

    if continent not in ["Europe"]:
        minimum = 10

    if weight < minimum:
        return country_costs.get('<3', '')
    elif weight < 15:
        return country_costs.get('<15', '')
    else:
        return country_costs.get('>=15', '')

def get_shipping_for_country(country, weight):
    countries_shipping_costs = HEXSPOOR_SHIPPING_COSTS.get(get_continent(country), None)

    if countries_shipping_costs:
        if country in countries_shipping_costs:
            return get_costs_by_weight(countries_shipping_costs[country], weight, country)
        else:
            return get_costs_by_weight(countries_shipping_costs['REST'], weight, country)
    else:
        return UNKNOWN_SHIPPING

def get_delivery_data(request):

    delivery_data = {
        'alternative_delivery': False,
        'delivery_address_country': 'NL',
        'billing_address_country': 'NL'
    }

    if 'checkout.billing_address.country' not in request:
        cookies = request.cookies

        delivery_data['alternative_delivery'] = cookies.get('alternative_delivery', '')

        if delivery_data['alternative_delivery'] not in ['', 'False']:
            delivery_data['alternative_delivery'] = True
        else:
            delivery_data['alternative_delivery'] = False

        delivery_data['billing_address_country'] = cookies.get('billing_address_country', '')
        delivery_data['delivery_address_country'] = cookies.get('delivery_address_country', '')

    else:
        delivery_data['alternative_delivery'] = request.get('checkout.delivery_address.alternative_delivery')
        if delivery_data['alternative_delivery'] != None:
            delivery_data['alternative_delivery'] = True
        else:
            delivery_data['alternative_delivery'] = False

        delivery_data['billing_address_country'] = request.get('checkout.billing_address.country', '')
        delivery_data['delivery_address_country'] = request.get('checkout.delivery_address.country', '')

    return delivery_data

def get_total_shipping_costs(context, request, items, delivery_data=None):

    shipping_costs = Decimal(0)

    if not delivery_data:
        delivery_data = get_delivery_data(request)

    alternative_delivery = delivery_data['alternative_delivery']
    country_billing = delivery_data['billing_address_country']
    country_delivery = delivery_data['delivery_address_country']

    default_delivery_country = country_billing

    if alternative_delivery and country_billing != country_delivery:
        default_delivery_country = country_delivery
    
    if default_delivery_country:
        final_country = convert_country_to_alpha2(default_delivery_country)
    else:
        final_country = "NL"

    total_weight = calculate_weight(items)
    shipping_costs += get_shipping_for_country(final_country, total_weight)

    print("Alternative delivery: '%s'" %(alternative_delivery))
    print("Country billing: %s" %(country_billing))
    print("Country delivery: %s" %(country_delivery))
    print("Delivering to: %s" %(final_country))
    print("Total shipping costs: %s" %(shipping_costs))

    return shipping_costs


class HexspoorShipping(Shipping):
    sid = "hexspoor_shipping"
    label = _("hexspoor_shipping", default="Hexspoor Shipping")


    @property
    def description(self):
        return _(
            "hexspoor_shipping_description",
            default="Default shipping with Hexspoor",
        )

    def net(self, items, delivery_data=None):
        request = self.context.REQUEST

        settings = get_shop_shipping_settings()
        cart_data = get_data_provider(self.context)
        shipping_limit_from_gross = settings.shipping_limit_from_gross

        purchase_price = Decimal(0)

        if shipping_limit_from_gross:
            purchase_price += cart_data.net(items) + cart_data.vat(items)
        else:
            purchase_price += cart_data.net(items)

        shipping_costs = get_total_shipping_costs(self.context, request, items)

        return shipping_costs

    def vat(self, items):
        return Decimal("0")
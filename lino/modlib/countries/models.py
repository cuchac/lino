# -*- coding: UTF-8 -*-
# Copyright 2008-2014 Luc Saffre
# This file is part of the Lino project.
# Lino is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
Defines models
:class:`Country` and
:class:`Place`.

"""


import datetime
from django.db import models
from django.conf import settings

from lino import dd
#~ from lino import layouts
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from django.core.exceptions import ValidationError


from lino.modlib.contacts import Plugin


class PlaceTypes(dd.ChoiceList):

    """
    Sources used:
    
    - http://en.wikipedia.org/wiki/List_of_subnational_entities
    
    """
    verbose_name = _("Place Type")
add = PlaceTypes.add_item
# ~ add('10', pgettext_lazy(u'countries','State'))             # de:Bundesland
add('10', _('Member State'))      # de:Bundesland
add('11', _('Division'))
add('12', _('Region'))
add('13', _('Community'))            # fr:Communauté de: Gemeinschaft
add('14', _('Territory'))
# ~ add('15', _('City-state'))        # et:Linnriik  de:Stadtstaat  fr:Cité-État

add('20', _('County'), 'county')      # et:maakond   de:Regierungsbezirk
add('21', _('Province'), 'province')
add('22', _('Shire'))
add('23', _('Subregion'))
add('24', _('Department'))
add('25', _('Arrondissement'))
add('26', _('Prefecture'))
add('27', _('District'))          # de:Kreis
add('28', _('Sector'))

add('50', _('City'), 'city')              # et:suurlinn  de:Stadt
add('51', _('Town'), 'town')              # et:linn      de:Kleinstadt
# et:vald     de:Gemeinde fr:Commune
add('52', _('Municipality'), 'municipality')
# ~ add('53', _('Commune'),'commune')           # de:Kommune fr:Commune
add('54', _('Parish'), 'parish')           # de:Pfarre fr:Paroisse
add('55', _('Township'), 'township')         # de:Stadtteil fr:?
add('56', _('Quarter'), 'quarter')           # de:Viertel fr:Quartier

add('61', _('Borough'), 'borough')           # et:alev
add('62', _('Small borough'), 'smallborough')     # et:alevik

add('70', _('Village'), 'village')           # et:küla

#~ REGION_TYPES = '10 11 12 13 14 15 20 21 22 23 24 25 26 27 28'
#~ REGION_TYPES = [PlaceTypes.get_by_value(v) for v in REGION_TYPES.split()]


class CountryDriver(object):

    def __init__(self, region_types, city_types):
        self.region_types = [PlaceTypes.get_by_value(v)
                             for v in region_types.split()]
        self.city_types = [PlaceTypes.get_by_value(v)
                           for v in city_types.split()]


class CountryDrivers:
    BE = CountryDriver('21', '50 70')
    EE = CountryDriver('20', '50 51 52 61 62 70')
    DE = CountryDriver('10', '50 51 52 70')
    FR = CountryDriver('24', '50 51 52 70')


class Country(dd.BabelNamed):

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    isocode = models.CharField(max_length=4, primary_key=True,
                               verbose_name=_("ISO code"),
        help_text=_("""\
        The two-letter code for this country as defined by ISO 3166-1. 
        For countries that no longer exist it may be a 4-letter code."""))
    #~ name = models.CharField(max_length=200)
    #~ name = d.BabelCharField(max_length=200,verbose_name=_("Designation"))
    short_code = models.CharField(max_length=4, blank=True,
                                  verbose_name=_("Short code"),
        help_text=_("""A short abbreviation for regional usage. Obsolete."""))
    iso3 = models.CharField(max_length=3, blank=True,
                            verbose_name=_("ISO-3 code"),
        help_text=_("""The three-letter code for this country as defined by ISO 3166-1."""))

    #~ def __unicode__(self):
        #~ return babel.babelattr(self,'name')

    def allowed_city_types(self):
        cd = getattr(CountryDrivers, self.isocode, None)
        if cd is not None:
            return cd.region_types + cd.city_types
        return PlaceTypes.items()


#~ add_babel_field(Country,'name')

class Countries(dd.Table):
    help_text = _("""
    A country is a geographic entity considered a "nation".
    """)
    #~ label = _("Countries")
    model = 'countries.Country'
    required = dd.Required(user_groups='office')
    order_by = ["name", "isocode"]
    column_names = "name isocode *"
    detail_layout = """
    isocode name short_code
    countries.PlacesByCountry
    """


FREQUENT_COUNTRIES = ['BE', 'NL', 'DE', 'FR', 'LU']


class Place(dd.BabelNamed):

    class Meta:
        verbose_name = _("Place")
        verbose_name_plural = _("Places")
        if not settings.SITE.allow_duplicate_cities:
            unique_together = ('country', 'parent', 'name', 'type')
            #~ unique_together = ('country','parent','name','type','zip_code')

    #~ name = models.CharField(max_length=200)
    country = models.ForeignKey('countries.Country')
    zip_code = models.CharField(max_length=8, blank=True)
    type = PlaceTypes.field(blank=True)
    parent = models.ForeignKey(
        'self',
        blank=True, null=True,
        verbose_name=_("Part of"),
        help_text=_("The superordinate geographic place \
        of which this place is a part."))

    #~ def __unicode__(self):
        #~ return self.name

    def get_parents(self, *grandparents):
        if self.parent_id:
            return self.parent.get_parents(self, *grandparents)
        return [self] + list(grandparents)

    @dd.chooser()
    def type_choices(cls, country):
        if country is not None:
            allowed = country.allowed_city_types()
            return [(i, t) for i, t in PlaceTypes.choices if i in allowed]
        return PlaceTypes.choices

    def get_choices_text(self, request, actor, field):
        """
        Extends the default behaviour (which would simply diplay this
        city in the current language) by also adding the name in other
        languages.
        """
        names = [self.name]
        for lng in settings.SITE.BABEL_LANGS:
            #~ n = getattr(self,'name_'+lng)
            n = getattr(self, 'name' + lng.suffix)
            if n and not n in names:
                names.append(n)
                #~ s += ' / ' + n
        if len(names) == 1:
            return names[0]
        return "%s (%s)" % (names[0], ', '.join(names[1:]))
        #~ return s
        #~ return unicode(self)


class Places(dd.Table):
    help_text = _("""
    The table of known geographical places.
    A geographical place can be a city, a town, a suburb,
    a province, a lake... any named geographic entity,
    except for countries because these have their own table.
    """)

    model = 'countries.Place'
    required = dd.Required(user_level='admin', user_groups='office')
    order_by = "country name".split()
    column_names = "country name type zip_code *"
    detail_layout = """
    name country 
    type parent zip_code id 
    PlacesByPlace
    """


class PlacesByPlace(Places):
    label = _("Subdivisions")
    master_key = 'parent'
    column_names = "name type zip_code *"
    required = dd.Required(user_groups='office')


class PlacesByCountry(Places):
    master_key = 'country'
    column_names = "name type zip_code *"
    #~ required = dd.Required(user_groups='office')
    required = dd.Required()
    details_of_master_template = _("%(details)s in %(master)s")


class CountryCity(dd.Model):

    """
    Model mixin that adds two fields `country` and `city` 
    and defines 
    a context-sensitive chooser for `city`, 
    a `create_city_choice` method, ...
    """
    class Meta:
        abstract = True

    country = models.ForeignKey(
        "countries.Country", blank=True, null=True)
    city = models.ForeignKey(
        'countries.Place',
        verbose_name=_('City'),
        blank=True, null=True)

    @dd.chooser()
    def city_choices(cls, country):
        if country is None:
            cd = None
            flt = models.Q()
        else:
            cd = getattr(CountryDrivers, country.isocode, None)
            flt = models.Q(country=country)

        #~ types = [PlaceTypes.blank_item] 20120829
        types = [None]
        if cd:
            types += cd.city_types
            #~ flt = flt & models.Q(type__in=cd.city_types)
        else:
            types += [v for v in PlaceTypes.items() if v.value >= '50']
            #~ flt = flt & models.Q(type__gte=PlaceTypes.get_by_value('50'))
        flt = flt & models.Q(type__in=types)
        #~ flt = flt | models.Q(type=PlaceTypes.blank_item)
        return Place.objects.filter(flt).order_by('name')

        #~ if country is not None:
            #~ cd = getattr(CountryDrivers,country.isocode,None)
            #~ if cd:
                #~ return Place.objects.filter(
                    #~ country=country,
                    #~ type__in=cd.city_types).order_by('name')
            #~ return country.place_set.order_by('name')
        #~ return cls.city.field.rel.to.objects.order_by('name')

    def create_city_choice(self, text):
        """
        Called when an unknown city name was given.
        Try to auto-create it.
        """
        if self.country is not None:
            return Place.lookup_or_create('name', text, country=self.country)

        raise ValidationError(
            "Cannot auto-create city %r if country is empty", text)

    def country_changed(self, ar):
        """
        If user changes the `country`, then the `city` gets lost.
        """
        if self.city is not None and self.country != self.city.country:
            self.city = None

    def full_clean(self, *args, **kw):
        if self.city is not None and self.city.country is not None \
                and self.country != self.city.country:
            self.country = self.city.country
        super(CountryCity, self).full_clean(*args, **kw)


class CountryRegionCity(CountryCity):
    region = models.ForeignKey(
        'countries.Place',
        blank=True, null=True,
        verbose_name=_('Region'),
        related_name="%(app_label)s_%(class)s_set_by_region")
        #~ related_name='regions')
    zip_code = models.CharField(_("Zip code"), max_length=10, blank=True)

    class Meta:
        abstract = True

    @dd.chooser()
    def region_choices(cls, country):
        if country is not None:
            cd = getattr(CountryDrivers, country.isocode, None)
            if cd:
                flt = models.Q(type__in=cd.region_types)
            else:
                flt = models.Q(type__lt=PlaceTypes.get_by_value('50'))
            #~ flt = flt | models.Q(type=PlaceTypes.blank_item)
            flt = flt & models.Q(country=country)
            return Place.objects.filter(flt).order_by('name')
            #~ return Place.filter(flt).order_by('name')
        else:
            flt = models.Q(type__lt=PlaceTypes.get_by_value('50'))
            return Place.objects.filter(flt).order_by('name')

    def create_city_choice(self, text):
        # if a Place is created by super, then we add our region
        obj = super(CountryRegionCity, self).create_city_choice(text)
        obj.region = self.region
        return obj

    @dd.chooser()
    def city_choices(cls, country, region):
        qs = super(CountryRegionCity, cls).city_choices(country)

        if region is not None:
            parent_list = [p.pk for p in region.get_parents()] + [None]
            #~ print 20120822, region,region.get_parents(), parent_list
            qs = qs.filter(parent__id__in=parent_list)
            #~ print flt

        return qs

            #~ return country.place_set.filter(flt).order_by('name')
        #~ return cls.city.field.rel.to.objects.order_by('name')


def setup_config_menu(site, ui, profile, m):
    m = m.add_menu("contacts", Plugin.verbose_name)
    m.add_action(Countries)
    m.add_action(Places)

#~ def setup_explorer_menu(site,ui,profile,m):
    #~ m = m.add_menu("contacts",Plugin.verbose_name)
    #~ m.add_action(Places)

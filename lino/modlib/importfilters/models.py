# Copyright 2009-2014 Luc Saffre
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
The :xfile:`models.py` module of the :mod:`lino.modlib.system` app.
"""

import logging
logger = logging.getLogger(__name__)
#~ from lino.utils import dblogger

from django.conf import settings
from django.contrib.contenttypes import models as contenttypes
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode


from django.db import models
from django.utils.translation import ugettext_lazy as _


from lino import dd

from lino.utils.instantiator import Instantiator


class FieldSeparators(dd.ChoiceList):
    pass


class Filter(dd.Model):
    name = models.CharField(_("Name"), max_length=200)
    content_type = dd.ForeignKey(contenttypes.ContentType,
                                 verbose_name=_("Model"))
    field_sep = models.CharField(_("Field separator"), max_length=10)
    help_text = dd.RichTextField(_("HelpText"),
                                 blank=True, null=True, format='plain')


class Filters(dd.Table):
    model = Filter
    column_names = "name content_type *"
    detail_layout = """
    name content_type field_sep
    help_text
    importfilters.ItemsByFilter
    """


class Item(dd.Sequenced):

    class Meta:
        verbose_name = _("Import Filter Item")
        verbose_name_plural = _("Import Filter Items")

    filter = dd.ForeignKey(Filter)
    field = models.CharField(_("Field"), max_length=200)
    column = models.IntegerField(_("Column"))

    help_text = dd.RichTextField(_("HelpText"),
                                 blank=True, null=True, format='plain')

    @dd.chooser(simple_values=True)
    def field_choices(cls, filter):
        l = []
        if filter is not None:
            model = filter.content_type.model_class()
            meta = model._meta
            for f in meta.fields:
                if not getattr(f, '_lino_babel_field', False):
                    l.append(f.name)
            l.sort()
        return l


class Items(dd.Table):
    model = Item
    column_names = "column field help_text *"


class ItemsByFilter(Items):
    master_key = 'filter'
    column_names = "column field help_text workflow_buttons *"


class Import(dd.VirtualTable):
    column_names = 'description obj2unicode'
    parameters = dict(
        filter=dd.ForeignKey(Filter),
        data=dd.RichTextField(_("Data to import"),
                              blank=True, null=True,
                              format='plain'))

    @classmethod
    def get_data_rows(self, ar):
        flt = ar.param_values.filter
        build = Instantiator(flt.content_type.model_class()).build
        for ln in ar.param_values.data.splitlines():
            ln = ln.strip()
            if ln:
                kw = dict()
                cells = flt.field_sep.split(ln)
                for item in flt.item_set.all():
                    if item.column:
                        kw[item.field] = cells[item.column-1]
                yield build(**kw)

    @dd.displayfield(_("Description"))
    def description(cls, obj, ar):
        kw = dict()
        flt = ar.param_values.filter
        for item in flt.item_set.all():
            kw[item.field] = getattr(obj, item.field)
        return unicode(kw)

    @dd.displayfield(_("obj2unicode"))
    def obj2unicode(cls, obj, ar):
        return dd.obj2unicode(obj)


def setup_config_menu(site, ui, profile, m):
    p = site.plugins.importfilters
    m = m.add_menu('filters', p.verbose_name)
    m.add_action('importfilters.Filters')
    m.add_action('importfilters.Import')


def setup_explorer_menu(site, ui, profile, m):
    p = site.plugins.importfilters
    m = m.add_menu('filters', p.verbose_name)
    m.add_action('importfilters.Filters')

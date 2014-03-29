# -*- coding: UTF-8 -*-
# Copyright 2014 Luc Saffre
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

"""Defines a virtual table SimilarPersons.

Current implementation is very primitive: same last_name and same
first letter of first_name.

We plan to add another table with NYSIIS or SOUNDEX strings.

"""

from __future__ import unicode_literals

# import fuzzy
# fuzzy.nysiis()


import logging
logger = logging.getLogger(__name__)


from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


from lino import dd

contacts = dd.resolve_app('contacts')

class SimilarPersons(dd.VirtualTable):
    label = _("Similar Persons")
    slave_grid_format = 'html'

    class Row:

        def __init__(self, master, slave):
            self.master = master
            self.slave = slave

    @classmethod
    def get_data_rows(self, ar):
        mi = ar.master_instance
        if mi is None:
            return

        # others = set()

        for o in self.find_similar_instances(mi):
            # if not o in others:
            #     others.add(o)
            yield self.Row(mi, o)

        # for o in find_similar_instances(mi, 5, 'last_name'):
        #     if not o in others:
        #         others.add(o)
        #         yield self.Row(mi, o)

    # @classmethod
    # def get_target_model(self, obj):
    #     return obj.__class__
    
    @classmethod
    def get_words(self, obj):
        s1 = set()
        for s in (obj.last_name, obj.first_name):
            for word in s.split():
                s1.add(word)
        s2 = set()
        for n in s1:
            for word in s.split('-'):
                s2.add(word)
        return s2
    
    @classmethod
    def find_similar_instances(self, obj):
        flt = models.Q()
        for w in self.get_words(obj):
            flt |= models.Q(last_name__icontains=w)
            flt |= models.Q(first_name__icontains=w)
        # model = self.get_target_model(obj)
        qs = contacts.Person.objects.exclude(pk=obj.pk)
        return qs.filter(flt)
        # v = obj.first_name[:2]
        # return qs.filter(
        #     last_name__icontains=obj.last_name,
        #     first_name__istartswith=v)

    @dd.displayfield(_("Other"))
    def other(self, obj, ar):
        return ar.obj2html(obj.slave)


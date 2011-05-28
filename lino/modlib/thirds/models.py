#coding: UTF-8
## Copyright 2011 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


#~ import lino
#~ logger.debug(__file__+' : started')

from lino import reports
from lino.utils import perms
from lino import mixins
from lino.modlib.contacts import models as contacts

class Third(
    mixins.Sequenced,
    contacts.PartnerDocument,
    mixins.Owned):
    
    class Meta:
        verbose_name = _("Third Party")
        verbose_name_plural = _('Third Parties')
        
    remark = models.TextField(_("Remark"),blank=True,null=True)
    
    def set_seqno(self):
        qs = Third.objects.filter(owner_type__exact=self.owner_type,
          owner_id__exact=self.owner_id).order_by('seqno')
        n = qs.count()
        if n == 0:
            self.seqno = 1
        else:
            last = qs[n-1]
            self.seqno = last.seqno + 1
            
    def summary_row(self,ui,rr,**kw):
        s = ''
        s += ui.href_to(self)
        if self.person:
            if self.company:
                s += ": " + ui.href_to(self.person) + " / " + ui.href_to(self.company)
            else:
                s += ": " + ui.href_to(self.person)
        elif self.company:
            s += ": " + ui.href_to(self.company)
        return s
        
    def __unicode__(self):
        return unicode(self.seqno)
        #~ return unicode(self.get_partner())
        
class Thirds(reports.Report):
    model = Third
    #~ order_by = ["modified"]
    column_names = "owner_type owner_id seqno person company *"
    

class ThirdsByOwner(Thirds):
    fk_name = 'owner'
    column_names = "seqno person company id"
    show_slave_grid = False
    
    
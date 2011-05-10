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


import datetime
#~ import logging
#~ logger = logging.getLogger(__name__)

#~ from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _


from lino import reports
from lino.core import actors
from lino.mixins import printable
#~ from lino.utils import perms
from lino.utils import dblogger



class User(models.Model):
    """
    Represents a User of this site.
    
    This version of the Users table is used on Lino sites with
    :doc:`/topics/http_auth`. 
    
    Only username is required. Other fields are optional.
    
    There is no password field since Lino is not responsible for authentication.
    New users are automatically created in this table when 
    Lino gets a first request with a username that doesn't yet exist.
    It is up to the local system administrator to manually fill then 
    fields like first_name, last_name, email, access rights for the new user.    
    """
    username = models.CharField(_('username'), max_length=30, 
        unique=True, 
        help_text=_("""
        Required. 30 characters or fewer. 
        Letters, numbers and @/./+/-/_ characters
        """))
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('e-mail address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False, 
        help_text=_("""
        Designates whether the user can log into this admin site.
        """))
    is_active = models.BooleanField(_('active'), default=True, 
        help_text=_("""
        Designates whether this user should be treated as active. 
        Unselect this instead of deleting accounts.
        """))
    is_superuser = models.BooleanField(_('superuser status'), 
        default=False, 
        help_text=_("""
        Designates that this user has all permissions without 
        explicitly assigning them.
        """))
    last_login = models.DateTimeField(_('last login'), default=datetime.datetime.now)
    date_joined = models.DateTimeField(_('date joined'), default=datetime.datetime.now)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __unicode__(self):
        return self.username

    def get_full_name(self):
        "Returns the first_name plus the last_name, with a space in between."
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()


    def email_user(self, subject, message, from_email=None):
        "Sends an e-mail to this User."
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email])


class Users(reports.Report):
    """Shows the list of users on this site.
    """
    model = User
    #~ order_by = "last_name first_name".split()
    order_by = ["username"]
    column_names = 'username first_name last_name is_active id is_superuser is_staff last_login date_joined'

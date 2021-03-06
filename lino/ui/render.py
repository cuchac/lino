# -*- coding: UTF-8 -*-
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

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.utils.encoding import force_unicode

from django.utils.translation import ugettext as _
from django.utils.translation import get_language

from lino.core import constants as ext_requests

from lino.utils.xmlgen.html import E

if False:
    from lino.utils.jscompressor import JSCompressor
    jscompress = JSCompressor().compress
else:
    def jscompress(s):
        return s


def add_user_language(kw, ar):
    if len(settings.SITE.languages) == 1:
        return
    u = ar.get_user()
    lang = get_language()
    #~ print 2013115, [li.django_code for li in settings.SITE.languages], settings.SITE.get_default_language(), lang, u.language
    if u and u.language and lang != u.language:
        kw.setdefault(ext_requests.URL_PARAM_USER_LANGUAGE, lang)
    #~ elif lang != settings.SITE.DEFAULT_LANGUAGE.django_code:
    elif lang != settings.SITE.get_default_language():
        kw.setdefault(ext_requests.URL_PARAM_USER_LANGUAGE, lang)


    #~ if len(settings.SITE.languages) > 1:
      #~
        #~ ul = rqdata.get(constants.URL_PARAM_USER_LANGUAGE,None)
        #~ if ul:
            #~ translation.activate(ul)
            #~ request.LANGUAGE_CODE = translation.get_language()


class NOT_GIVEN:
    pass


class HtmlRenderer(object):

    """
    Deserves more documentation.
    """
    is_interactive = False
    row_classes_map = {}

    def __init__(self, plugin):
        self.plugin = plugin
        # self.ui = plugin.site.ui

    def href(self, url, text):
        #~ return '<a href="%s">%s</a>' % (url,text)
        return E.a(text, href=url)

    def show_request(self, ar, **kw):
        """
        Returns a HTML element representing this request as a table.
        """
        #~ return ar.table2xhtml(**kw)
        return E.tostring(ar.table2xhtml(**kw))

    def href_button_action(
            self, ba, url, text=None, title=None, icon_name=NOT_GIVEN, **kw):
        """
        changed 20130905 for "Must read eID card button"
        but that caused icons to not appear in workflow_buttons.
        """
        if icon_name is NOT_GIVEN:
            icon_name = ba.action.icon_name
        if icon_name is not None and not kw.has_key('style'):
            kw.update(style="vertical-align:-30%;")
        return self.href_button(url, text, title, icon_name=icon_name, **kw)

    def href_button(self, url, text, title=None, target=None, icon_name=None, **kw):
        """
        Returns an etree object of a "button-like" ``<a href>`` tag.
        """
        #~ logger.info('20121002 href_button %r',unicode(text))
        if target:
            kw.update(target=target)
        if title:
            # Remember that Python 2.6 doesn't like if title is a Promise
            kw.update(title=unicode(title))
            #~ return xghtml.E.a(text,href=url,title=title)
        kw.update(href=url)
        #~ if icon_name:
        if icon_name is not None:
            #~ btn = xghtml.E.button(type='button',class_='x-btn-text '+icon_name)
            #~ btn = xghtml.E.button(
                #~ type='button',
                #~ class_='x-btn-text '+icon_name,
                #~ onclick='function() {console.log(20121024)}')
            #~ return btn
            #~ return xghtml.E.a(btn,**kw)
            #~ kw.update(class_='x-btn-text '+icon_name)
            img = E.img(src=settings.SITE.build_media_url(
                'lino', 'extjs', 'images', 'mjames', icon_name + '.png'))
            return E.a(img, **kw)
        else:
            #~ return E.span('[',xghtml.E.a(text,**kw),']')
            #~ kw.update(style='border-width:1px; border-color:black; border-style:solid;')
            return E.a(text, **kw)

    def quick_add_buttons(self, ar):
        """
        Returns a HTML chunk that displays "quick add buttons"
        for the given :class:`action request <lino.core.dbtables.TableRequest>`:
        a button  :guilabel:`[New]` followed possibly 
        (if the request has rows) by a :guilabel:`[Show last]` 
        and a :guilabel:`[Show all]` button.
        
        See also :doc:`/tickets/56`.
        
        """
        buttons = []
        btn = ar.insert_button(_("New"))
        if btn is not None:
            buttons.append(btn)
            buttons.append(' ')
                #~ after_show = ar.get_status()
        n = ar.get_total_count()
        #~ print 20120702, [o for o in ar]
        if n > 0:
            obj = ar.data_iterator[n - 1]
            st = ar.get_status()
            st.update(record_id=obj.pk)
            #~ a = ar.actor.get_url_action('detail_action')
            a = ar.actor.detail_action
            buttons.append(self.window_action_button(
                ar.request, a, st, _("Show Last"),
                icon_name='application_form',
                title=_("Show the last record in a detail window")))
            buttons.append(' ')
            #~ s += ' ' + self.window_action_button(
                #~ ar.ah.actor.detail_action,after_show,_("Show Last"))
            #~ s += ' ' + self.href_to_request(ar,"[%s]" % unicode(_("Show All")))
            buttons.append(self.href_to_request(None, ar,
                                                _("Show All"),
                                                icon_name='application_view_list',
                                                title=_("Show all records in a table window")))
        #~ return '<p>%s</p>' % s
        return E.p(*buttons)

    def obj2html(self, ar, obj, text=None):
        if text is None:
            text = (force_unicode(obj),)
        elif isinstance(text, basestring):
            text = (text,)
        if self.is_interactive:
            url = self.instance_handler(ar, obj)
            if url is not None:
                return E.a(*text, href=url)
        return E.b(*text)

    def quick_upload_buttons(self, rr):
        return '[?!]'

    def insert_button(self, ar, text, known_values={}, **options):
        return '[?!]'

    def row_action_button(self, obj, request, ba,
                          label=None, title=None, **kw):
        return '[?!]'

    def href_to_request(self, sar, tar, text=None, **kw):
        return '[?!]'
        
    def window_action_button(
            self, request, ba,
            after_show={}, label=None, title=None, **kw):
        """
        Return a HTML chunk for a button that will execute this action.
        """
        label = unicode(label or ba.get_button_label())
        url = 'javascript:' + self.action_call(request, ba, after_show)
        #~ logger.info('20121002 window_action_button %s %r',a,unicode(label))
        return self.href_button_action(ba, url, label,
                                       title or ba.action.help_text, **kw)


class TextRenderer(HtmlRenderer):

    "The renderer used when rendering to .rst files and console output."
    user = None

    def __init__(self, *args, **kw):
        HtmlRenderer.__init__(self,  *args, **kw)
        self.user = None

    def instance_handler(self, ar, obj):
        return None

    def pk2url(self, ar, pk, **kw):
        return None

    def get_request_url(self, ar, *args, **kw):
        return None

    def href_to_request(self, sar, tar, text=None):
        if text is None:
            text = '#'
        return text

    def show_request(self, ar, *args, **kw):
        """
        Returns a string representing this request in reStructuredText markup.
        """
        print(ar.to_rst(*args, **kw))



# -*- coding: UTF-8 -*-
# Copyright 2011-2014 Luc Saffre
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
Part of the :xfile:`models.py` module for the :mod:`lino.modlib.cal` app.

Defines the :class:`EventType` and :class:`Event` models and their tables.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext

from lino import mixins
from lino import dd

from .utils import (
    Recurrencies,
    when_text,
    AccessClasses)


from .mixins import Ended
from .mixins import RecurrenceSet, EventGenerator
from .mixins import UpdateEvents
from .mixins import MoveEventNext
from .models import Component
from .models import Priority
from .workflows import EventStates

contacts = dd.resolve_app('contacts')
postings = dd.resolve_app('postings')
outbox = dd.resolve_app('outbox')


def daterange_text(a, b):
    if a == b:
        return a.strftime(settings.SITE.date_format_strftime)
    d = dict(min="...", max="...")
    if a:
        d.update(min=a.strftime(settings.SITE.date_format_strftime))
    if b:
        d.update(max=b.strftime(settings.SITE.date_format_strftime))
    return _("Dates %(min)s to %(max)s") % d


class EventType(dd.BabelNamed, dd.Sequenced,
                dd.PrintableType, outbox.MailableType):

    """
    An EventType is a collection of events and tasks.
    """

    templates_group = 'cal/Event'

    class Meta:
        abstract = settings.SITE.is_abstract_model('cal.EventType')
        verbose_name = _("Event Type")
        verbose_name_plural = _("Event Types")
        ordering = ['seqno']

    #~ name = models.CharField(_("Name"),max_length=200)
    description = dd.RichTextField(_("Description"), blank=True, format='html')
    is_appointment = models.BooleanField(
        _("Event is an appointment"), default=True)
    all_rooms = models.BooleanField(_("Locks all rooms"), default=False)
    locks_user = models.BooleanField(
        _("Locks the user"),
        help_text=_(
            "Lino won't not accept more than one locking event per user at the same time."),
        default=False)
    #~ is_default = models.BooleanField(
        #~ _("is default"),default=False)
    #~ is_private = models.BooleanField(
        #~ _("private"),default=False,help_text=_("""\
#~ Whether other users may subscribe to this EventType."""))
    start_date = models.DateField(
        verbose_name=_("Start date"),
        blank=True, null=True)
    event_label = dd.BabelCharField(
        _("Event label"),
        max_length=200, blank=True, default=_("Appointment"))

    #~ def full_clean(self,*args,**kw):
        #~ if not self.name:
            #~ if self.username:
                #~ self.name = self.username
            #~ elif self.user is None:
                #~ self.name = "Anonymous"
            #~ else:
                #~ self.name = self.user.get_full_name()
        #~ super(EventType,self).full_clean(*args,**kw)


    #~ def __unicode__(self):
        #~ return self.name

    #~ def color(self,request):
        #~ return settings.SITE.get_calendar_color(self,request)
    #~ color.return_type = models.IntegerField(_("Color"))


class EventTypes(dd.Table):
    help_text = _("""The list of Event Types defined on this system.
    An EventType is a list of events which have certain things in common,
    especially they are displayed in the same colour in the calendar panel""")
    required = dd.required(user_groups='office', user_level='manager')
    model = 'cal.EventType'
    column_names = "name build_method template *"

    detail_layout = """
    name 
    event_label
    # description
    start_date id 
    # type url_template username password
    build_method template email_template attach_to_email
    is_appointment all_rooms locks_user
    EventsByType 
    """

    insert_layout = dd.FormLayout("""
    name 
    event_label 
    """, window_size=(60, 'auto'))

#~ def default_calendar(user):
    #~ """
    #~ Returns or creates the default calendar for the given user.
    #~ """
    #~ try:
        #~ return Calendar.objects.get(user=user,is_default=True)
    #~ except Calendar.DoesNotExist,e:
        #~ color = Calendar.objects.all().count() + 1
        #~ while color > 32:
            #~ color -= 32
        #~ cal = Calendar(user=user,is_default=True,color=color)
        #~ cal.full_clean()
        #~ cal.save()
        #~ logger.debug(u"Created default calendar for %s.",user)
        #~ return cal


#~ class EventType(mixins.PrintableType,outbox.MailableType,dd.BabelNamed):
    #~ """The type of an Event.
    #~ Determines which build method and template to be used for printing the event.
    #~ """
    #~ templates_group = 'cal/Event'
    #~ class Meta:
        #~ verbose_name = pgettext(u"cal",u"Event Type")
        #~ verbose_name_plural = pgettext(u"cal",u'Event Types')
#~ class EventTypes(dd.Table):
    #~ model = EventType
    #~ required = dict(user_groups='office')
    #~ column_names = 'name build_method template *'
    #~ detail_layout = """
    #~ id name
    #~ build_method template email_template attach_to_email
    #~ cal.EventsByType
    #~ """
#~ class AutoEvent(object):
    #~ def __init__(self,auto_id,user,date,subject,owner,start_time,end_time):
        #~ self.auto_id = auto_id
        #~ self.user = user
        #~ self.date = date
        #~ self.subject = subject
        #~ self.owner = owner
        #~ self.start_time = start_time
        #~ self.end_time = end_time


class RecurrentEvent(dd.BabelNamed, RecurrenceSet, EventGenerator):

    """
    An event that recurs at intervals.
    """

    class Meta:
        verbose_name = _("Recurrent Event")
        verbose_name_plural = _("Recurrent Events")

    event_type = models.ForeignKey('cal.EventType', blank=True, null=True)
    # ~ summary = models.CharField(_("Summary"),max_length=200,blank=True) # iCal:SUMMARY
    description = dd.RichTextField(_("Description"), blank=True, format='html')

    #~ def on_create(self,ar):
        #~ super(RecurrentEvent,self).on_create(ar)
        #~ self.event_type = settings.SITE.site_config.holiday_event_type

    #~ def __unicode__(self):
        #~ return self.summary

    def update_cal_rset(self):
        return self

    def update_cal_from(self, ar):
        return self.start_date

    def update_cal_calendar(self):
        return self.event_type

    def update_cal_summary(self, i):
        return unicode(self)

dd.update_field(
    RecurrentEvent, 'every_unit',
    default=Recurrencies.yearly)


class RecurrentEvents(dd.Table):

    """
    The list of all :class:`Recurrence Sets <RecurrenceSet>`.
    """
    model = 'cal.RecurrentEvent'
    required = dd.required(user_groups='office', user_level='manager')
    column_names = "start_date end_date name every_unit event_type *"
    auto_fit_column_widths = True
    order_by = ['start_date']

    insert_layout = """
    start_date every_unit event_type
    name
    """

    detail_layout = """
    id user event_type name
    start_date start_time  end_date end_time
    max_events every_unit every
    monday tuesday wednesday thursday friday saturday sunday
    description cal.EventsByController
    """


class ExtAllDayField(dd.VirtualField):

    """
    An editable virtual field needed for 
    communication with the Ext.ensible CalendarPanel
    because we consider the "all day" checkbox 
    equivalent to "empty start and end time fields".
    """

    editable = True

    def __init__(self, *args, **kw):
        dd.VirtualField.__init__(self, models.BooleanField(*args, **kw), None)

    def set_value_in_object(self, request, obj, value):
        if value:
            obj.end_time = None
            obj.start_time = None
        else:
            if not obj.start_time:
                obj.start_time = datetime.time(9, 0, 0)
            if not obj.end_time:
                obj.end_time = datetime.time(10, 0, 0)
        #~ obj.save()

    def value_from_object(self, obj, ar):
        #~ logger.info("20120118 value_from_object() %s",dd.obj2str(obj))
        return (obj.start_time is None)

# ~ from lino.modlib.workflows import models as workflows # Workflowable

#~ class Components(dd.Table):
# ~ # class Components(dd.Table,workflows.Workflowable):

    #~ workflow_owner_field = 'user'
    #~ workflow_state_field = 'state'

    #~ def disable_editing(self,request):
    #~ def get_row_permission(cls,row,user,action):
        #~ if row.rset: return False

    #~ @classmethod
    #~ def get_row_permission(cls,action,user,row):
        #~ if not action.readonly:
            #~ if row.user != user and user.level < UserLevel.manager:
                #~ return False
        #~ if not super(Components,cls).get_row_permission(action,user,row):
            #~ return False
        #~ return True


class Event(Component, Ended,
            mixins.TypedPrintable,
            outbox.Mailable,
            postings.Postable):

    """A Calendar Event (french "Rendez-vous", german "Termin") is a
    planned ("scheduled") lapse of time where something happens.

    """

    class Meta:
        abstract = settings.SITE.is_abstract_model('cal.Event')
        #~ abstract = True
        verbose_name = pgettext(u"cal", u"Event")
        verbose_name_plural = pgettext(u"cal", u"Events")

    event_type = models.ForeignKey('cal.EventType', blank=True, null=True)

    transparent = models.BooleanField(
        _("Transparent"), default=False, help_text=_("""\
Indicates that this Event shouldn't prevent other Events at the same time."""))
    room = dd.ForeignKey('cal.Room', null=True, blank=True)  # iCal:LOCATION
    priority = models.ForeignKey(Priority, null=True, blank=True)
    state = EventStates.field(default=EventStates.suggested)  # iCal:STATUS
    all_day = ExtAllDayField(_("all day"))

    assigned_to = dd.ForeignKey(
        settings.SITE.user_model,
        verbose_name=_("Assigned to"),
        related_name="cal_events_assigned",
        blank=True, null=True)

    move_next = MoveEventNext()

    def has_conflicting_events(self):
        qs = self.get_conflicting_events()
        if qs is None:
            return False
        return qs.count() > 0

    def __unicode__(self):
        if self.pk:
            s = self._meta.verbose_name + " #" + str(self.pk)
        else:
            s = _("Unsaved %s") % self._meta.verbose_name
        if self.summary:
            s += " " + self.summary
        if self.start_date:
            d = self.start_date.strftime(settings.SITE.date_format_strftime)
            if self.start_time:
                t = self.start_time.strftime(
                    settings.SITE.time_format_strftime)
                s += " (%s %s)" % (d, t)
            else:
                s += " (%s)" % d
        return s

    #~ def conflicts_with_existing(self):
    def get_conflicting_events(self):
        """
        Return a QuerySet of Events that conflict with this one.
        Must work also when called on an unsaved instance.
        May return None to indicate an empty queryset.
        Applications may override this to add specific conditions.
        """
        if self.transparent:
            return
        #~ return False
        #~ Event = dd.resolve_model('cal.Event')
        #~ ot = ContentType.objects.get_for_model(RecurrentEvent)
        qs = self.__class__.objects.filter(transparent=False)
        end_date = self.end_date or self.start_date
        flt = Q(start_date=self.start_date, end_date__isnull=True)
        flt |= Q(end_date__isnull=False,
                 start_date__lte=self.start_date, end_date__gte=end_date)
        if end_date == self.start_date:
            if self.start_time and self.end_time:
                # the other starts before me and ends after i started
                c1 = Q(start_time__lte=self.start_time,
                       end_time__gt=self.start_time)
                # the other ends after me and started before i ended
                c2 = Q(end_time__gte=self.end_time,
                       start_time__lt=self.end_time)
                # the other is full day
                c3 = Q(end_time__isnull=True, start_time__isnull=True)
                flt &= (c1 | c2 | c3)
        qs = qs.filter(flt)
        if self.id is not None:  # don't conflict with myself
            qs = qs.exclude(id=self.id)
        # generated events never conflict with other generated events of same owner. Rule needed for update_events.
        if self.auto_type is not None:
            qs = qs.exclude(
                # auto_type=self.auto_type,
                owner_id=self.owner_id, owner_type=self.owner_type)
        if self.room is not None:
            # other event in the same room
            c1 = Q(room=self.room)
            # other event locks all rooms (e.h. holidays)
            c2 = Q(event_type__all_rooms=True)
            qs = qs.filter(c1 | c2)
        if self.user is not None:
            if self.event_type is not None:
                if self.event_type.locks_user:
                    #~ c1 = Q(event_type__locks_user=False)
                    #~ c2 = Q(user=self.user)
                    #~ qs = qs.filter(c1|c2)
                    qs = qs.filter(user=self.user, event_type__locks_user=True)
        #~ qs = Event.objects.filter(flt,owner_type=ot)
        #~ if we.start_date.month == 7:
            #~ print 20131011, self, we.start_date, qs.count()
        #~ print 20131025, qs.query
        return qs

    def is_fixed_state(self):
        return self.state.fixed
        #~ return self.state in EventStates.editable_states

    def is_user_modified(self):
        return self.state != EventStates.suggested

    def save(self, *args, **kw):
        r = super(Event, self).save(*args, **kw)
        self.add_guests()
        #~ """
        #~ The following hack removes this event from the series of
        #~ automatically generated events so that the Generator re-creates
        #~ a new one.
        #~ """
        #~ if self.state == EventStates.cancelled:
            #~ self.auto_type = None
        return r

    def add_guests(self):
        """
        Decide whether it is time to add Guest instances for this event,
        and if yes, call :meth:`suggest_guests` to instantiate them.
        """
        #~ print "20130722 Event.save"
        #~ print "20130717 add_guests"
        if settings.SITE.loading_from_dump:
            return
        if not self.is_user_modified():
            #~ print "not is_user_modified"
            return
        if not self.state.edit_guests:
        #~ if not self.state in (EventStates.suggested, EventStates.draft):
        #~ if self.is_fixed_state():
            #~ print "is a fixed state"
            return
        if self.guest_set.all().count() > 0:
            #~ print "guest_set not empty"
            return
        for g in self.suggest_guests():
            g.save()
            #~ settings.SITE.modules.cal.Guest(event=self,partner=p).save()

    def suggest_guests(self):
        """
        Yield a list of Partner instances to be invited to this Event.
        This method is called when :meth:`add_guests` decided so.
        """
        return []

    def get_event_summary(event, ar):
        """
        How this event should be summarized in contexts 
        where possibly another user is looking 
        (i.e. currently in invitations of guests, or in the extensible calendar 
        panel).
        """
        #~ from django.utils.translation import ugettext as _
        s = event.summary
        if event.user != ar.get_user():
            if event.access_class == AccessClasses.show_busy:
                s = _("Busy")
            s = event.user.username + ': ' + unicode(s)
        elif settings.SITE.project_model is not None \
                and event.project is not None:
            s += " " + unicode(_("with")) + " " + unicode(event.project)
        if event.state:
            s = ("(%s) " % unicode(event.state)) + s
        n = event.guest_set.all().count()
        if n:
            s = ("[%d] " % n) + s
        return s

    def before_ui_save(self, ar, **kw):
        """
        Mark the event as "user modified" by setting a default state.
        This is important because EventGenerators may not modify any user-modified Events.
        """
        #~ logger.info("20130528 before_ui_save")
        if self.state is EventStates.suggested:
            self.state = EventStates.draft
        return super(Event, self).before_ui_save(ar, **kw)

    def on_create(self, ar):
        self.event_type = ar.user.event_type or settings.SITE.site_config.default_event_type
        self.start_date = datetime.date.today()
        self.start_time = datetime.datetime.now().time()
        # 20130722 e.g. CreateClientEvent sets it explicitly
        if self.assigned_to is None:
            self.assigned_to = ar.subst_user
        super(Event, self).on_create(ar)

    #~ def on_create(self,ar):
        #~ self.start_date = datetime.date.today()
        #~ self.start_time = datetime.datetime.now().time()
        # ~ # default user is almost the same as for UserAuthored
        # ~ # but we take the *real* user, not the "working as"
        #~ if self.user_id is None:
            #~ u = ar.user
            #~ if u is not None:
                #~ self.user = u
        #~ super(Event,self).on_create(ar)

    def get_postable_recipients(self):
        """return or yield a list of Partners"""
        if settings.SITE.is_installed('contacts') and issubclass(settings.SITE.project_model, contacts.Partner):
            if self.project:
                yield self.project
        for g in self.guest_set.all():
            yield g.partner
        #~ if self.user.partner:
            #~ yield self.user.partner

    def get_mailable_type(self):
        return self.event_type

    def get_mailable_recipients(self):
        if settings.SITE.is_installed('contacts') and issubclass(settings.SITE.project_model, contacts.Partner):
            if self.project:
                yield ('to', self.project)
        for g in self.guest_set.all():
            yield ('to', g.partner)
        if self.user.partner:
            yield ('cc', self.user.partner)

    #~ def get_mailable_body(self,ar):
        #~ return self.description

    def get_system_note_recipients(self, ar, silent):
        if self.user != ar.user:
            yield "%s <%s>" % (unicode(self.user), self.user.email)
        if silent:
            return
        for g in self.guest_set.all():
            if g.partner.email:
                yield "%s <%s>" % (unicode(g.partner), g.partner.email)

    @dd.displayfield(_("When"))
    def when_text(self, ar):
        assert ar is not None
        #~ print 20130802, ar.renderer
        #~ raise foo
        #~ txt = when_text(self.start_date)
        txt = when_text(self.start_date, self.start_time)
        #~ return txt
        #~ logger.info("20130802a when_text %r",txt)
        return ar.obj2html(self, txt)
        #~ try:
            #~ e = ar.obj2html(self,txt)
        #~ except Exception,e:
            #~ import traceback
            #~ traceback.print_exc(e)
        #~ logger.info("20130802b when_text %r",E.tostring(e))
        #~ return e

    @dd.displayfield(_("Link URL"))
    def url(self, ar):
        return 'foo'

    @dd.displayfield(_("Date"))
    def linked_date(self, ar):
        pv = dict(start_date=self.start_date)
        if False:
            # TODO: what to do in case of multiple day events?
            pv.update(end_date=self.end_date or self.start_date)
        else:
            pv.update(end_date=self.start_date)
        target = ar.spawn('cal.EventsByDay', param_values=pv)
        txt = self.start_date.strftime(settings.SITE.date_format_strftime)
        return ar.href_to_request(target, txt)

    @dd.virtualfield(dd.DisplayField(_("Reminder")))
    def reminder(self, request):
        return False
    #~ reminder.return_type = dd.DisplayField(_("Reminder"))

    def get_calendar(self):
        """
        Returns the Calendar which contains this event,
        or None if no subscription is found.
        Needed for ext.ensible calendar panel.

        The default implementation returns None.
        Override this if your app uses Calendars.
        """
        #~ for sub in Subscription.objects.filter(user=ar.get_user()):
            #~ if sub.contains_event(self):
                #~ return sub
        return None

    @dd.virtualfield(models.ForeignKey('cal.Calendar'))
    def calendar(self, ar):
        return self.get_calendar()

    def get_print_language(self):
        if settings.SITE.project_model is not None and self.project:
            return self.project.get_print_language()
        return self.user.language

    @classmethod
    def get_default_table(cls):
        return OneEvent

    @classmethod
    def on_analyze(cls, lino):
        cls.DISABLED_AUTO_FIELDS = dd.fields_list(cls,
            '''summary''')


dd.update_field(Event, 'user', verbose_name=_("Responsible user"))


class EventDetail(dd.FormLayout):
    start = "start_date start_time"
    end = "end_date end_time"
    main = """
    event_type summary user assigned_to
    start end #all_day #duration state
    room priority access_class transparent #rset 
    owner created:20 modified:20  
    description
    GuestsByEvent outbox.MailsByController
    """


class EventInsert(EventDetail):
    main = """
    event_type summary 
    start end 
    room priority access_class transparent 
    """

class EventEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
add = EventEvents.add_item
add('10', _("Okay"), 'okay')
add('20', _("Pending"), 'pending')


class Events(dd.Table):
    help_text = _("A List of calendar entries. Each entry is called an event.")
    model = 'cal.Event'
    required = dd.required(user_groups='office', user_level='manager')
    column_names = 'when_text:20 user summary event_type *'

    # hidden_columns = """
    # priority access_class transparent
    # owner created modified
    # description
    # sequence auto_type build_time owner owner_id owner_type
    # end_date end_time
    # """

    #~ active_fields = ['all_day']
    order_by = ["start_date", "start_time"]

    detail_layout = EventDetail()
    insert_layout = EventInsert()

    params_panel_hidden = True

    parameters = dd.ObservedPeriod(
        user=dd.ForeignKey(settings.SITE.user_model,
                           verbose_name=_("Managed by"),
                           blank=True, null=True,
                           help_text=_("Only rows managed by this user.")),
        project=dd.ForeignKey(settings.SITE.project_model,
                              blank=True, null=True),
        event_type=dd.ForeignKey('cal.EventType', blank=True, null=True),
        assigned_to=dd.ForeignKey(settings.SITE.user_model,
                                  verbose_name=_("Assigned to"),
                                  blank=True, null=True,
                                  help_text=_(
                                      "Only events assigned to this user.")),
        state=EventStates.field(blank=True,
                                help_text=_("Only rows having this state.")),
        #~ unclear = models.BooleanField(_("Unclear events"))
        observed_event=EventEvents.field(blank=True),
        show_appointments=dd.YesNo.field(_("Appointments"), blank=True),
    )

    params_layout = """
    start_date end_date observed_event state 
    user assigned_to project event_type show_appointments
    """
    #~ params_layout = dd.Panel("""
    #~ start_date end_date other
    #~ """,other="""
    #~ user
    #~ assigned_to
    #~ state
    #~ """)

    # ~ next = NextDateAction() # doesn't yet work. 20121203

    fixed_states = set(EventStates.filter(fixed=True))
    #~ pending_states = set([es for es in EventStates if not es.fixed])
    pending_states = set(EventStates.filter(fixed=False))

    @classmethod
    def get_request_queryset(self, ar):
        #~ logger.info("20121010 Clients.get_request_queryset %s",ar.param_values)
        qs = super(Events, self).get_request_queryset(ar)

        if ar.param_values.user:
            #~ if ar.param_values.assigned_to:
                #~ qs = qs.filter(Q(assigned_to=ar.param_values.assigned_to)|Q(user=ar.param_values.user))
            #~ else:
            qs = qs.filter(user=ar.param_values.user)
        if ar.param_values.assigned_to:
            qs = qs.filter(assigned_to=ar.param_values.assigned_to)

        if settings.SITE.project_model is not None and ar.param_values.project:
            qs = qs.filter(project=ar.param_values.project)

        if ar.param_values.event_type:
            qs = qs.filter(event_type=ar.param_values.event_type)
        else:
            if ar.param_values.show_appointments == dd.YesNo.yes:
                qs = qs.filter(event_type__is_appointment=True)
            elif ar.param_values.show_appointments == dd.YesNo.no:
                qs = qs.filter(event_type__is_appointment=False)

        if ar.param_values.state:
            qs = qs.filter(state=ar.param_values.state)

        #~ if ar.param_values.observed_event:
        if ar.param_values.observed_event == EventEvents.okay:
            qs = qs.filter(state__in=self.fixed_states)
        elif ar.param_values.observed_event == EventEvents.pending:
            qs = qs.filter(state__in=self.pending_states)

        if ar.param_values.start_date:
            qs = qs.filter(start_date__gte=ar.param_values.start_date)
            #~ if ar.param_values.end_date:
                #~ qs = qs.filter(start_date__gte=ar.param_values.start_date)
            #~ else:
                #~ qs = qs.filter(start_date=ar.param_values.start_date)
        if ar.param_values.end_date:
            qs = qs.filter(start_date__lte=ar.param_values.end_date)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Events, self).get_title_tags(ar):
            yield t
        if ar.param_values.start_date or ar.param_values.end_date:
            yield daterange_text(
                ar.param_values.start_date,
                ar.param_values.end_date)

        if ar.param_values.state:
            yield unicode(ar.param_values.state)

        if ar.param_values.event_type:
            yield unicode(ar.param_values.event_type)

        if ar.param_values.user:
            yield unicode(ar.param_values.user)

        if settings.SITE.project_model is not None and ar.param_values.project:
            yield unicode(ar.param_values.project)

        if ar.param_values.assigned_to:
            yield unicode(self.parameters['assigned_to'].verbose_name) \
                + ' ' + unicode(ar.param_values.assigned_to)

    @classmethod
    def apply_cell_format(self, ar, row, col, recno, td):
        """
        Enhance today by making background color a bit darker.
        """
        if row.start_date == datetime.date.today():
            td.attrib.update(bgcolor="#bbbbbb")


class EventsByType(Events):
    master_key = 'event_type'


class EventsByDay(Events):
    column_names = 'room summary workflow_buttons *'
    auto_fit_column_widths = True

#~ class EventsByType(Events):
    #~ master_key = 'type'

#~ class EventsByPartner(Events):
    #~ required = dd.required(user_groups='office')
    #~ master_key = 'user'


class EventsByRoom(Events):

    """
    Displays the :class:`Events <Event>` at a given :class:`Room`.
    """
    master_key = 'room'


class EventsByController(Events):
    required = dd.required(user_groups='office')
    master_key = 'owner'
    column_names = 'when_text:20 summary workflow_buttons *'
    auto_fit_column_widths = True

if settings.SITE.project_model:

    class EventsByProject(Events):
        required = dd.required(user_groups='office')
        master_key = 'project'
        auto_fit_column_widths = True
        column_names = 'when_text user summary workflow_buttons'


class OneEvent(Events):
    show_detail_navigator = False
    use_as_default_table = False
    required = dd.required(user_groups='office')

if settings.SITE.user_model:

    class MyEvents(Events):
        label = _("My events")
        help_text = _("Table of all my calendar events.")
        required = dd.required(user_groups='office')
        column_names = 'when_text summary workflow_buttons project *'

        @classmethod
        def param_defaults(self, ar, **kw):
            kw = super(MyEvents, self).param_defaults(ar, **kw)
            kw.update(user=ar.get_user())
            kw.update(show_appointments=dd.YesNo.yes)
            #~ kw.update(assigned_to=ar.get_user())
            #~ logger.info("20130807 %s %s",self,kw)
            kw.update(start_date=datetime.date.today())
            return kw

        @classmethod
        def create_instance(self, ar, **kw):
            kw.update(start_date=ar.param_values.start_date)
            return super(MyEvents, self).create_instance(ar, **kw)

    #~ class MyUnclearEvents(MyEvents):
        #~ label = _("My unclear events")
        #~ help_text = _("Events which probably need your attention.")
        #~
        #~ @classmethod
        #~ def param_defaults(self,ar,**kw):
            #~ kw = super(MyUnclearEvents,self).param_defaults(ar,**kw)
            #~ kw.update(observed_event=EventEvents.pending)
            #~ kw.update(start_date=datetime.date.today())
            #~ kw.update(end_date=datetime.date.today()+ONE_DAY)
            #~ return kw
    class MyAssignedEvents(MyEvents):
        label = _("Events assigned to me")
        help_text = _("Table of events assigned to me.")
        #~ master_key = 'assigned_to'
        required = dd.required(user_groups='office')
        #~ column_names = 'when_text:20 project summary workflow_buttons *'
        #~ known_values = dict(assigned_to=EventStates.assigned)

        @classmethod
        def param_defaults(self, ar, **kw):
            kw = super(MyAssignedEvents, self).param_defaults(ar, **kw)
            kw.update(user=None)
            kw.update(assigned_to=ar.get_user())
            return kw


def update_reminders_for_user(user, ar):
    n = 0
    for model in dd.models_by_base(EventGenerator):
        for obj in model.objects.filter(user=user):
            obj.update_reminders(ar)
            #~ logger.info("--> %s",unicode(obj))
            n += 1
    return n


class UpdateUserReminders(UpdateEvents):

    """
    Users can invoke this to re-generate their automatic tasks.
    """

    def run_from_ui(self, ar, **kw):
        user = ar.selected_rows[0]
        logger.info("Updating reminders for %s", unicode(user))
        n = update_reminders_for_user(user, ar)
        #~ ar.response.update(success=True)
        msg = _("%(num)d reminders for %(user)s have been updated."
                ) % dict(user=user, num=n)
        logger.info(msg)
        ar.success(msg, **kw)


@dd.receiver(dd.pre_analyze, dispatch_uid="add_update_reminders")
def pre_analyze(sender, **kw):
    #~ logger.info("%s.set_merge_actions()",__name__)
    #~ modules = sender.modules
    sender.user_model.add_model_action(update_reminders=UpdateUserReminders())


__all__ = [
    'UpdateEvents',
    'Event', 'Events',
    'EventType', 'EventTypes']

# -*- coding: UTF-8 -*-
# Copyright 2002-2014 Luc Saffre
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

"""This defines the :class:`Site` class.  It has a lot of class
attributes which may be overridden by the application developer and/or
the local site administrator.

Here is a list of Lino-specific settings.  The settings inherited
:class:`north.north_site.Site` and :class:`djangosite.Site` are
documented there.

.. setting:: config_id

The primary key of the one and only `SiteConfig` instance of this
SITE. Default value is 1.

This is Lino's equivalent of Django's :setting:`SITE_ID` setting.
Lino applications don't need ``django.contrib.sites`` (`The "sites"
framework
<https://docs.djangoproject.com/en/dev/ref/contrib/sites/>`_) because
this functionality is integral part of :mod:`lino.modlib.system`.

.. setting:: verbose_client_info_message

Set this to True if actions should send debug messages to the client.
These will be shown in the client's Javascript console only.


.. setting:: demo_fixtures

The list of fixtures to be loaded by the :manage:`initdb_demo`
command.

.. setting:: use_davlink

No longer used. Replaced by :class:`lino.modlib.davlink`.

Set this to `True` if this site should feature WebDAV-enabled links
using :ref:`davlink`.

.. setting:: use_eidreader

No longer used. Replaced by :class:`lino.modlib.beid`.

Set this to `True` if this site should feature using :ref:`eidreader`.


.. setting:: auto_configure_logger_names

A string with a space-separated list of logger names to be
automatically configured. See :mod:`lino.utils.log`.

.. setting:: use_java

A site-wide option to disable everything that needs Java.  Note that
it is up to the apps which include Java applications to respect this
setting. Usage example is :mod:`lino.modlib.beid`.

.. setting:: user_model

Most Lino application wil set this to ``"users.User"`` if you use
`lino.modlib.users`.

Default value us `None`, meaning that this site has no user management
(feature used by e.g. :mod:`lino.test_apps.1`)

Set this to ``"auth.User"`` if you use `django.contrib.auth` instead of
`lino.modlib.users` (not tested).


.. setting:: remote_user_header
    
The name of the header (set by the web server) that Lino should
consult for finding the user of a request.  The default value `None`
means that http authentication is not used.  Apache's default value is
``"REMOTE_USER"``.


.. setting:: ldap_auth_server

This should be a string with the domain name and DNS (separated by a
space) of the LDAP server to be used for authentication.  Example::

  ldap_auth_server = 'DOMAIN_NAME SERVER_DNS'
  
.. setting:: auth_middleware

Override used Authorisation middlewares with supplied tuple of
middleware class names.

If None, use logic described in :doc:`/topics/auth`
  


.. setting:: project_model

Deprecated because this is an obsolete pattern.

Optionally set this to the <applabel.ModelName> of a model used as
"central project" in your application.  Which concretely means that
certain other models like notes.Note, outbox.Mail, ... have an
additional ForeignKey to this model.



.. setting:: admin_prefix

The prefix to use for Lino "admin mode"
(i.e. the "admin main page" with a pull-down "main menu").

TODO: convert `admin_prefix` to a `url_prefix` setting on the
`lino.modlib.extjs` plugin.

The default value is an empty string, resulting in a website whose
root url shows the admin mode.

Note that unlike Django's `MEDIA_URL
<https://docs.djangoproject.com/en/dev/ref/settings/#media-url>`__
setting, this must not contain any slash.

If this is nonempty, then your site features a "web content mode": the
root url renders "web content" defined by :mod:`lino.modlib.pages`.
The usual value in that case is ``admin_prefix = "admin"``.

See also

- `telling Django to recognize a different application root url
  <http://groups.google.com/group/django-users/browse_thread/thread/c95ba83e8f666ae5?pli=1>`__
- `How to get site's root path in Django 
  <http://groups.google.com/group/django-users/browse_thread/thread/27f035aa8e566af6>`__
- `#8906 django.contrib.auth settings.py URL's aren't portable <https://code.djangoproject.com/ticket/8906>`__
- `Changed the way URL paths are determined 
  <https://code.djangoproject.com/wiki/BackwardsIncompatibleChanges#ChangedthewayURLpathsaredetermined>`__

.. setting:: plain_prefix

The prefix to use for "plain html" URLs.
Default value is ``'plain'``.

TODO: convert `plain_prefix` to a `url_prefix` setting on the
`lino.modlib.plain` App.

Exactly one of :setting:`admin_prefix` and :setting:`plain_prefix`
must be empty.


.. setting:: preview_limit
    
Default value for the :attr:`preview_limit
<lino.core.tables.AbstractTable.preview_limit>` parameter of all
tables who don't specify their own one.  Default value is 15.


.. setting:: start_year

An integer with the calendar year in which this site starts working.
Used e.g. 
by :mod:`lino.modlib.ledger.utils`
to fill the default list of FixcalYears.
Or by :mod:`lino.modlib.ledger.fixtures.mini`
to generate demo invoices.


.. setting:: setup_choicelists

Redefine application-specific Choice Lists.

Especially used to define application-specific
:class:`UserProfiles <lino.core.perms.UserProfiles>`.

Lino by default has two user profiles "User" and "Administrator",
defined in :mod:`lino.core.perms`.

Application developers who use group-based requirements must override
this in their application's :xfile:`settings.py` to provide a default
list of user profiles for their application.

See the source code of :mod:`lino.projects.presto` or
:mod:`lino_welfare.settings` for a usage example.

Local site administrators may again override this in their
:xfile:`settings.py`.

Note that you may not specify values longer than `max_length` when
redefining your choicelists.  This limitation is because these
redefinitions happen at a moment where database fields have already
been instantiated, so it is too late to change their max_length.  Not
that this limitation is only for the *values*, not for the names or
texts of choices.

.. setting:: get_installed_apps

This method is expected to yield the list of strings
to be stored into Django's :setting:`INSTALLED_APPS` setting.


.. setting:: uppercase_last_name

Whether last name of persons should (by default) be printed with
uppercase letters.  See :mod:`lino.test_apps.human`

"""


from __future__ import unicode_literals

from os.path import join, abspath
import datetime

from urllib import urlencode

from django.utils.translation import ugettext_lazy as _

from north import Site

from lino.utils.xmlgen.html import E


class Site(Site):

    """
    This is the base for every Lino Site.
    """

    config_id = 1

    preview_limit = 15

    default_ui = 'extjs'

    textfield_format = 'plain'
    """
    The default format for text fields.
    Valid choices are currently 'plain' and 'html'.

    Text fields are either Django's `models.TextField`
    or :class:`lino.fields.RichTextField`.

    You'll probably better leave the global option as 'plain',
    and specify explicitly the fields you want as html by declaring
    them::

      foo = fields.RichTextField(...,format='html')

    We even recommend that you declare your *plain* text fields also
    using `fields.RichTextField` and not `models.TextField`::

      foo = fields.RichTextField()

    Because that gives subclasses of your application the possibility to
    make that specific field html-formatted::

       resolve_field('Bar.foo').set_format('html')

    """

    verbose_client_info_message = False

    help_url = "http://code.google.com/p/lino"
    title = "Unnamed Lino site"

    catch_layout_exceptions = True
    """
    Lino usually catches any exception during 
    :meth:`lino.ui.extjs3.ExtUI.create_layout_element`
    to report errors of style 
    "Unknown element "postings.PostingsByController ('postings')" 
    referred in layout <PageDetail on pages.Pages>."
    
    Setting this to `False` is
    useful when there's some problem *within* the framework.
    
    """

    csv_params = dict()
    """
    Site-wide default parameters for CSV generation.
    This must be a dictionary that will be used 
    as keyword parameters to Python `csv.writer()
    <http://docs.python.org/library/csv.html#csv.writer>`_
    
    Possible keys include:
    
    - encoding : 
      the charset to use when responding to a CSV request.
      See 
      http://docs.python.org/library/codecs.html#standard-encodings
      for a list of available values.
      
    - many more allowed keys are explained in
      `Dialects and Formatting Parameters
      <http://docs.python.org/library/csv.html#csv-fmt-params>`_.
    
    """

    auto_configure_logger_names = 'atelier djangosite north lino'

    appy_params = dict(ooPort=8100)
    """
    Used by :class:`lino.mixins.printable.AppyBuildMethod`.
    """

    #~ decimal_separator = '.'
    decimal_separator = ','
    """
    Set this to either ``'.'`` or ``','`` to define wether to use 
    comma or dot as decimal point separator when entering 
    a `DecimalField`.
    """

    #~ decimal_group_separator = ','
    decimal_group_separator = ' '
    """
    Decimal group separator for :func:`lino.utils.moneyfmt`.
    """

    time_format_strftime = '%H:%M'
    """
    Format (in strftime syntax) to use for displaying dates to the user.
    If you change this setting, you also need to override :meth:`parse_time`.
    """

    date_format_strftime = '%d.%m.%Y'
    """
    Format (in strftime syntax) to use for displaying dates to the user.
    If you change this setting, you also need to override :meth:`parse_date`.
    """

    date_format_regex = "/^[0123]?\d\.[01]?\d\.-?\d+$/"
    """Format (in Javascript regex syntax) to use for displaying dates to
    the user.  If you change this setting, you also need to override
    :meth:`parse_date`.

    """

    datetime_format_strftime = '%Y-%m-%dT%H:%M:%S'
    """Format (in strftime syntax) to use for formatting timestamps in
    AJAX responses.  If you change this setting, you also need to
    override :meth:`parse_datetime`.

    """

    datetime_format_extjs = 'Y-m-d\TH:i:s'
    """Format (in ExtJS syntax) to use for formatting timestamps in AJAX
    calls.  If you change this setting, you also need to override
    :meth:`parse_datetime`.

    """

    _welcome_actors = []

    def init_before_local(self, *args):
        super(Site, self).init_before_local(*args)

        self.GFK_LIST = []
        self.VIRTUAL_FIELDS = []

        self.update_settings(
            LOGGING_CONFIG='lino.utils.log.configure',
            LOGGING=dict(
                filename=None,
                level='INFO',
                logger_names=self.auto_configure_logger_names,
                disable_existing_loggers=True,  # Django >= 1.5
            ),
        )

    def parse_date(self, s):
        """
        Convert a string formatted using
        :attr:`date_format_strftime` or  :attr:`date_format_extjs`
        into a `(y,m,d)` tuple (not a `datetime.date` instance).
        See `/blog/2010/1130`.
        """
        ymd = tuple(reversed(map(int, s.split('.'))))
        assert len(ymd) == 3
        return ymd
        #~ return datetime.date(*ymd)

    def parse_time(self, s):
        """
        Convert a string formatted using
        :attr:`time_format_strftime` or  :attr:`time_format_extjs`
        into a datetime.time instance.
        """
        hms = map(int, s.split(':'))
        return datetime.time(*hms)

    def parse_datetime(self, s):
        """
        Convert a string formatted using
        :attr:`datetime_format_strftime` or  :attr:`datetime_format_extjs`
        into a datetime.datetime instance.
        """
        #~ print "20110701 parse_datetime(%r)" % s
        #~ s2 = s.split()
        s2 = s.split('T')
        if len(s2) != 2:
            raise Exception("Invalid datetime string %r" % s)
        ymd = map(int, s2[0].split('-'))
        hms = map(int, s2[1].split(':'))
        return datetime.datetime(*(ymd + hms))
        #~ d = datetime.date(*self.parse_date(s[0]))
        #~ return datetime.combine(d,t)

    ignore_dates_before = datetime.date.today() + datetime.timedelta(days=-7)
    """Ignore dates before the gived date.  Set this to None if you want
    no limit.

    """

    def resolve_virtual_fields(self):
        for vf in self.VIRTUAL_FIELDS:
            vf.lino_resolve_type()
        self.VIRTUAL_FIELDS = []

    def register_virtual_field(self, vf):
        self.VIRTUAL_FIELDS.append(vf)

    def do_site_startup(self):
        """Start the Lino instance (the object stored as :setting:`LINO` in
        your :xfile:`settings.py`).  This is called exactly once from
        :mod:`lino.models` when Django has has populated it's model
        cache.

        This code can run several times at once when running
        e.g. under mod_wsgi: another thread has started and not yet
        finished `startup_site()`.

        """
        # self.logger.info("20140227 lino_site.Site.do_site_startup() a")
        
        super(Site, self).do_site_startup()

        from lino.core.kernel import Kernel
        self.kernel = Kernel(self)
        self.ui = self.kernel  # internal backwards compat

        # self.logger.info("20140227 lino_site.Site.do_site_startup() b")

    def setup_workflows(self):
        self.on_each_app('setup_workflows')

    def setup_choicelists(self):
        #~ raise Exception("20130302 setup_choicelists()")
        #~ logger.info("20130302 setup_choicelists()")
        from lino import dd
        dd.UserProfiles.reset()
        add = dd.UserProfiles.add_item
        add('000', _("Anonymous"), name='anonymous', level=None,
            #~ readonly=True,
            authenticated=False)
        add('100', _("User"), name='user', level='user')
        add('900', _("Administrator"), name='admin', level='admin')

    def add_user_field(self, name, fld):
        if self.user_model:
            from lino import dd
            #~ User = dd.resolve_model(self.user_model)
            dd.inject_field(self.user_model, name, fld)
            #~ if profile:
                #~ self.user_profile_fields.append(name)

    def get_generic_related(self, obj):
        """
        Yield all database objects in database which have a GenericForeignKey
        that points to the object `obj`.
        """
        from django.contrib.contenttypes.models import ContentType
        for gfk in self.GFK_LIST:
            ct = ContentType.objects.get_for_model(gfk.model)
            kw = dict()
            kw[gfk.fk_field] = obj.pk
            yield gfk, ct.get_all_objects_for_this_type(**kw)

    def get_used_libs(self, html=None):
        """
        Adds Lino, Jinja, Spinx, dateutil, ...
        """
        import lino
        yield ("Lino", lino.SETUP_INFO['version'], lino.SETUP_INFO['url'])

        for u in super(Site, self).get_used_libs(html):
            yield u

        #~ import tidylib
        #~ version = getattr(tidylib,'__version__','')
        #~ yield ("tidylib",version,"http://countergram.com/open-source/pytidylib")

        #~ import pyPdf
        #~ version = getattr(pyPdf,'__version__','')
        #~ yield ("pyPdf",version,"http://countergram.com/open-source/pytidylib")

        import jinja2
        version = getattr(jinja2, '__version__', '')
        yield ("Jinja", version, "http://jinja.pocoo.org/")

        import sphinx
        version = getattr(sphinx, '__version__', '')
        yield ("Sphinx", version, "http://sphinx-doc.org/")

        import dateutil
        version = getattr(dateutil, '__version__', '')
        yield ("python-dateutil", version, "http://labix.org/python-dateutil")

        #~ try:
            #~ import Cheetah
            #~ version = Cheetah.Version
            #~ yield ("Cheetah",version ,"http://cheetahtemplate.org/")
        #~ except ImportError:
            #~ pass

        try:
            from odf import opendocument
            version = opendocument.__version__
        except ImportError:
            version = self.not_found_msg
        yield ("OdfPy", version, "http://pypi.python.org/pypi/odfpy")

        try:
            import docutils
            version = docutils.__version__
        except ImportError:
            version = self.not_found_msg
        yield ("docutils", version, "http://docutils.sourceforge.net/")

        try:
            import suds
            version = suds.__version__
        except ImportError:
            version = self.not_found_msg
        yield ("suds", version, "https://fedorahosted.org/suds/")

        import yaml
        version = getattr(yaml, '__version__', '')
        yield ("PyYaml", version, "http://pyyaml.org/")

        if False:
            try:
                import pyratemp
                version = getattr(pyratemp, '__version__', '')
            except ImportError:
                version = self.not_found_msg
            yield ("pyratemp", version, "http://www.simple-is-better.org/template/pyratemp.html")

        if False:
            try:
                import ho.pisa as pisa
                version = getattr(pisa, '__version__', '')
                yield ("xhtml2pdf", version, "http://www.xhtml2pdf.com")
            except ImportError:
                pass

            try:
                import reportlab
                version = reportlab.Version
            except ImportError:
                version = self.not_found_msg
            yield ("ReportLab", version, "http://www.reportlab.org/rl_toolkit.html")

        try:
            #~ import appy
            from appy import version
            version = version.verbose
        except ImportError:
            version = self.not_found_msg
        yield ("Appy", version, "http://appyframework.org/pod.html")

        for p in self.installed_plugins:
            for u in p.get_used_libs(html):
                yield u

    def get_db_overview_rst(self):
        """
        Returns a reStructredText-formatted "database overview" report.
        Used by the :mod:`diag <lino.management.commands.diag>` command
        and in test cases.
        """
        from atelier import rstgen
        from lino.core.dbutils import (full_model_name,
                                       sorted_models_list, app_labels)


        #~ writeln("Lino %s" % lino.__version__)
        #~ yield (settings.SITE.verbose_name, settings.SITE.version)
        #~ writeln(settings.SITE.title)
        models_list = sorted_models_list()

        apps = app_labels()
        s = "%d apps: %s." % (len(apps), ", ".join(apps))
        s += "\n%d models:\n" % len(models_list)
        i = 0
        headers = [
            #~ "No.",
            "Name",
            #~ "Class",
            #~ "M",
            "#fields",
            "#rows",
            #~ ,"first","last"
        ]
        rows = []
        for model in models_list:
            if model._meta.managed:
                i += 1
                cells = []
                #~ cells.append(str(i))
                cells.append(full_model_name(model))
                #~ cells.append(str(model))
                #~ if model._meta.managed:
                #~ cells.append('X')
                #~ else:
                #~ cells.append('')
                cells.append(str(len(model._meta.fields)))
                #~ qs = model.objects.all()
                qs = model.objects.order_by('pk')
                n = qs.count()
                cells.append(str(n))
                #~ if n:
                #~ cells.append(obj2str(qs[0]))
                #~ cells.append(obj2str(qs[n-1]))
                #~ else:
                #~ cells.append('')
                #~ cells.append('')

                rows.append(cells)
        s += rstgen.table(headers, rows)
        return s

    partners_app_label = 'contacts'
    """
    Temporary setting, see :ref:`polymorphism`.
    """

    # three constants used by lino.modlib.workflows:
    max_state_value_length = 20
    max_action_name_length = 50
    max_actor_name_length = 100

    trusted_templates = False
    """
    Set this to True if you are sure that the users of your site won't try to 
    misuse Jinja's capabilities.
    """

    allow_duplicate_cities = False
    """In a default configuration (when :attr:`allow_duplicate_cities` is
    False), Lino declares a UNIQUE clause for :class:`Places
    <lino.modlib.countries.models.Places>` to make sure that your
    database never contains duplicate cities.  This behaviour mighr
    disturb e.g. when importing legacy data that did not have this
    restriction.  Set it to True to remove the UNIQUE clause.
    
    Changing this setting might affect your database structure and
    thus require a :doc:`/topics/datamig` if your application uses
    :mod:`lino.modlib.countries`.

    """

    uid = 'myuid'
    """A universal identifier for this Site.  This is needed when
    synchronizing with CalDAV server.  Locally created calendar
    components in remote calendars will get a UID based on this
    parameter, using ``"%s@%s" (self.pk,settings.SITE.ui)``.
    
    The default value is ``'myuid'``, and you should certainly
    override this on a production server that uses remote calendars.

    """

    project_model = None

    #~ user_model = "users.User"
    user_model = None

    auth_middleware = None

    legacy_data_path = None
    """Used by custom fixtures that import data from some legacy
    database.

    """

    propvalue_max_length = 200
    """
    Used by :mod:`lino.modlib.properties`.
    """

    never_build_site_cache = False
    """Set this to `True` if you want that Lino never (re)builds the site
    cache, even when asked.  This can be useful on a development
    server when you are debugging directly on the generated
    :xfile:`lino*.js`.  Or for certain unit test cases.

    """

    show_internal_field_names = False
    """Whether the internal field names should be visible.  Default is
    `False`.  ExtUI implements this by prepending them to the tooltip,
    which means that :attr:`use_quicktips` must also be `True`.

    """

    build_js_cache_on_startup = None
    """Whether the Javascript cache files should be built on startup for
    all user profiles and languages.
    
    On a production server this should be `True` for best performance,
    but while developing, it may be easier to set it to `False`, which means 
    that each file is built upon need (when a first request comes in).
    
    The default value `None` means that Lino decides automatically 
    during startup:
    it becomes `False` if
    either :func:`lino.core.dbutils.is_devserver` returns True
    or setting:`DEBUG` is set.

    """

    #~ replace_django_templates = True
    #~ """
    #~ Whether to replace Djano's template engine by Jinja.
    #~ """

    use_java = True

    use_experimental_features = False
    """
    Whether to include "experimental" features.
    """

    site_config_defaults = {}
    """
    Default values to be used when creating the 
    :class:`lino.models.SiteConfig` instance.
    
    Usage example::
    
      site_config_defaults = dict(default_build_method='appypdf')
      
    """

    is_demo_site = True
    """
    When this is `True`, then this site runs in "demo" mode.     
    "Demo mode" means:
    
    - the welcome text for anonymous users says "This demo site has X 
      users, they all have "1234" as password", 
      followed by a list of available usernames.
    
    Default value is `True`.
    On a production site you will of course set this to `False`.
    
    See also :attr:`demo_fixtures`.
    
    """

    demo_email = 'demo@example.com'
    """
    
    """

    demo_fixtures = ['std', 'demo', 'demo2']

    use_spinner = False  # doesn't work. leave this to False

    #~ django_admin_prefix = '/django'
    django_admin_prefix = None
    """
    The prefix to use for Django admin URLs.
    Leave this unchanged as long as :doc:`/tickets/70` is not solved.
    """

    start_year = 2011

    # plain_prefix = 'plain'
    # admin_prefix = ''

    time_format_extjs = 'H:i'
    """
    Format (in ExtJS syntax) to use for displaying dates to the user.
    If you change this setting, you also need to override :meth:`parse_time`.
    """

    date_format_extjs = 'd.m.Y'
    """
    Format (in ExtJS syntax) to use for displaying dates to the user.
    If you change this setting, you also need to override :meth:`parse_date`.
    """

    alt_date_formats_extjs = 'd/m/Y|Y-m-d'
    """
    Alternative date entry formats accepted by ExtJS Date widgets.
    """

    #~ default_number_format_extjs = '0,000.00/i'
    default_number_format_extjs = '0,00/i'

    uppercase_last_name = False

    tinymce_base_url = "http://www.tinymce.com/js/tinymce/jscripts/tiny_mce/"
    "Similar to :attr:`extjs_base_url` but pointing to http://www.tinymce.com."

    jasmine_root = None
    """
    Path to the Jasmine root directory. 
    Only used on a development server
    if the `media` directory has no symbolic link to the Jasmine root directory
    and only if :attr:`use_jasmine` is True.
    """

    tinymce_root = None
    """
    Path to the tinymce root directory. 
    Only to be used on a development server
    if the `media` directory has no symbolic link to the TinyMCE root directory,
    and only if :attr:`use_tinymce` is True.
    """

    default_user = None
    """
    Username to be used if a request with 
    no REMOTE_USER header makes its way through to Lino. 
    Which may happen on a development server and if Apache is 
    configured to allow it.
    Used by :mod:`lino.core.auth`.
    """

    anonymous_user_profile = '000'
    """
    The UserProfile to be assigned to anonymous user.
    
    """

    #~ remote_user_header = "REMOTE_USER"
    remote_user_header = None
    ldap_auth_server = None

    #~ simulate_remote_user = False

    use_gridfilters = True

    use_eid_applet = False
    """
    Whether to include functionality to read Belgian id cards
    using the official 
    `eid-applet <http://code.google.com/p/eid-applet>`_.
    This option is experimental and doesn't yet work.
    See `/blog/2012/1105`.
    """

    use_esteid = False
    """
    Whether to include functionality to read Estonian id cards.
    This option is experimental and doesn't yet work.
    """

    use_filterRow = not use_gridfilters
    """
    See `/blog/2011/0630`.
    This option was experimental and doesn't yet work (and maybe never will).
    """

    use_awesome_uploader = False
    """
    Whether to use AwesomeUploader. 
    This option was experimental and doesn't yet work (and maybe never will).
    """

    use_tinymce = True
    """
    Whether to use TinyMCE instead of Ext.form.HtmlEditor. 
    See also :attr:`tinymce_root`.
    See `/blog/2011/0523`.
    """

    use_jasmine = False
    """
    Whether to use the `Jasmine <https://github.com/pivotal/jasmine>`_ testing library.
    """

    use_quicktips = True
    """
    Whether to make use of `Ext.QuickTips
    <http://docs.sencha.com/ext-js/3-4/#!/api/Ext.QuickTips>`_
    when displaying :ref:`help_texts`.
    
    """

    use_css_tooltips = False
    """
    Whether to make use of CSS tooltips
    when displaying help texts defined in :class:`lino.models.HelpText`.
    """

    use_vinylfox = False
    """
    Whether to use VinylFox extensions for HtmlEditor. 
    This feature was experimental and doesn't yet work (and maybe never will).
    See `/blog/2011/0523`.
    """

    webdav_root = None
    """
    The path on server to store webdav files.
    Default is "PROJECT_DIR/media/webdav".
    """

    webdav_url = None
    """
    The URL prefix for webdav files.
    In a normal production configuration you should leave this to `None`, 
    Lino will set a default value "/media/webdav/",
    supposing that your Apache is configured as described in 
    :doc:`/admin/webdav`.
    
    This may be used to simulate a :term:`WebDAV` location 
    on a development server.
    For example on a Windows machine, you may set it to ``w:\``,      
    and before invoking :term:`runserver`, you issue in a command prompt::
    
        subst w: <dev_project_path>\media\webdav
        
    """


    #~ use_eidreader = False
    #~ """
    #~ Set this to `True` if this site should feature using :ref:`eidreader`.
    #~ """

    # use_davlink = False

    #~ max_auto_events = 72
    #~ """
    #~ Maximum number of automatic events to be generated.
    #~ """

    #~ mergeable_models = []
    #~ """
    #~ A list of models that should have a "Merge" action
    #~ (see :mod:`lino.mixins.mergeable`).
    #~ """


    sidebar_width = 0
    """
    Width of the sidebar in 1/12 of total screen width.
    Meaningful values are 0 (no sidebar), 2 or 3.
    """

    # for internal use:
    #~ _extjs_ui = None
    #~ _groph_ui = None
    _site_config = None

    def override_defaults(self, **kwargs):
        """
        """
        #~ logger.info("20130404 lino.site.Site.override_defaults")
        super(Site, self).override_defaults(**kwargs)

        #~ fd = list()
        #~ self.update_settings(FIXTURE_DIRS=tuple(settings_subdirs('fixtures')))
        if self.webdav_url is None:
            self.webdav_url = '/media/webdav/'
        if self.webdav_root is None:
            self.webdav_root = join(
                abspath(self.project_dir), 'media', 'webdav')

        if not self.django_settings.get('MEDIA_ROOT', False):
            """
            Django's default value for MEDIA_ROOT is an empty string.
            In certain test cases there migth be no MEDIA_ROOT key at all.
            Lino's default value for MEDIA_ROOT is ``<project_dir>/media``.
            """
            self.django_settings.update(
                MEDIA_ROOT=join(self.project_dir, 'media'))

        self.update_settings(
            ROOT_URLCONF='lino.ui.urls'
        )
        self.update_settings(
            MEDIA_URL='/media/'
        )
        self.update_settings(
            TEMPLATE_LOADERS=tuple([
                'lino.core.web.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                #~ 'django.template.loaders.eggs.Loader',
            ]))

        tcp = []
        if self.user_model == 'auth.User':
            self.update_settings(LOGIN_URL='/accounts/login/')
            self.update_settings(LOGIN_REDIRECT_URL="/")
            tcp += ['django.contrib.auth.context_processors.auth']

        tcp += [
            'django.core.context_processors.debug',
            'django.core.context_processors.i18n',
            'django.core.context_processors.media',
            'django.core.context_processors.static',
            #    'django.core.context_processors.request',
            #~ 'django.contrib.messages.context_processors.messages',
        ]
        self.update_settings(TEMPLATE_CONTEXT_PROCESSORS=tuple(tcp))

        self.define_settings(
            MIDDLEWARE_CLASSES=tuple(self.get_middleware_classes()))

        #~ print 20130313, self.django_settings['MIDDLEWARE_CLASSES']

    def is_imported_partner(self, obj):
        """
        Return whether the specified
        :class:`Partner <lino.modlib.contacts.models.Partner>` instance
        `obj` is to be considered as imported from some legacy database.
        """
        #~ return obj.id is not None and (obj.id < 200000 or obj.id > 299999)
        return False
        #~ return obj.id is not None and (obj.id > 10 and obj.id < 21)

    def site_header(self):
        """
        Used in footnote or header of certain printed documents.

        The convention is to call it as follows from an appy.pod template
        (use the `html` function, not `xhtml`)
        ::

          do text
          from html(settings.SITE.site_header())

        Note that this is expected to return a unicode string possibly
        containing valid HTML (not XHTML) tags for formatting.


        """
        if self.is_installed('contacts'):
            if self.site_config.site_company:
                return self.site_config.site_company.get_address('<br/>')
                #~ s = unicode(self.site_config.site_company) + " / "  + s
        #~ return ''

    def setup_main_menu(self):
        """
        To be implemented by applications.
        """
        pass

    #~ @property
    #~ def site_config(self):
        #~ SiteConfig = self.modules.system.SiteConfig
        #~ try:
            #~ return SiteConfig.objects.get(pk=1)
        #~ except SiteConfig.DoesNotExist:
            #~ kw = dict(pk=1)
            #~ kw.update(self.site_config_defaults)
            #~ sc = SiteConfig(**kw)
            #~ sc.full_clean()
            #~ sc.save()
            #~ return sc
    @property
    def site_config(self):
        """
        Returns the one and only
        :class:`lino.modlib.system.models.SiteConfig` instance which
        contains Site configuration parameters which are stored in the
        database and editable using the web interface.

        If no instance exists (which happens in a virgin database),
        we create it using default values from :attr:`site_config_defaults`.

        """

        if not 'system' in self.modules:
            return None

        if self._site_config is None:
            #~ raise Exception(20130301)
            #~ print '20130320 create _site_config'
            #~ from lino.core.dbutils import resolve_model
            #~ from lino.core.dbutils import obj2str
            #~ from lino.utils import dblogger as logger
            #~ SiteConfig = resolve_model('system.SiteConfig')
            SiteConfig = self.modules.system.SiteConfig
            #~ from .models import SiteConfig
            #~ from django.db.utils import DatabaseError
            try:
                #~ self._site_config = SiteConfig.real_objects.get(pk=1)
                self._site_config = SiteConfig.real_objects.get(
                    pk=self.config_id)
                #~ print "20130301 Loaded SiteConfig record", obj2str(self._site_config,True)
            #~ except (SiteConfig.DoesNotExist,DatabaseError):
            except SiteConfig.DoesNotExist:
            #~ except Exception,e:
                kw = dict(pk=self.config_id)
                #~ kw.update(settings.SITE.site_config_defaults)
                kw.update(self.site_config_defaults)
                self._site_config = SiteConfig(**kw)
                #~ print "20130301 Created SiteConfig record", obj2str(self._site_config,True)
                # 20120725
                # polls_tutorial menu selection `Config --> Site Parameters`
                # said "SiteConfig 1 does not exist"
                # cannot save the instance here because the db table possibly doesn't yet exit.
                #~ self._site_config.save()
        return self._site_config
    #~ site_config = property(get_site_config)

    #~ def shutdown(self):
        #~ self.clear_site_config()
        #~ return super(Site,self).shutdown()

    def clear_site_config(self):
        """
        Clear the cached SiteConfig instance.

        This is needed e.g. when the test runner has created a new
        test database.
        """
        self._site_config = None
        #~ print "20130320 clear_site_config"

    #~ def on_site_config_saved(self,sc):
        #~ """
        #~ Used internally. Called by SiteConfig.save() to update the cached instance.
        #~ """
        #~ pass
        #~ self._site_config = sc
        #~ from lino.core.dbutils import obj2str
        #~ print '20120801 site_config saved', obj2str(sc,True)

    def is_imported_partner(self, obj):
        """
        Return whether the specified
        :class:`Partner <lino.modlib.contacts.models.Partner>` instance
        `obj` is to be considered as imported from some legacy database.
        """
        #~ return obj.id is not None and (obj.id < 200000 or obj.id > 299999)
        return False
        #~ return obj.id is not None and (obj.id > 10 and obj.id < 21)

    def get_quicklinks(self, ar):
        from lino.core import menus
        m = menus.Toolbar(ar.get_user().profile, 'quicklinks')
        self.setup_quicklinks(ar, m)
        return m

    def get_site_menu(self, ui, profile):
        """
        Return this site's main menu for the given UserProfile.
        Must be a :class:`lino.core.menus.Toolbar` instance.
        Applications usually should not need to override this.
        """
        from django.utils.translation import ugettext_lazy as _
        from lino.core import menus
        main = menus.Toolbar(profile, 'main')
        self.setup_menu(ui, profile, main)
        main.compress()
        #~ url = self.admin_url
        #~ if not url:
            #~ url = "/"
        #~ main.add_url_button(url,label=_("Home"))
        #~ url = "javascript:Lino.close_all_windows()"
        #~ main.add_url_button(url,label=_("Home"))
        return main

    def setup_quicklinks(self, ar, m):
        """
        Override this
        in application-specific (or even local) :xfile:`settings.py` files
        to define a series of *quick links* to appear below the main menu bar.
        Example see :meth:`lino.projects.pcsw.settings.Site.setup_quicklinks`.
        """
        self.on_each_app('setup_quicklinks', ar, m)

    def setup_menu(self, ui, profile, main):
        """
        Set up the application's menu structure.

        The default implementation uses a system of
        predefined top-level items that are filled by the
        different :setting:`INSTALLED_APPS`.
        To use this system, application programmers
        define one or several of the following functions in
        their `models` module:

        - `setup_master_menu`
        - `setup_main_menu`
        - `setup_reports_menu`
        - `setup_config_menu`
        - `setup_explorer_menu`
        - `setup_site_menu`

        These functions, if present, will be called with three
        positional arguments: `ui`, `profile` and `menu`.

        Deserves more documentation.

        """
        from django.utils.translation import ugettext_lazy as _
        m = main.add_menu("master", _("Master"))
        self.on_each_app('setup_master_menu', ui, profile, m)
        #~ if not profile.readonly:
            #~ m = main.add_menu("my",_("My menu"))
            #~ self.on_each_app('setup_my_menu',ui,profile,m)
        self.on_each_app('setup_main_menu', ui, profile, main)
        m = main.add_menu("reports", _("Reports"))
        self.on_each_app('setup_reports_menu', ui, profile, m)
        m = main.add_menu("config", _("Configure"))
        self.on_each_app('setup_config_menu', ui, profile, m)
        m = main.add_menu("explorer", _("Explorer"))
        self.on_each_app('setup_explorer_menu', ui, profile, m)
        m = main.add_menu("site", _("Site"))
        self.on_each_app('setup_site_menu', ui, profile, m)
        return main

    def get_middleware_classes(self):
        """
        Yields the strings to be stored in
        the :setting:`MIDDLEWARE_CLASSES` setting.

        In case you don't want to use this method
        for defining :setting:`MIDDLEWARE_CLASSES`,
        you can simply set :setting:`MIDDLEWARE_CLASSES`
        in your :xfile:`settings.py`
        after the :class:`lino.site.Site` has been instantiated.

        `Django and standard HTTP authentication
        <http://stackoverflow.com/questions/152248/can-i-use-http-basic-authentication-with-django>`_
        """

        yield 'django.middleware.common.CommonMiddleware'
        #~ yield 'django.contrib.sessions.middleware.SessionMiddleware'
        if self.languages and len(self.languages) > 1:
            yield 'django.middleware.locale.LocaleMiddleware'
        #~ yield 'django.contrib.auth.middleware.AuthenticationMiddleware'
        #~ if self.user_model:
        #~ if self.user_model is None:
            #~ yield 'lino.core.auth.NoUserMiddleware'
        #~ elif self.remote_user_header:

        if self.auth_middleware:
            yield self.auth_middleware
        else:
            if self.user_model is None:
                yield 'lino.core.auth.NoUserMiddleware'
            elif self.remote_user_header:
                yield 'lino.core.auth.RemoteUserMiddleware'
                #~ yield 'django.middleware.doc.XViewMiddleware'
            else:
                # not using remote http auth, so we need sessions
                yield 'django.contrib.sessions.middleware.SessionMiddleware'
                if self.ldap_auth_server:
                    yield 'lino.core.auth.LDAPAuthMiddleware'
                else:
                    yield 'lino.core.auth.SessionUserMiddleware'

                #~ raise Exception("""\
    #~ `user_model` is not None, but no `remote_user_header` in your settings.SITE.""")
        #~ yield 'lino.utils.editing.EditingMiddleware'
        if True:
            yield 'lino.utils.ajax.AjaxExceptionResponse'

        if False:  # not BYPASS_PERMS:
            yield 'django.contrib.auth.middleware.RemoteUserMiddleware'
            # TODO: find solution for this:
            #~ AUTHENTICATION_BACKENDS = (
              #~ 'django.contrib.auth.backends.RemoteUserBackend',
            #~ )

        if False:
            #~ yield 'lino.utils.sqllog.ShortSQLLogToConsoleMiddleware'
            yield 'lino.utils.sqllog.SQLLogToConsoleMiddleware'
            #~ yield 'lino.utils.sqllog.SQLLogMiddleware'

    def get_main_action(self, profile):
        """
        Return the action to show as top-level "index.html".
        The default implementation returns `None`, which means
        that Lino will call :meth:`get_main_html`.
        """
        return None

    def get_main_html(self, request):
        """Return a chunk of html to be displayed in the main area of the
        admin index.  This is being called only if
        :meth:`get_main_action` returns `None`.  The default
        implementation renders the :xfile:`admin_main.html` template.

        """
        from lino.core import web
        return web.render_from_request(request, 'admin_main.html')

    def get_welcome_messages(self, ar):
        """
        Return or yield a list of messages to display for welcome.
        """
        for a in self._welcome_actors:
            for msg in a.get_welcome_messages(ar):
                yield msg

    def get_todo_tables(self, ar):
        """
        Return or yield a list of tables that should be empty
        """
        from django.db import models
        for app_module in models.get_apps():
            meth = getattr(app_module, 'get_todo_tables', None)
            if meth is not None:
                #~ dblogger.debug("Running %s of %s", methname, mod.__name__)
                for table, text in meth(ar):
                    if isinstance(table, basestring):
                        table = self.modules.resolve(table)
                    if table.default_action.get_view_permission(ar.get_user().profile):
                        if table.default_action.get_row_permission(ar, None, None):
                        #~ if table.default_action.get_bound_action_permission(ar,None,None):
                            if text is None:
                                text = "%d " + unicode(table.label)
                            yield (table, text)

    def get_installed_apps(self):

        if self.user_model is not None and self.remote_user_header is None:
            yield 'django.contrib.sessions'  # 20121103
        if self.django_admin_prefix:
            yield 'django.contrib.admin'
        yield 'lino.modlib.about'
        yield 'lino.modlib.extjs'
        yield 'lino.modlib.plain'
        yield "lino"
        for a in self.user_apps:
            yield a

    #~ def get_guest_greeting(self):
        #~ return E.p("Please log in")

    site_prefix = '/'
    """
    This must be set if your project is not sitting at the "root" URL 
    of your server.
    It must start *and* end with a *slash*. Default value is ``'/'``. 
    For example if you have::
    
        WSGIScriptAlias /foo /home/luc/mypy/lino_sites/foo/wsgi.py
      
    Then your :xfile:`settings.py` should specify::
    
        site_prefix = '/foo/'
    
    See also :ref:`mass_hosting`.
    
    """

    def buildurl(self, *args, **kw):
        #~ url = '/' + ("/".join(args))
        url = self.site_prefix + ("/".join(args))
        if len(kw):
            url += "?" + urlencode(kw)
        return url

    def build_media_url(self, *args, **kw):
        return self.buildurl('media', *args, **kw)

    # def build_admin_url(self, *args, **kw):
    #     if self.admin_prefix:
    #         return self.buildurl(self.admin_prefix, *args, **kw)
    #     return self.buildurl(*args, **kw)

    # def build_plain_url(self, *args, **kw):
    #     if self.plain_prefix:
    #         return self.buildurl('plain', *args, **kw)
    #     return self.buildurl(*args, **kw)

    def build_admin_url(self, *args, **kw):
        # backwards compatibility
        return self.kernel.default_renderer.plugin.build_plain_url(
            *args, **kw)
        
    def build_extjs_url(self, *args, **kw):
        # backwards compatibility
        return self.kernel.default_renderer.plugin.build_media_url(
            *args, **kw)
        # return self.plugins.extjs.build_media_url(*args, **kw) 

    # def build_extjs_url(self, url):
    #     if self.extjs_base_url:
    #         return self.extjs_base_url + url
    #     return self.build_media_url('extjs', url)

    # def build_extensible_url(self, url):
    #     if self.extensible_base_url:
    #         return self.extensible_base_url + url
    #     return self.build_media_url('extensible', url)

    # def build_bootstrap_url(self, url):
    #     if self.bootstrap_base_url:
    #         return self.bootstrap_base_url + url
    #     return self.build_media_url('bootstrap', url)

    def build_tinymce_url(self, url):
        if self.tinymce_base_url:
            return self.tinymce_base_url + url
        return self.build_media_url('tinymce', url)

    def get_system_note_recipients(self, ar, obj, silent):
        """
        Return or yield a list of recipients
        (i.e. strings "Full Name <name@example.com>" )
        to be notified by email about a system note issued
        by action request `ar` about the object instance `obj`.

        Default behaviour is to simply forwar it to the `obj`'s
        :meth:`get_system_note_recipients <lino.core.model.Model.get_system_note_recipients>`,
        but here is a hook to define local exceptions to the
        application specific default rules.
        """
        return obj.get_system_note_recipients(ar, silent)

    def welcome_html(self, ui=None):
        """
        Return a HTML version of the "This is APPLICATION
        version VERSION using ..." text. to be displayed in the
        About dialog, in the plain html footer, and maybe at other
        places.
        """
        from django.utils.translation import ugettext as _

        p = []
        sep = ''
        if self.verbose_name:
            p.append(_("This is "))
            if self.url:
                p.append(
                    E.a(self.verbose_name, href=self.url, target='_blank'))
            else:
                p.append(E.b(self.verbose_name))
            if self.version:
                p.append(' ')
                p.append(self.version)
            sep = _(' using ')

        for name, version, url in self.get_used_libs(html=E):
            p.append(sep)
            p.append(E.a(name, href=url, target='_blank'))
            p.append(' ')
            p.append(version)
            sep = ', '
        return E.span(*p)

    def login(self, username=None, **kw):
        """
        For usage from a shell.

        The :meth:`login <lino.site.Site.login>` method doesn't require any
        password because when somebody has command-line access we trust
        that she has already authenticated. It returns a
        :class:`BaseRequest <lino.core.requests.BaseRequest>` object which
        has a :meth:`show <lino.core.requests.BaseRequest.show>` method.
        """
        if self.user_model is None or username is None:
            if not 'user' in kw:
                from lino.core.auth import AnonymousUser
                kw.update(user=AnonymousUser.instance())
        else:
            kw.update(user=self.user_model.objects.get(username=username))

        if not 'renderer' in kw:
            kw.update(renderer=self.ui.text_renderer)

        from lino.core import requests
        import lino.ui.urls  # hack: trigger ui instantiation
        return requests.BaseRequest(**kw)

    def get_letter_date_text(self, today=None):
        """
        Returns a string like "Eupen, den 26. August 2013".

        """
        sc = self.site_config.site_company
        if today is None:
            today = datetime.date.today()
        from lino import dd
        if sc and sc.city:
            return _("%(place)s, %(date)s") % dict(
                place=unicode(sc.city.name), date=dd.fdl(today))
        return dd.fdl(today)

    #~ def get_letter_margin_top_html(self,ar):
        #~ s = '<p class="Centered9pt">%s</p>'
        #~ s = s % self.site_config.site_company.get_address('<br/>')
        #~ return s
        #~ from lino.utils.config import find_config_file
        #~ logo_path = find_config_file('logo.jpg')
        #~ return '<img src="%s"/>' % logo_path
        #~ return '<img src="file://%s" />' % logo_path

    #~ def get_letter_margin_bottom_html(self,ar):
        #~ s = '<p class="Centered9pt">%s</p>'
        #~ s = s % self.site_config.site_company.get_address('<br/>')
        #~ return s
        #~ return ''

    def get_admin_main_items(self, ar):
        """
        Yield a sequence of "items" to be rendered
        in :xfile:`admin_main.html`.
        """
        return []

    #~ def make_url_tester(self):
        #~ from lino.utils.test import URLTester
        #~ return URLTester()


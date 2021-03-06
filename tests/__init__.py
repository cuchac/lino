from unipath import Path

ROOTDIR = Path(__file__).parent.parent

# load  SETUP_INFO:
execfile(ROOTDIR.child('lino','project_info.py'),globals())

from djangosite.utils.pythontest import TestCase


class LinoTestCase(TestCase):
    demo_settings_module = "lino.projects.std.settings_test"
    project_root = ROOTDIR


class PackagesTests(LinoTestCase):
    def test_01(self):
        self.run_packages_test(SETUP_INFO['packages'])


class BlogTest(LinoTestCase):
    def test_all(self):
        self.run_simple_doctests("""
        docs/blog/2013/0316.rst
        docs/blog/2013/0507.rst
        # docs/blog/2013/0508.rst
        # docs/blog/2013/0513.rst
        # docs/blog/2013/0622.rst
        # docs/blog/2013/0714.rst
        docs/blog/2013/0716.rst
        # docs/blog/2013/0719.rst
        # docs/blog/2013/0807.rst
        # docs/blog/2013/0821.rst
        # docs/blog/2013/1210.rst
        docs/blog/2013/1211.rst
        docs/blog/2014/0108.rst
        # docs/blog/2014/0208.rst
        """)

    def one(self):
        """
        this does not start with "test_" and is not called automatically.
        used to call explicitly a single case::

          $ python setup.py test -s tests.BlogTest.one

        """
        self.run_simple_doctests("""
        docs/blog/2014/0208.rst
        """)


class DocsTests(LinoTestCase):

    def test_docs(self):
        self.run_simple_doctests("""
        docs/user/templates_api.rst
        docs/tutorials/dumpy.rst
        """)

    def test_de_BE(self):
        self.run_django_manage_test('docs/tutorials/de_BE')

    def test_auto_create(self):
        self.run_django_manage_test('docs/tutorials/auto_create')
    
    def test_human(self):
        self.run_django_manage_test('docs/tutorials/human')

    def test_actions(self):
        self.run_django_manage_test('docs/tutorials/actions')

    def test_actors(self):
        self.run_django_manage_test('docs/tutorials/actors')
    
    def test_pisa(self):
        self.run_django_manage_test('docs/tutorials/pisa')
    
    def test_polls(self):
        self.run_django_manage_test('docs/tutorials/polls')

    def test_quickstart(self):
        self.run_django_manage_test('docs/tutorials/quickstart')


class UtilsTests(LinoTestCase):

    def test_01(self):
        self.run_simple_doctests("""
        lino/utils/instantiator.py
        lino/utils/__init__.py
        lino/modlib/cal/utils.py
        """)

    # def test_01(self): self.run_simple_doctests('lino/utils/__init__.py')
    def test_02(self): self.run_simple_doctests('lino/utils/html2odf.py')
    def test_xmlgen_html(self): self.run_simple_doctests('lino/utils/xmlgen/html.py')
    def test_xmlgen_sepa(self): 
        # self.run_simple_doctests('lino/utils/xmlgen/sepa.py')
        self.run_simple_doctests('lino/utils/xmlgen/sepa/__init__.py')
    def test_05(self): self.run_simple_doctests('lino/utils/memo.py')
    def test_06(self): self.run_simple_doctests('lino/utils/html2xhtml.py')
    def test_07(self): self.run_simple_doctests('lino/utils/demonames.py')
    def test_08(self): self.run_simple_doctests('lino/utils/odsreader.py')
    
    def test_ssin(self): self.run_simple_doctests('lino/utils/ssin.py')
    #~ def test_11(self): self.run_simple_doctests('lino/core/choicelists.py')
    def test_jsgen(self): self.run_simple_doctests('lino/utils/jsgen.py')
    def test_ranges(self): self.run_simple_doctests('lino/utils/ranges.py')

    def test_vat_utils(self): self.run_simple_doctests('lino/modlib/vat/utils.py')
    def test_ledger_utils(self): self.run_simple_doctests('lino/modlib/ledger/utils.py')
    def test_accounts_utils(self): self.run_simple_doctests('lino/modlib/accounts/utils.py')
    def test_contacts_utils(self): self.run_simple_doctests('lino/modlib/contacts/utils.py')

    def test_mixins_addressable(self): self.run_simple_doctests('lino/mixins/addressable.py')

class I18nTests(LinoTestCase):
    def test_i18n(self): self.run_simple_doctests('docs/tested/test_i18n.rst')
    
class ProjectsTests(LinoTestCase):
    
    def test_events(self): 
        self.run_django_manage_test("lino/projects/events")
    def test_belref(self): 
        self.run_django_manage_test("lino/projects/belref")
    def test_babel_tutorial(self): 
        self.run_django_manage_test("lino/projects/babel_tutorial")
    def test_min1(self): 
        self.run_django_manage_test("lino/projects/min1")
    def test_min2(self): 
        self.run_django_manage_test("lino/projects/min2")


class Tutorials(LinoTestCase):
    def test_lets(self):
        self.run_django_manage_test("lino/tutorials/lets1")

    def test_mini(self):
        self.run_django_manage_test("lino/tutorials/mini")
    

class TestAppsTests(LinoTestCase):
    
    def test_20100212(self):
        self.run_django_admin_test_cd("lino/test_apps/20100212")

    def test_quantityfield(self):
        self.run_django_admin_test_cd("lino/test_apps/quantityfield")
    




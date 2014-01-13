from django.forms.widgets import Media
from django.http.request import HttpRequest
from django.test.testcases import TestCase
from lino.core.assets import Assets
from lino.core.requests import ActionRequest


class AssetsTest(TestCase):

    # Testing class defining some media and glue
    class TestClass(Assets):
        class Media:
            css = (
                'test1.css',
                'test2.css'
            )
            js = (
                'js1.js',
                'js2.js'
            )
            glue = (
                'tests/glue.js'
            )

    def testMediaGenerating(self):
        media = self.TestClass.media
        self.assertHTMLEqual(unicode(media), "")

        all_media = Media()

        all_media += media

    def testGlueGenerating(self):
        media = self.TestClass.media

        ar = ActionRequest(request=HttpRequest())

        self.assertHTMLEqual(media.render_glue(ar), "")
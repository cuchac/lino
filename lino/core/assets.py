from django.forms import widgets
from django.utils import six
from lino.core import web

widgets.MEDIA_TYPES = widgets.MEDIA_TYPES + ("glue", )


class AssetsMetaClass(widgets.MediaDefiningClass):
    pass


class Assets(six.with_metaclass(AssetsMetaClass)):
    name = None


class AssetsMedia(widgets.Media):
    def __init__(self, *args, **kwargs):
        self._glue = []

        return super(AssetsMedia, self).__init__(*args, **kwargs)

    def add_glue(self, glue):
        self._glue.append(*glue)

    def render_glue(self, ar):
        if not ar:
            return ""

        context = {
            'name': None
        }

        for glue in self._glue:
            context['name'] = glue
            web.render_from_request(ar.request, glue, **context)

#Monkey-patch to use Assets class instead of Media
widgets.Media = AssetsMedia


class AssetsManager(object):
    _assets = {}

    @classmethod
    def register(cls, assets):
        """
        Registers Assets class to global assets catalog
        """
        assert isinstance(assets.name, Assets)
        cls._assets[assets.name] = assets

    @classmethod
    def render_glue(cls, ar):
        context = {
            'manager': cls,
            'ar': ar
        }
        return web.render_from_request(ar.request, "assets.html", context)

    @property
    def assets(self):
        return self._assets

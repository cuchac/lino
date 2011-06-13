# -*- coding: UTF-8 -*-
## Copyright 2008-2010 Luc Saffre
## This file is part of the Lino-DSBE project.
## Lino-DSBE is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino-DSBE is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino-DSBE; if not, see <http://www.gnu.org/licenses/>.


from django.utils.translation import ugettext_lazy as _

from lino.utils.instantiator import Instantiator, i2d
from lino.tools import resolve_model


def objects():
  
    noteType = Instantiator('notes.NoteType',"name").build
    # TODO: move the following to modlib.notes.fixtures
    yield noteType((u"Test (odt)"),build_method='appyodt',template='test.odt')
    yield noteType((u"Test (rtf)"),build_method='rtf',template='test.rtf')
   
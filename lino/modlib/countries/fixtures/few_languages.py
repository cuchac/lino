﻿## Copyright 2009-2011 Luc Saffre
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

from django.db import models
#countries = models.get_app('countries')

from lino.utils.instantiator import Instantiator

Language = Instantiator('countries.Language',"id name").build

def objects():
    yield Language('ger',"German")
    yield Language('fre',"French")
    yield Language('eng',"English")
    yield Language('est',"Estonian")
    yield Language('dut',"Dutch")

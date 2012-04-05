# -*- coding: UTF-8 -*-
## Copyright 2008-2011 Luc Saffre
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


from django.contrib.contenttypes.models import ContentType
from lino.utils.instantiator import Instantiator, i2d
from lino.tools import resolve_model
from django.utils.translation import ugettext_lazy as _


from django.db import models
from django.conf import settings
from lino.utils.babel import babel_values, babelitem

Person = resolve_model(settings.LINO.person_model)
Company = resolve_model(settings.LINO.company_model)
ExclusionType = resolve_model('pcsw.ExclusionType')

#~ from lino.modlib.properties import models as properties 

def objects():
  
    noteType = Instantiator('notes.NoteType',"name").build
    
    yield noteType(u"Beschluss")
    yield noteType(u"Konvention",remark=u"Einmaliges Dokument in Verbindung mit Arbeitsvertrag")
    #~ yield noteType(u"Externes Dokument",remark=u"Aufenthaltsgenehmigung, Arbeitsgenehmigung, Arbeitsvertrag,...")
    yield noteType(u"Brief oder Einschreiben")
    yield noteType(u"Notiz",remark=u"Kontaktversuch, Gesprächsbericht, Telefonnotiz")
    yield noteType(u"Vorladung",remark=u"Einladung zu einem persönlichen Gespräch")
    yield noteType(u"Übergabeblatt",remark=u"Übergabeblatt vom allgemeinen Sozialdienst") # (--> Datum Eintragung DSBE)
    yield noteType(u"Neuantrag")
    yield noteType(u"Antragsformular")
    yield noteType((u"Auswertungsbogen allgemein"),build_method='rtf',template=u'Auswertungsbogen_allgemein.rtf')
    yield noteType((u"Anwesenheitsbescheinigung"),build_method='rtf',template=u'Anwesenheitsbescheinigung.rtf')
    yield noteType((u"Lebenslauf"),build_method='appyrtf',template=u'cv.odt')
    
    eventType = Instantiator('notes.EventType',"name").build
    
    yield eventType(u"Eröffnungsbericht")
    yield eventType(u"Erstgespräch")
    yield eventType(u"Abschlussbericht")
    
    #~ projectType = Instantiator('projects.ProjectType',"name").build
    #~ yield projectType(u"VSE Ausbildung")
    #~ yield projectType(u"VSE Arbeitssuche")
    #~ yield projectType(u"VSE Integration")
    #~ yield projectType(u"Hausinterne Arbeitsverträge")
    #~ yield projectType(u"Externe Arbeitsverträge")
    #~ yield projectType(u"Kurse und Zusatzausbildungen")
    
    #~ yield projectType(u"Sozialhilfe")
    #~ yield projectType(u"EiEi")
    #~ yield projectType(u"Aufenthaltsgenehmigung")
    
    studyType = Instantiator('jobs.StudyType').build
    #~ yield studyType(u"Schule")
    #~ yield studyType(u"Sonderschule")
    #~ yield studyType(u"Ausbildung")
    #~ yield studyType(u"Lehre")
    #~ yield studyType(u"Hochschule")
    #~ yield studyType(u"Universität")
    #~ yield studyType(u"Teilzeitunterricht")
    #~ yield studyType(u"Fernkurs")
    yield studyType(**babel_values('name',
          de=u"Schule",
          fr=u"École",
          en=u"School",
          ))
    yield studyType(**babel_values('name',
          de=u"Sonderschule",
          fr=u"École spéciale",
          en=u"Special school",
          ))
    yield studyType(**babel_values('name',
          de=u"Ausbildung",
          fr=u"Formation",
          en=u"Schooling",
          ))
    yield studyType(**babel_values('name',
          de=u"Lehre",
          fr=u"Apprentissage",
          en=u"Apprenticeship",
          ))
    yield studyType(**babel_values('name',
          de=u"Hochschule",
          fr=u"École supérieure",
          en=u"Highschool",
          ))
    yield studyType(**babel_values('name',
          de=u"Universität",
          fr=u"Université",
          en=u"University",
          ))
    yield studyType(**babel_values('name',
          de=u"Teilzeitunterricht",
          fr=u"Cours à temps partiel",
          en=u"Part-time study",
          ))
    yield studyType(**babel_values('name',
          de=u"Fernkurs",
          fr=u"Cours à distance",
          en=u"Remote study",
          ))
    
    

    #~ studyContent = Instantiator('pcsw.StudyContent',"name").build
    #~ yield studyContent(u"Grundschule")
    #~ yield studyContent(u"Mittlere Reife")
    #~ yield studyContent(u"Abitur")
    #~ yield studyContent(u"Schlosser")
    #~ yield studyContent(u"Schreiner")
    #~ yield studyContent(u"Biotechnologie")
    #~ yield studyContent(u"Geschichte")

    #~ license = Instantiator('pcsw.DrivingLicense',"id name").build
    #~ yield license('A',u"Motorrad")
    #~ yield license('B',u"PKW")
    #~ yield license('C',u"LKW")
    #~ yield license('CE',u"LKW über X Tonnen")
    #~ yield license('D',u"Bus")
    
    
    #~ coachingType = Instantiator('pcsw.CoachingType',"name").build
    #~ yield coachingType(u"DSBE")
    #~ yield coachingType(u"Schuldnerberatung")
    #~ yield coachingType(u"Energieberatung")
    #~ yield coachingType(u"allgemeiner Sozialdienst")
    
    
    excltype = Instantiator('pcsw.ExclusionType','name').build
    yield excltype(u"Termin nicht eingehalten")
    yield excltype(u"ONEM-Auflagen nicht erfüllt")
    
    #~ linkType = Instantiator('links.LinkType',"a_type b_type name").build
    Company = resolve_model(settings.LINO.company_model)
    Person = resolve_model(settings.LINO.person_model)
    
    #~ yield linkType(
        #~ ContentType.objects.get_for_model(Company),
        #~ ContentType.objects.get_for_model(Person),
        #~ babelitem(de=u"Direktor",fr=u"directeur"))
    #~ yield linkType(
        #~ ContentType.objects.get_for_model(Person),
        #~ ContentType.objects.get_for_model(Person),
        #~ babelitem(de=u"Vater",fr=u"père"))
    #~ yield linkType(
        #~ ContentType.objects.get_for_model(Person),
        #~ ContentType.objects.get_for_model(Person),
        #~ babelitem(de=u"Mutter",fr=u"mère"))
    #~ yield linkType(babelitem(de=u"Private Website",fr=u"Site privé"))
    #~ yield linkType(babelitem(de=u"Firmen-Website",fr=u"Site commercial"))
    #~ yield linkType(babelitem(de=u"Facebook-Profil",fr=u"Profil Facebook"))
    #~ yield linkType(babelitem(de=u"Sonstige",fr=u"Autres"))
    
    from lino.models import update_site_config
    
    uploadType = Instantiator('uploads.UploadType',"name").build
    yield uploadType(babelitem(de=u"Personalausweis",fr=u"Carte d'identité",en="ID card"))
    p = uploadType(babelitem(de=u"Aufenthaltserlaubnis",fr=u"Permis de séjour",en="Residence permit"))
    yield p
    update_site_config(residence_permit_upload_type=p)
    p = uploadType(babelitem(de=u"Arbeitserlaubnis",fr=u"Permis de travail",en="Work permit"))
    yield p
    update_site_config(work_permit_upload_type = p)
    yield uploadType(babelitem(de=u"Vertrag",fr=u"Contrat",en="Contract"))
    p = uploadType(babelitem(de=u"Führerschein",fr=u"Permis de conduire",en="Diving licence"))
    yield p
    update_site_config(driving_licence_upload_type = p)
    
    
    from lino.modlib.cal.models import DurationUnit

    exam_policy = Instantiator('isip.ExamPolicy','every',every_unit=DurationUnit.months).build
    yield exam_policy(1,**babel_values('name',en='every month',de='monatlich',fr="mensuel"))
    yield exam_policy(2,**babel_values('name',en='every 2 months',de='zweimonatlich',fr="bimensuel"))
    yield exam_policy(3,**babel_values('name',en='every 3 months',de='alle 3 Monate',fr="tous les 3 mois"))
    exam_policy = Instantiator('isip.ExamPolicy','every',every_unit=DurationUnit.weeks).build
    yield exam_policy(2,**babel_values('name',en='every 2 weeks',de='zweiwöchentlich',fr="hebdomadaire"))
    exam_policy = Instantiator('isip.ExamPolicy','every').build
    yield exam_policy(0,**babel_values('name',en='other',de='andere',fr="autre"))
        
    #~ def create_dsbe_aidtype(id,name,name_fr):
        #~ return AidType(id=id,name=name,name_fr=name_fr)        
    
    aidtype = Instantiator('pcsw.AidType').build
    yield aidtype(**babel_values('name',
      de=u'Eingliederungseinkommen Kat 1 (Zusammenlebend)',
      fr=u"Revenu d'intégration cat. 1 (couple)",
      en=u"Revenu d'intégration cat. 1 (couple)",
      ))
    yield aidtype(**babel_values('name',
      de=u'Eingliederungseinkommen Kat 2 (Alleinlebend)',
      fr=u"Revenu d'intégration cat. 2 (célibataire)",
      en=u"Revenu d'intégration cat. 2 (célibataire)",
      ))
    yield aidtype(**babel_values('name',
      de=u'Eingliederungseinkommen Kat 3 (Familie zu Lasten)',
      fr=u"Revenu d'intégration cat. 3 (famille à charge)",
      en=u"Revenu d'intégration cat. 3 (famille à charge)",
      ))
    yield aidtype(**babel_values('name',
      de=u'Ausl\xe4nderbeihilfe Kat 1 (Zusammenlebend)',
      fr=u"Aide aux immigrants cat. 1 (couple)",
      en=u"Aide aux immigrants cat. 1 (couple)",
      ))
    yield aidtype(**babel_values('name',
      de=u'Ausl\xe4nderbeihilfe Kat 2 (Alleinlebend)',
      fr=u"Aide aux immigrants cat. 2 (célibataire)",
      en=u"Aide aux immigrants cat. 2 (célibataire)",
      ))
    yield aidtype(**babel_values('name',
      de=u'Ausl\xe4nderbeihilfe Kat 3 (Familie zu Lasten)',
      fr=u"Aide aux immigrants cat. 3 (famille à charge)",
      en=u"Aide aux immigrants cat. 3 (famille à charge)",
      ))
    yield aidtype(**babel_values('name',
      de=u'Sonstige Sozialhilfe',
      fr=u"Autre aide sociale",
      en=u"Autre aide sociale",
      ))
    
    I = Instantiator('lino.HelpText','content_type field help_text').build
    
    t = ContentType.objects.get_for_model(Person)
    yield I(t,'in_belgium_since',"""\
Since when this person in Belgium lives.
<b>Important:</b> help_text can be formatted.""")
    yield I(t,'noble_condition',"""\
The eventual noble condition of this person. Imported from TIM.
""")
    yield I(t,'birth_date',u"""\
Unkomplette Geburtsdaten sind erlaubt, z.B. 
<ul>
<li>00.00.1980 : irgendwann in 1980</li>
<li>00.07.1980 : im Juli 1980</li>
<li>23.07.0000 : Geburtstag am 23. Juli, Alter unbekannt</li>
</ul>    
""")
    
    Partner = resolve_model('contacts.Partner')
    t = ContentType.objects.get_for_model(Partner)
    yield I(t,'language',u"""\
    Die Sprache, in der Dokumente ausgestellt werden sollen.
""")
    
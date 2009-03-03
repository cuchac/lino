## Copyright 2009 Luc Saffre

## This file is part of the Lino project.

## Lino is free software; you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## Lino is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
## or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
## License for more details.

## You should have received a copy of the GNU General Public License
## along with Lino; if not, write to the Free Software Foundation,
## Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA



from lino.django.reports.reports import Report, list_view

class ReportsSite:
    def __init__(self):
        self._registry={}
        
    def register(self,rptclass):
        self._registry[rptclass.__name__] = rptclass
        
    def get_report(self,name):
        return self._registry[name]
        
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include
        
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        
        # Admin-site-wide views.
        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.index)),
            url(r'^(?P<rptname>\w+)/$',
                wrap(self.list_view)),
            url(r'^(?P<rptname>\w+)/(?P<rownum>.+)/$',
                wrap(self.page_view)),
        )
        
        # Add in each model's views.
        for model, model_admin in self._registry.iteritems():
            urlpatterns += patterns('',
                url(r'^%s/%s/' % (model._meta.app_label, model._meta.module_name),
                    include(model_admin.urls))
            )
        return urlpatterns         
        
    def urls(self):
        return self.get_urls()
    urls = property(urls)
    
    
    def list_view(self,request,rptname):
        rpt = self.get_report(rptname)
        fsclass = modelformset_factory(rpt.modelForm,
                                       fields=rpt.columNames.split())
        if request.method == 'POST':
            fs = fsclass(request.POST,queryset=rpt.queryset)
            if fs.is_valid():
                fs.save()
        else:
            fs = fsclass(queryset=rpt.queryset)
        context_dict = dict(
            report=rpt,
            formset=fs,
        )
        return render_to_response("reports/list.html",context)    
    
    def page_view(self,request,rptname,rownum):
        rpt = self.get_report(rptname)
        obj=rpt.queryset[int(rownum)]
        if request.method == 'POST':
            frm=rpt.modelForm(request.POST,instance=obj)
            if frm.is_valid():
                frm.save()
        else:
            frm=rpt.modelForm(instance=obj)      
        return render_to_response("reports/page.html",context)    
site = ReportsSite()


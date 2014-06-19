from django.conf.urls import patterns, include, url

from django.contrib import admin
# from app.views import hello
from app.food import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',views.index),
    url(r'^debug',views.debug),

    url(r'^getcontent',views.get_content),
    url(r'^search/$',views.wordcloud),
     url(r'^autocomplate',views.get_top_word),
    url(r'^analyse/(.*)',views.analyse),
    url(r'^cache',views.gen_cache),
    url(r'^baike',views.baike),

    url(r'^admin/', include(admin.site.urls)),
)

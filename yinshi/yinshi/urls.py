from django.conf.urls import patterns, include, url

from django.contrib import admin
# from app.views import hello
from app.food import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #   url(r'^hello/test/',views.test),
    url(r'^$',views.index),
    # url(r'^base',views.base),
    url(r'^debug',views.debug),
    url(r'^getcontent',views.get_content),
    # url(r'^hello/compare/',views.compare),
    url(r'^search/$',views.wordcloud),
    url(r'^cache',views.gen_cache),
    # url(r'^test',views.test),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

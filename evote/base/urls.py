from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from rest_framework_extensions.routers import ExtendedDefaultRouter

from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from evote.voting import views as voting_views

# router = ExtendedDefaultRouter()
#
# router.register(r'author', blog_api_views.AuthorViewSet, base_name='author')
# router.register(r'category', blog_api_views.CategoryViewSet, base_name='category')
# router.register(r'tag', blog_api_views.TagViewSet, base_name='tag')
# router.register(r'post', blog_api_views.PostViewSet, base_name='post')

urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logout.html'}),
    url(r'^dashboard/$', voting_views.dashboard, name='dashboard'),
    url(r'^organization-campaigns/', voting_views.adm_dashboard, name='adm_dashboard'),
    url(r'^my-campaigns/', voting_views.my_dashboard, name='my_dashboard'),
    url(r'^campaign-edit/archive/', voting_views.archive_campaign, name='archive_campaign'),
    url(r'^campaign-edit/', voting_views.campaign, name='campaign'),
    url(r'^profile/$', voting_views.profile, name='profile'),
    url(r'^test/$', TemplateView.as_view(template_name='test.html')),
    url(r'^vote/', voting_views.vote, name='vote'),
    url(r'^report/', voting_views.report, name='report'),
    url(r'^favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True), name='favicon'),
    url(r'^.*$', RedirectView.as_view(url='/dashboard/', permanent=False), name='index'),

]

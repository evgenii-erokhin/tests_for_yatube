from django.views.generic.base import TemplateView


class AuthorPage(TemplateView):
    template_name = 'about/author.html'


class TechPage(TemplateView):
    template_name = 'about/tech.html'

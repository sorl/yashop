import datetime
from django.db import models
from django.db.models.expressions import RawSQL
from django.utils.functional import cached_property
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from metafields.models import MetaFieldsMixin
from utils.fields import StringField, TransStringField, TransHandleField, TransTextField
from sumsum.middleware import get_request


class PageManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by(RawSQL('title_t->>%s', (get_language(),)))


class Page(MetaFieldsMixin, models.Model):
    user = models.ForeignKey('users.User', verbose_name=_('author'))
    body_html_t = TransTextField(_('description'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    handle_t = TransHandleField(_('handle'), populate_from='title_t', unique_together=('handle_t', 'user'))
    published_at = models.DateTimeField(_('published at'), blank=True, null=True, default=datetime.datetime.now)
    shop = models.ForeignKey('shops.Shop', blank=True, null=True)
    template_suffix = StringField(_('template suffix'))
    title_t = TransStringField(_('title'), required=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = PageManager()

    class Meta:
        ordering = ('updated_at',)
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        self.user = get_request().user
        super().save(**kwargs)

    @cached_property
    def author(self):
        return self.user.get_full_name()

    @property
    def content(self):
        return self.body_html

    def get_absolute_url(self):
        return self.url

    @cached_property
    def url(self):
        return '/pages/{}'.format(self.handle)

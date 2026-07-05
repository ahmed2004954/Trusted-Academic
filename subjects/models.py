from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), unique=True, blank=True, allow_unicode=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class GradeLevel(models.Model):
    class Category(models.TextChoices):
        PRIMARY = 'primary', _('Primary')
        PREPARATORY = 'preparatory', _('Preparatory')
        SECONDARY = 'secondary', _('Secondary')

    name = models.CharField(_('name'), max_length=100, unique=True)
    category = models.CharField(_('category'), max_length=20, choices=Category.choices)
    order = models.PositiveSmallIntegerField(_('order'), default=0)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('grade level')
        verbose_name_plural = _('grade levels')
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return self.name

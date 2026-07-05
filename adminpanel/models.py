from django.conf import settings
from django.db import models
from django.urls import NoReverseMatch, reverse


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='admin_audit_logs',
        blank=True,
        null=True,
    )
    action = models.CharField(max_length=100)
    target_label = models.CharField(max_length=255, blank=True)
    target_url = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['actor', 'created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.action} by {self.actor or "system"} at {self.created_at:%Y-%m-%d %H:%M}'


def _admin_change_url(target) -> str:
    if not target or not getattr(target, 'pk', None):
        return ''
    meta = target._meta
    try:
        return reverse(f'admin:{meta.app_label}_{meta.model_name}_change', args=[target.pk])
    except NoReverseMatch:
        return ''


def record_audit_log(actor, action, target, metadata=None):
    return AuditLog.objects.create(
        actor=actor if getattr(actor, 'is_authenticated', False) else None,
        action=action,
        target_label=str(target) if target else '',
        target_url=_admin_change_url(target),
        metadata=metadata or {},
    )

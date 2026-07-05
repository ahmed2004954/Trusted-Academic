from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body', 'attachment']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Write your message...')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        body = cleaned_data.get('body')
        attachment = cleaned_data.get('attachment')
        if not body and not attachment:
            raise forms.ValidationError(_('Enter a message or attach a file.'))
        return cleaned_data

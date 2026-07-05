from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Payment


class PaymentReceiptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receipt_image'].required = True

    class Meta:
        model = Payment
        fields = ['payment_method', 'receipt_image', 'transaction_reference']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'receipt_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'payment_method': _('Payment method'),
            'receipt_image': _('Receipt image'),
            'transaction_reference': _('Transaction reference'),
        }


class PaymentRejectionForm(forms.Form):
    rejection_reason = forms.CharField(
        label=_('Rejection reason'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
    )

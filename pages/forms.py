from django import forms
from django.utils.translation import gettext_lazy as _
from orders.models import Order

class CheckoutForm(forms.ModelForm):
    field_class = 'w-full px-4 py-3 border border-black/10 bg-white rounded-lg focus:ring-2 focus:ring-[#a64224]/20 focus:border-[#a64224] transition-colors outline-none'

    customer_name = forms.CharField(
        label=_("Full Name"),
        widget=forms.TextInput(attrs={
            'class': field_class,
            'placeholder': _("Enter your full name")
        })
    )
    phone = forms.CharField(
        label=_("Phone Number"),
        widget=forms.TextInput(attrs={
            'class': field_class,
            'placeholder': _("Enter your phone number")
        })
    )
    state = forms.CharField(
        label=_("State / Governorate"),
        widget=forms.Select(attrs={
            'class': field_class,
            'id': 'state-select',
        })
    )
    city = forms.CharField(
        label=_("City"),
        widget=forms.Select(attrs={
            'class': field_class,
            'id': 'city-select',
        })
    )
    address = forms.CharField(
        label=_("Address"),
        widget=forms.Textarea(attrs={
            'class': field_class,
            'placeholder': _("Street address, City, etc."),
            'rows': 3
        })
    )
    notes = forms.CharField(
        label=_("Order Notes (Optional) "),
        required=False,
        widget=forms.Textarea(attrs={
            'class': field_class,
            'placeholder': _("Any special instructions?"),
            'rows': 2
        })
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'phone', 'state', 'city', 'address', 'notes']

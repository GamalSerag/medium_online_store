import re

from django import forms
from django.utils.translation import gettext_lazy as _
from orders.models import Order


EGYPT_PHONE_RE = re.compile(r'^0?1[0125]\d{8}$')
NAME_RE = re.compile(r"^[A-Za-z\u0600-\u06FF][A-Za-z\u0600-\u06FF\s'.-]*$")

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

    def clean_customer_name(self):
        name = ' '.join(self.cleaned_data['customer_name'].strip().split())
        if len(name) < 2:
            raise forms.ValidationError(_("Please enter your full name."))
        if len(name) > 80:
            raise forms.ValidationError(_("Name must be 80 characters or less."))
        if not NAME_RE.match(name):
            raise forms.ValidationError(_("Name can only contain letters, spaces, apostrophes, hyphens, or dots."))
        return name

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        normalized = re.sub(r'[\s().-]+', '', phone)
        if normalized.startswith('00'):
            normalized = normalized[2:]
        if normalized.startswith('+'):
            normalized = normalized[1:]
        if normalized.startswith('20'):
            normalized = normalized[2:]
        if not EGYPT_PHONE_RE.match(normalized):
            raise forms.ValidationError(_("Enter a valid Egyptian mobile number."))
        return '0' + normalized if not normalized.startswith('0') else normalized

    def clean_state(self):
        state = self.cleaned_data['state'].strip()
        if not state or len(state) < 2:
            raise forms.ValidationError(_("Please select a governorate."))
        if len(state) > 100:
            raise forms.ValidationError(_("Governorate name is too long."))
        return state

    def clean_city(self):
        city = self.cleaned_data['city'].strip()
        if not city or len(city) < 2:
            raise forms.ValidationError(_("Please select a city."))
        if len(city) > 100:
            raise forms.ValidationError(_("City name is too long."))
        return city

    def clean_address(self):
        address = ' '.join(self.cleaned_data['address'].strip().split())
        if len(address) < 10:
            raise forms.ValidationError(_("Please enter a detailed address."))
        if len(address) > 500:
            raise forms.ValidationError(_("Address must be 500 characters or less."))
        return address

    def clean_notes(self):
        notes = self.cleaned_data.get('notes', '').strip()
        if len(notes) > 500:
            raise forms.ValidationError(_("Order notes must be 500 characters or less."))
        return notes

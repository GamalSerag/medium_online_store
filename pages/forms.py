from django import forms
from django.utils.translation import gettext_lazy as _
from orders.models import Order

class CheckoutForm(forms.ModelForm):
    customer_name = forms.CharField(
        label=_("Full Name"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors',
            'placeholder': _("Enter your full name")
        })
    )
    phone = forms.CharField(
        label=_("Phone Number"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors',
            'placeholder': _("Enter your phone number")
        })
    )
    address = forms.CharField(
        label=_("Address"),
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors',
            'placeholder': _("Street address, City, etc."),
            'rows': 3
        })
    )
    notes = forms.CharField(
        label=_("Order Notes (Optional)"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors',
            'placeholder': _("Any special instructions?"),
            'rows': 2
        })
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'phone', 'address', 'notes']

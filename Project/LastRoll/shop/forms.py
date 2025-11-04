from django import forms
from django.contrib.auth.models import User
from store.models import SellerApplication
from store.models import Product
from store.models import Order


class BuyerRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class SellerRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    store_name = forms.CharField(max_length=100)
    location = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
class ProductForm(forms.ModelForm):
    name = forms.TextInput()
    description = forms.TextInput()
    price = forms.DecimalField()
    stock = forms.IntegerField()
    image = forms.ImageField()
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']
    

VALID_PROMO_CODES = {
    "VALID",
    "TESTING"
}

class OrderForm(forms.ModelForm):
    address = forms.TextInput()
    payment = forms.CharField(max_length=100)

    class Meta:
        model = Order
        fields = ['payment', 'address']

    def clean_payment(self):
        code = self.cleaned_data.get('payment', '').strip()
        if code and code.upper() not in VALID_PROMO_CODES:
            raise forms.ValidationError("That promo code is not valid.")
        return code.upper()
   

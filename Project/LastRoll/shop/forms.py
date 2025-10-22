# shop/models.py
from django import forms
from store.models import Product

class ProductForm(forms.ModelForm):
    name = forms.TextInput()
    description = forms.TextInput()
    price = forms.DecimalField()
    stock = forms.IntegerField()
    image = forms.ImageField()
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']

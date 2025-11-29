from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from store.models import SellerApplication, Product, Order


class BuyerRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class SellerRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    store_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class ProductForm(forms.ModelForm):
    COLOR_PRESETS = [
        ("N/A", "N/A"),
        ("Red", "Red"),
        ("Blue", "Blue"),
        ("Green", "Green"),
        ("Black", "Black"),
        ("White", "White"),
        ("Purple", "Purple"),
        ("__custom__", "Custom / Other"),
    ]

    MATERIAL_PRESETS = [
        ("N/A", "N/A"),
        ("Plastic", "Plastic"),
        ("Metal", "Metal"),
        ("Wood", "Wood"),
        ("Resin", "Resin"),
        ("Stone", "Stone"),
        ("__custom__", "Custom / Other"),
    ]

    DICE_TYPE_PRESETS = [
        ("N/A", "N/A"),
        ("D6", "D6"),
        ("D20", "D20"),
        ("Full Set", "Full Set"),
        ("D4", "D4"),
        ("D8", "D8"),
        ("D10", "D10"),
        ("D12", "D12"),
        ("__custom__", "Custom / Other"),
    ]

    # Model fields overridden as ChoiceField with presets
    color = forms.ChoiceField(
        choices=COLOR_PRESETS,
        required=False,
        initial="N/A",
        label="Color",
    )
    material = forms.ChoiceField(
        choices=MATERIAL_PRESETS,
        required=False,
        initial="N/A",
        label="Material",
    )
    dice_type = forms.ChoiceField(
        choices=DICE_TYPE_PRESETS,
        required=False,
        initial="N/A",
        label="Dice Type",
    )

    # Extra fields for custom values
    color_custom = forms.CharField(
        max_length=30,
        required=False,
        label="Custom color",
    )
    material_custom = forms.CharField(
        max_length=30,
        required=False,
        label="Custom material",
    )
    dice_type_custom = forms.CharField(
        max_length=30,
        required=False,
        label="Custom dice type",
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "stock",
            "image",
            "color",
            "material",
            "dice_type",
        ]

    def clean_color(self):
        value = self.cleaned_data.get("color")
        custom = (self.cleaned_data.get("color_custom") or "").strip()

        if value == "__custom__":
            if not custom:
                raise ValidationError("Please enter a custom color.")
            return custom
        return value or "N/A"

    def clean_material(self):
        value = self.cleaned_data.get("material")
        custom = (self.cleaned_data.get("material_custom") or "").strip()

        if value == "__custom__":
            if not custom:
                raise ValidationError("Please enter a custom material.")
            return custom
        return value or "N/A"

    def clean_dice_type(self):
        value = self.cleaned_data.get("dice_type")
        custom = (self.cleaned_data.get("dice_type_custom") or "").strip()

        if value == "__custom__":
            if not custom:
                raise ValidationError("Please enter a custom dice type.")
            return custom
        return value or "N/A"

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment', 'address']
        widgets = {
            'payment': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
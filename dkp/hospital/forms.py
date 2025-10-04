from django import forms
from django.contrib.sites.models import Site
from .models import Hospital, Ward, OperatingRoom


class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'short_name', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }


class WardForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        site_hospital = kwargs.pop('site_hospital', None)
        super().__init__(*args, **kwargs)

        # For non-superusers, make hospital field disabled and set initial value
        if user and not user.is_superuser:
            if site_hospital:
                self.fields['hospital'].initial = site_hospital
                self.fields['hospital'].queryset = Hospital.objects.filter(pk=site_hospital.pk)
            self.fields['hospital'].widget.attrs['disabled'] = True
            self.fields['hospital'].required = False

    def clean_hospital(self):
        # If hospital field is disabled, use the instance's hospital or initial value
        if 'hospital' in self.fields and self.fields['hospital'].widget.attrs.get('disabled'):
            if self.instance and self.instance.pk:
                return self.instance.hospital
            return self.fields['hospital'].initial
        return self.cleaned_data['hospital']

    class Meta:
        model = Ward
        fields = ['name', 'hospital', 'nurse_telephone', 'surgeon_telephone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-select'}),
            'nurse_telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'surgeon_telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class OperatingRoomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        site_hospital = kwargs.pop('site_hospital', None)
        super().__init__(*args, **kwargs)

        # For non-superusers, make hospital field disabled and set initial value
        if user and not user.is_superuser:
            if site_hospital:
                self.fields['hospital'].initial = site_hospital
                self.fields['hospital'].queryset = Hospital.objects.filter(pk=site_hospital.pk)
            self.fields['hospital'].widget.attrs['disabled'] = True
            self.fields['hospital'].required = False

    def clean_hospital(self):
        # If hospital field is disabled, use the instance's hospital or initial value
        if 'hospital' in self.fields and self.fields['hospital'].widget.attrs.get('disabled'):
            if self.instance and self.instance.pk:
                return self.instance.hospital
            return self.fields['hospital'].initial
        return self.cleaned_data['hospital']

    class Meta:
        model = OperatingRoom
        fields = ['name', 'hospital']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-select'}),
        }
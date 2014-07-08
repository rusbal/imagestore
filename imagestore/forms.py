#!/usr/bin/env python
# vim:fileencoding=utf-8
try:
    import autocomplete_light
    AUTOCOMPLETE_LIGHT_INSTALLED = True
except ImportError:
    AUTOCOMPLETE_LIGHT_INSTALLED = False

__author__ = 'zeus'

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

import zipfile

from models import Image, Album


class ImageForm(forms.ModelForm):
    class Meta(object):
        model = Image
        exclude = ('user', 'order')

    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'cols': 19}), required=False,
                                  label=_('Description'))

    def __init__(self, user, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields['album'].queryset = Album.objects.filter(user=user)
        self.fields['album'].required = True
        if AUTOCOMPLETE_LIGHT_INSTALLED:
            self.fields['tags'].widget = autocomplete_light.TextWidget('TagAutocomplete')


class AlbumForm(forms.ModelForm):
    class Meta(object):
        model = Album
        exclude = ('user', 'created', 'updated')

    def __init__(self, *args, **kwargs):
        super(AlbumForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['head'].queryset = Image.objects.filter(album=kwargs['instance'])
        else:
            self.fields['head'].widget = forms.HiddenInput()


class AlbumOwnerChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name_with_owner()


class AlbumOwnerMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name_with_owner()


class ImageAdminForm(forms.ModelForm):

    class Meta:
        model = Image

    def __init__(self, *args, **kwargs):
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        self.fields['albums'] = AlbumOwnerMultipleChoiceField(
            queryset=Album.objects.all().order_by('user__first_name', 'name'))

    def clean_albums(self):
        msgs = []
        user = None
        with_error = False

        data = self.cleaned_data

        for album in data['albums']:
            if user is None:
                user = album.user
            if user == album.user:
                msgs.append({'valid': True, 'user': album.user.get_full_name(), 'name': album.name})
            else:
                msgs.append({'valid': False, 'user': album.user.get_full_name(), 'name': album.name})
                with_error = True

        if with_error:
            valid_msg = ""
            invalid_msg = ""
            for msg in msgs:
                if msg['valid']:
                    valid_msg += "Image was assigned to {0} on \"{1}\". ".format(msg['user'], msg['name'])
                else:
                    invalid_msg += "But re-assignment to {0} on \"{1}\" is not allowed. ".format(msg['user'], msg['name'])

            raise forms.ValidationError(valid_msg + invalid_msg)
        return data['albums']


class ZipImageAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ZipImageAdminForm, self).__init__(*args, **kwargs)
        self.fields['album'] = AlbumOwnerChoiceField(
            queryset=Album.objects.all().order_by('user__first_name', 'name'))
        self.fields['album'].required = False

    def clean_zip_file(self):
        data = self.cleaned_data
        if not zipfile.is_zipfile(data['zip_file'].file):
            raise forms.ValidationError("Please select a zip file.")
        return data['zip_file']



class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username


class AlbumAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AlbumAdminForm, self).__init__(*args, **kwargs)
        self.fields['user'] = UserChoiceField(
            queryset=User.objects.filter(is_active=True))

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

    def assign_image_owner(self, obj):
        messages = []
        saved_user = None
        for album in self.cleaned_data['albums']:
            if saved_user is None:
                obj.user = album.user
                obj.save()
                saved_user = album.user
                messages.append({
                    'type': 'success',
                    'message': "%s (" + album.name + ") saved as owner of this work of art.",
                    'name': album.user.get_full_name()
                })
            elif saved_user == album.user:
                # Assigned to more than one Album owned by same User
                messages.append({
                    'type': 'success',
                    'message': "%s (" + album.name + ") saved as owner of this work of art.",
                    'name': album.user.get_full_name()
                })
            else:
                # Attempt to assign to more than one Album owned by different
                # User but this is not allowed since an Image can only be owned
                # by one User.
                messages.append({
                    'type': 'warning',
                    'message': "%s (" + album.name + ") wasn't saved as owner of this work of art.",
                    'name': album.user.get_full_name()
                })
        return messages


class ZipImageAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ZipImageAdminForm, self).__init__(*args, **kwargs)
        self.fields['album'] = AlbumOwnerChoiceField(
            queryset=Album.objects.all().order_by('user__first_name', 'name'))
        self.fields['album'].required = False


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username


class AlbumAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AlbumAdminForm, self).__init__(*args, **kwargs)
        self.fields['user'] = UserChoiceField(
            queryset=User.objects.filter(is_active=True))

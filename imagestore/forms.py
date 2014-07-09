#!/usr/bin/env python
# vim:fileencoding=utf-8
try:
    import autocomplete_light
    AUTOCOMPLETE_LIGHT_INSTALLED = True
except ImportError:
    AUTOCOMPLETE_LIGHT_INSTALLED = False

__author__ = 'zeus'

import zipfile

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from sorl.thumbnail.admin.current import AdminImageWidget

from models import Image, Album


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username


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

class MediaFileWidget(forms.TextInput):
    """
    COPIED FROM FeinCMS code
    TextInput widget, shows a link to the current value if there is one.
    """

    def render(self, name, value, attrs=None):

        inputfield = super(MediaFileWidget, self).render(name, value, attrs)
        if value:
            try:
                mf = Image.objects.get(pk=value)
            except Image.DoesNotExist:
                return inputfield

            # caption = mf.title
            # image = mf.admin_thumbnail_path()
            # image = u'background: url(%(url)s) center center no-repeat;' % {'url': image}
            # return mark_safe(u"""
            #     <div style="%(image)s" class="admin-gallery-image-bg absolute">
            #     <p class="admin-gallery-image-caption absolute">%(caption)s</p>
            #     %(inputfield)s</div>""" % {
            #         'image': image,
            #         'caption': caption,
            #         'inputfield': inputfield})

            return mark_safe(mf.admin_thumbnail())

        return inputfield


class InlineImageForm(forms.ModelForm):
    mediafile = forms.ModelChoiceField(queryset=Image.objects.all(),
                                       widget=MediaFileWidget(attrs={'class': 'image-fk'}),
                                       label=_('image file'),
                                       required=False)
    order = forms.IntegerField(label=_('order'),
                               required=False)

    class Meta:
        model = Image

    def __init__(self, *args, **kwargs):
        super(InlineImageForm, self).__init__(*args, **kwargs)
        try:
            image = Image.objects.get(pk=self.instance.image_id)
            self.fields["mediafile"].initial = image.pk
        except:
            pass


class ImageAdminForm(forms.ModelForm):

    class Meta:
        model = Image

    def __init__(self, *args, **kwargs):
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['user'] = UserChoiceField(
            queryset=User.objects.filter(is_active=True))
        self.fields['user'].required = False


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


class AlbumAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AlbumAdminForm, self).__init__(*args, **kwargs)
        self.fields['user'] = UserChoiceField(
            queryset=User.objects.filter(is_active=True))

#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'
from imagestore.utils import load_class, get_model_string
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

Album = load_class(getattr(settings, 'IMAGESTORE_ALBUM_MODEL', 'imagestore.models.album.Album'))
Image = load_class(getattr(settings, 'IMAGESTORE_IMAGE_MODEL', 'imagestore.models.image.Image'))

# This labels and classnames used to generate permissons labels
image_applabel = Image._meta.app_label
image_classname = Image.__name__.lower()

album_applabel = Album._meta.app_label
album_classname = Album.__name__.lower()


from upload import AlbumUpload


class AlbumImage(models.Model):
    album = models.ForeignKey(Album)
    image = models.ForeignKey(Image)
    order = models.IntegerField(_('Order'), default=0)

    class Meta:
        db_table = 'imagestore_album_images'
        ordering = ('order',)

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = 0
        super(AlbumImage, self).save(*args, **kwargs)

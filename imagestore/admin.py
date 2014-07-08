from django.contrib import admin
from imagestore.models import Image, Album, AlbumUpload
from sorl.thumbnail.admin import AdminInlineImageMixin
from django.conf import settings

from forms import AlbumAdminForm, ImageAdminForm, ZipImageAdminForm, InlineImageForm
from helpers.string import reverse_slug


class InlineImageAdmin(AdminInlineImageMixin, admin.TabularInline):
    form = InlineImageForm
    model = Image.albums.through
    fields = ('mediafile', 'image')
    extra = 0


class AlbumAdmin(admin.ModelAdmin):
    form = AlbumAdminForm
    fieldsets = ((None, {'fields': ['name', 'user', 'is_public', 'order']}),)
    list_display = ('name', 'admin_thumbnail', 'user', 'is_public', 'order', 'created', 'updated')
    list_editable = ('order', )
    inlines = [InlineImageAdmin]

admin.site.register(Album, AlbumAdmin)


class ImageAdmin(admin.ModelAdmin):
    form = ImageAdminForm
    fieldsets = ((None, {'fields': ['image', 'albums', 'title', 'description', 'order', 'tags']}),)
    list_display = ('admin_thumbnail', 'title', 'user', 'order')
    list_editable = ('order', )
    list_filter = ('user', 'albums', )

    def save_model(self, request, obj, form, change):
        """
        Assign filename as title if not supplied
        """
        if not obj.title:
            obj.title = reverse_slug(request.FILES['image'].name, remove_extension=True, title=True)
            print obj.title

        if not change:
            """
            Use owner of first album associated with this image to be the owner of this image
            """
            album_id = request.POST['albums']
            album = Album.objects.get(pk=album_id)
            obj.user = album.user
        obj.save()


class AlbumUploadAdmin(admin.ModelAdmin):
    form = ZipImageAdminForm

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

IMAGE_MODEL = getattr(settings, 'IMAGESTORE_IMAGE_MODEL', None)
if not IMAGE_MODEL:
    admin.site.register(Image, ImageAdmin)

ALBUM_MODEL = getattr(settings, 'IMAGESTORE_ALBUM_MODEL', None)
if not ALBUM_MODEL:
    admin.site.register(AlbumUpload, AlbumUploadAdmin)

from django.contrib import admin
from imagestore.models import Image, Album, AlbumUpload
from sorl.thumbnail.admin import AdminInlineImageMixin
from django.conf import settings
from django.contrib import messages

from forms import AlbumAdminForm, ImageAdminForm, ZipImageAdminForm


class InlineImageAdmin(AdminInlineImageMixin, admin.TabularInline):
    model = Image.albums.through
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
    list_filter = ('albums', )

    def save_model(self, request, obj, form, change):
        obj.save()
        msgs = form.assign_image_owner(obj)
        for msg in msgs:
            message = msg['message']
            name = msg['name']
            if msg['type'] == 'success':
                messages.success(request, message % ('"' + name + '"'))
            else:
                messages.warning(request, message % ('"' + name + '"'))


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

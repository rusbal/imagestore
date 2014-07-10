from django.contrib import admin
from django.conf import settings
from django.db.models import Count
from sorl.thumbnail.admin import AdminInlineImageMixin

from imagestore.models import Image, Album, AlbumUpload, AlbumImage
from forms import AlbumAdminForm, ImageAdminForm, ZipImageAdminForm, InlineImageForm
from helpers.string import reverse_slug


class InlineImageAdmin(AdminInlineImageMixin, admin.TabularInline):
    form = InlineImageForm
    model = AlbumImage
    fields = ('mediafile', 'image', 'order')
    extra = 0


class AlbumAdmin(admin.ModelAdmin):
    form = AlbumAdminForm
    fields = ('name', 'user', 'is_public', 'order')
    list_display = ('name', 'owner', 'admin_thumbnail', 'image_count', 'is_public', 'order')
    list_editable = ('order', )
    list_filter = ('user',)
    inlines = [InlineImageAdmin]

    def owner(self, obj):
        return obj.user.get_full_name()

    def queryset(self, request):
        return Album.objects.annotate(image_count=Count('images'))

    def image_count(self, inst):
        return inst.image_count
    image_count.admin_order_field = 'image_count'

admin.site.register(Album, AlbumAdmin)


class ImageAdmin(admin.ModelAdmin):
    form = ImageAdminForm
    fieldsets = ((None, {'fields': ['image', 'title', 'description', 'user', 'tags']}),)
    list_display = ('admin_thumbnail', 'title', 'user')
    list_filter = ('user', 'albums', )
    list_editable = ('title', 'user', )

    def save_model(self, request, obj, form, change):
        """
        Assign filename as title if not supplied
        """
        if not obj.title:
            obj.title = reverse_slug(request.FILES['image'].name, remove_extension=True, title=True)

        if not obj.user:
            obj.user = request.user
        obj.save()


class AlbumUploadAdmin(admin.ModelAdmin):
    form = ZipImageAdminForm
    fields = ('zip_file', ('new_album_name', 'user'), 'album', 'tags')

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

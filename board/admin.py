from django.contrib import admin

from .models import Post, Reply, Img, File
# Register your models here.
class ImgInline(admin.TabularInline):
    model = Img

class FileInline(admin.TabularInline):
    model = File

class PostAdmin(admin.ModelAdmin):
    inlines = [ImgInline, FileInline, ]

admin.site.register(Post, PostAdmin)
admin.site.register(Reply)
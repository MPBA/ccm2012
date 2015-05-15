from django.contrib import admin

from .models import MyChunkedUpload


class UploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'file', 'upload_id', 'completed_on']

admin.site.register(MyChunkedUpload, UploadAdmin)
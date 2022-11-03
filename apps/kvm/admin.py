from django.contrib import admin
from .models import VmInstance

# Register your models here.


@admin.register(VmInstance)
class AuthorAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        print(54555)


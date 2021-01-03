from django.contrib import admin

from todoapi.models import Todo


class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'user', 'is_finished')
    list_filter = ('user', 'is_finished')
    search_fields = ['title', 'content']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Todo, TodoAdmin)

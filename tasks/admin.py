from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'is_completed', 'due_date', 'created_at')
    list_filter = ('is_completed', 'priority', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'user__username')
    filter_horizontal = ('categories', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description')
        }),
        ('Task Details', {
            'fields': ('priority', 'due_date', 'is_completed')
        }),
        ('Categories & Tags', {
            'fields': ('categories', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

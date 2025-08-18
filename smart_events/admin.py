from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Event, Comment, Like, BirthdayMessage, BirthdayMessageUsed, QuoteMessageUsed, QuoteMessage

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'date', 'time', 'created_at')
    list_filter = ('type', 'date')
    search_fields = ('title', 'description')
    ordering = ('-date', 'time')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_id', 'employee_id', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text',)
    ordering = ('-created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_id', 'employee_id', 'created_at')
    list_filter = ('event_id', 'employee_id')
    search_fields = ('event_id', 'employee_id')
    ordering = ('-created_at',)

class BirthdayMessageResource(resources.ModelResource):
    def skip_row(self, instance, original, row, import_validation_errors=None):
        return not row.get("text_ru") or not row.get("text_kz")

    class Meta:
        model = BirthdayMessage
        fields = ('id', 'text_ru', 'text_kz')
        import_id_fields = ('id',)


@admin.register(BirthdayMessage)
class BirthdayMessageAdmin(ImportExportModelAdmin):
    resource_class = BirthdayMessageResource
    list_display = ("short_text_ru", "short_text_kz")
    search_fields = ("text_ru", "text_kz")

    def short_text_ru(self, obj):
        return obj.text_ru[:50] + ("..." if len(obj.text_ru) > 50 else "")
    short_text_ru.short_description = "Текст (RU)"

    def short_text_kz(self, obj):
        return obj.text_kz[:50] + ("..." if len(obj.text_kz) > 50 else "")
    short_text_kz.short_description = "Мәтін (KZ)"


@admin.register(BirthdayMessageUsed)
class BirthdayMessageUsedAdmin(admin.ModelAdmin):
    list_display = ('birthday_employee_id', 'birth_year', 'message_preview', 'created_at')
    search_fields = ('birthday_employee_id', 'birth_year')
    list_filter = ('birth_year',)

    def message_preview(self, obj):
        return obj.message.text_ru[:50] + ("..." if len(obj.message.text_ru) > 50 else "")
    message_preview.short_description = "Поздравление (RU)"

@admin.register(QuoteMessage)
class QuoteMessageAdmin(ImportExportModelAdmin):
    list_display = ("short_text_ru", "short_text_kz")
    search_fields = ("text_ru", "text_kz")

    def short_text_ru(self, obj):
        return obj.text_ru[:50] + ("..." if len(obj.text_ru) > 50 else "")
    short_text_ru.short_description = "Цитата (RU)"

    def short_text_kz(self, obj):
        return obj.text_kz[:50] + ("..." if len(obj.text_kz) > 50 else "")
    short_text_kz.short_description = "Цитата (KZ)"


@admin.register(QuoteMessageUsed)
class QuoteMessageUsedAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "date_used", "message", "created_at")
    list_filter = ("date_used",)
    search_fields = ("employee_id",)
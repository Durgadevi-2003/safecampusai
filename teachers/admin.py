from django.contrib import admin
from .models import Teacher,CounselingSession
# Register your models here.
admin.register(Teacher)
 
@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = ("student", "teacher", "session_date", "mode", "status")
    list_filter = ("mode", "status")
    search_fields = ("student__name", "teacher__username")



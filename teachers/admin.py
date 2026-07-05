from django.contrib import admin

from .models import TeacherCertificate, TeacherProfile


class TeacherCertificateInline(admin.TabularInline):
    model = TeacherCertificate
    extra = 0


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'approval_status', 'experience_years', 'average_rating', 'created_at')
    list_filter = ('approval_status', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'headline')
    inlines = [TeacherCertificateInline]


@admin.register(TeacherCertificate)
class TeacherCertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher_profile', 'issuing_organization', 'uploaded_at')
    search_fields = ('title', 'issuing_organization', 'teacher_profile__user__email')

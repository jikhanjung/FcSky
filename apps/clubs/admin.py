from django.contrib import admin

from .models import Club, ClubMembership


class ClubMembershipInline(admin.TabularInline):
    model = ClubMembership
    extra = 0
    autocomplete_fields = ["user"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ClubMembershipInline]


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ["club", "user", "role"]
    list_filter = ["role", "club"]
    autocomplete_fields = ["user", "club"]
    search_fields = ["user__username", "club__name"]

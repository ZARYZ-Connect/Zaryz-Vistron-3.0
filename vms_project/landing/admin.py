from django.contrib import admin
from django.utils.html import format_html
from .models import FAQ, GuideVideo, PricingPlan, ContactSubmission, BlogPost


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display  = ('question','category','order','is_published','updated_at')
    list_editable = ('is_published','order')
    list_filter   = ('is_published','category')
    search_fields = ('question','answer')
    ordering      = ('order',)
    actions       = ['publish','unpublish']

    @admin.action(description="Publish selected FAQs")
    def publish(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description="Unpublish selected FAQs")
    def unpublish(self, request, queryset):
        queryset.update(is_published=False)


@admin.register(GuideVideo)
class GuideVideoAdmin(admin.ModelAdmin):
    list_display    = ('title','preview_thumbnail','duration_label',
                       'order','is_published')
    list_editable   = ('is_published','order')
    readonly_fields = ('youtube_id','thumbnail_url','preview_thumbnail')
    search_fields   = ('title','description')

    def preview_thumbnail(self, obj):
        if obj.thumbnail_url:
            return format_html(
                '<img src="{}" width="120" style="border-radius:6px"/>',
                obj.thumbnail_url
            )
        return "—"
    preview_thumbnail.short_description = "Thumbnail"


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display  = ('name','monthly_price','yearly_price',
                     'currency','is_highlighted','is_published','order')
    list_editable = ('is_published','order','is_highlighted')
    ordering      = ('order',)

    def save_model(self, request, obj, form, change):
        if obj.is_highlighted:
            PricingPlan.objects.exclude(pk=obj.pk).update(is_highlighted=False)
        super().save_model(request, obj, form, change)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display    = ('full_name','email','subject','status','created_at')
    list_filter     = ('status',)
    list_editable   = ('status',)
    search_fields   = ('full_name','email','subject','message')
    readonly_fields = ('full_name','email','subject','message',
                       'ip_address','created_at')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display       = ('title', 'slug', 'is_published', 'created_at')
    list_editable      = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields      = ('title', 'content', 'excerpt')
    list_filter        = ('is_published', 'created_at')

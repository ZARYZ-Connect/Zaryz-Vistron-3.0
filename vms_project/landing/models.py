import re
from django.db import models


class FAQ(models.Model):
    question     = models.CharField(max_length=500)
    answer       = models.TextField(help_text="Supports Markdown")
    category     = models.CharField(max_length=100, blank=True)
    is_published = models.BooleanField(default=False)
    order        = models.PositiveIntegerField(default=0, db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class GuideVideo(models.Model):
    title          = models.CharField(max_length=255)
    description    = models.TextField(blank=True)
    youtube_url    = models.URLField(help_text="Paste any YouTube URL")
    youtube_id     = models.CharField(max_length=50, editable=False)
    thumbnail_url  = models.URLField(editable=False)
    duration_label = models.CharField(max_length=20, blank=True,
                                      help_text='e.g. "3:45"')
    is_published   = models.BooleanField(default=False)
    order          = models.PositiveIntegerField(default=0, db_index=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Guide Video"

    def save(self, *args, **kwargs):
        patterns = [
            r'youtube\.com/watch\?v=([^&]+)',
            r'youtu\.be/([^?]+)',
            r'youtube\.com/embed/([^?]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                self.youtube_id = match.group(1)
                break
        self.thumbnail_url = (
            f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg"
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PricingPlan(models.Model):
    CURRENCY_CHOICES = [('USD','USD'),('INR','INR'),('EUR','EUR')]

    name           = models.CharField(max_length=100)
    monthly_price  = models.DecimalField(max_digits=10, decimal_places=2,
                                         null=True, blank=True,
                                         help_text="Leave blank = Contact Us")
    yearly_price   = models.DecimalField(max_digits=10, decimal_places=2,
                                         null=True, blank=True)
    currency       = models.CharField(max_length=10,
                                      choices=CURRENCY_CHOICES, default='USD')
    billing_note   = models.CharField(max_length=100, blank=True)
    features       = models.JSONField(default=list)
    cta_label      = models.CharField(max_length=100, default="Get Started")
    cta_url        = models.URLField(blank=True)
    is_highlighted = models.BooleanField(default=False)
    is_published   = models.BooleanField(default=True)
    order          = models.PositiveIntegerField(default=0, db_index=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Pricing Plan"

    def __str__(self):
        return self.name


class ContactSubmission(models.Model):
    STATUS = [
        ('new','New'), ('read','Read'),
        ('replied','Replied'), ('archived','Archived'),
    ]
    full_name  = models.CharField(max_length=255)
    email      = models.EmailField()
    phone      = models.CharField(max_length=50, blank=True)
    company    = models.CharField(max_length=255, blank=True)
    subject    = models.CharField(max_length=255, blank=True)
    message    = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status     = models.CharField(max_length=20, choices=STATUS,
                                  default='new', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Submission"

    def __str__(self):
        return f"{self.full_name} — {self.status}"


class BlogPost(models.Model):
    title        = models.CharField(max_length=255)
    slug         = models.SlugField(unique=True, max_length=255)
    author       = models.CharField(max_length=100, default="Zaryz Team")
    content      = models.TextField(help_text="Supports HTML/Markdown")
    excerpt      = models.TextField(max_length=500, blank=True)
    featured_img = models.ImageField(upload_to='blog/featured/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blog Post"

    def __str__(self):
        return self.title

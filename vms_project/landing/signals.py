from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import FAQ, GuideVideo, PricingPlan

CACHE_KEY = "landing_page_data"

@receiver([post_save, post_delete], sender=FAQ)
@receiver([post_save, post_delete], sender=GuideVideo)
@receiver([post_save, post_delete], sender=PricingPlan)
def invalidate_landing_cache(sender, **kwargs):
    cache.delete(CACHE_KEY)

from modeltranslation.translator import register, TranslationOptions
from .models import Category, Governorate, Banner, SiteSettings, Product

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Governorate)
class GovernorateTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ('announcement_text',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'fragrance_family', 'concentration')

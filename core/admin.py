from django.contrib import admin

from . import models

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'post_preferences', 'is_staff')
    list_filter = (('is_staff', admin.BooleanFieldListFilter),
                   ('is_active', admin.BooleanFieldListFilter))

    def post_preferences(self, obj):
        return ", ".join([c.name for c in obj.preferences.all().order_by('name')])
    post_preferences.short_description = 'Preferencias'

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'location', 'city', 'address')

class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
    list_display = ('name', 'created', 'updated')

class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'status')
    list_display = ('code', 'name', 'description', 'price', 'post_categories', 'status')
    list_filter = (('status', admin.BooleanFieldListFilter),
                   'categories__name')

    def post_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all().order_by('name')])
    post_categories.short_description = 'Categorías'

class SearchAdmin(admin.ModelAdmin):
#    readonly_fields = ('id_session', 'user', 'time')
    list_display = ('id', 'id_session', 'user', 'phrase', 'time', 'category')
    list_filter = ('category__name',)

class ShoppingCartAdmin(admin.ModelAdmin):
#    readonly_fields = ('amount',)
    list_display = ('user', 'article', 'quantity', 'amount')
    list_filter = ('article__categories__name',)

class PaymentDetailsAdmin(admin.ModelAdmin):
    readonly_fields = ('status',)
    list_display = ('user', 'payment_type', 'transaction_code', 'status')
    list_filter = ('payment_type',)

class BillAdmin(admin.ModelAdmin):
    readonly_fields = ('status',)
    list_display = ('user', 'amount', 'address', 'date')

class BillDetailsAdmin(admin.ModelAdmin):
    list_display = ('bill', 'article', 'quantity', 'amount')
    list_filter = ('article__categories__name',)

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.CategoryArticle, CategoryAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.Search, SearchAdmin)
admin.site.register(models.ShoppingCart, ShoppingCartAdmin)
admin.site.register(models.PaymentDetails, PaymentDetailsAdmin)
admin.site.register(models.Bill, BillAdmin)
admin.site.register(models.BillDetails, BillDetailsAdmin)

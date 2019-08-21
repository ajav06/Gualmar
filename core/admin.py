from django.contrib import admin

from core.models import User, Address, CategoryArticle, Article, Search

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'location', 'city', 'address')


class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
    list_display = ('name', 'created', 'updated')

class ArticleAdmin(admin.ModelAdmin):
    readonly_fields = ('created', )
    list_display = ('code', 'name', 'description', 'price', 'post_categories')

    def post_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all().order_by('name')])
    post_categories.short_description = 'Categorías'

class SearchAdmin(admin.ModelAdmin):
#    readonly_fields = ('id_session', 'user', 'time')
    list_display = ('id_session', 'user', 'phrase', 'time')


admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(CategoryArticle, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Search, SearchAdmin)

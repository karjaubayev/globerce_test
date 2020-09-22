from django.contrib import admin
from credits.models import Person, BanList, Program, CreditRequest

# Register your models here.
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('iin',)
    readonly_fields = ('iin','birthday')


@admin.register(BanList)
class BanListAdmin(admin.ModelAdmin):
    list_display = ('iin',)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'min_value', 'max_value', 'min_age', 'max_age')


@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ('person','status','sum')
    list_filter = ('status',)
    readonly_fields = ('person','status','sum', 'decline')

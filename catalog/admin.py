from django.contrib import admin
from .models import Author,Book,BookInstance,Language,Genre
# Register your models here.

class BookInstanceInline(admin.TabularInline):
	model=BookInstance
	extra=0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display=['title','author','display_genre']
	inlines=[BookInstanceInline]

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
	list_display=['book','id','status','due_back','borrower']
	list_filter=['status','due_back']
	fieldsets=(
		('Description',{
			'fields':('book','imprint','id','language')
		}),
		('Availability',{
			'fields':('status','due_back','borrower')
		}),
	)

class BookInline(admin.TabularInline):
	model=Book
	extra=0	

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display=['last_name','first_name','date_of_birth','date_of_death']
	fields=['last_name','first_name',('date_of_birth','date_of_death')]
	inlines=[BookInline]

admin.site.register(Genre)
admin.site.register(Language)
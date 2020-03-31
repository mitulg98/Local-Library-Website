from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from .models import BookInstance, Author, Book
from django import forms 
import datetime

class RenewBookForm(forms.ModelForm):
	
	def clean_due_back(self):
		data=self.cleaned_data['due_back']
		if data<datetime.date.today():
			raise ValidationError(_('Invalid date - renewal in past'),code='invalid')

		if data>datetime.date.today()+datetime.timedelta(weeks=4):
			raise ValidationError(_('Invalid date - renewal more than 4 weeks from now'))

		return data

	class Meta:
		model=BookInstance
		fields=['due_back']
		labels={'due_back':_('Renewal Date')}
		help_texts={'due_back':_('Enter a date between now and 4 weeks (default 3).')}

class AuthorForm(forms.ModelForm):

	def clean(self):
		if self.cleaned_data['date_of_death']!=None and self.cleaned_data['date_of_death']<self.cleaned_data['date_of_birth']:
			raise ValidationError(_('Invalid date - death before birth!!'))

	class Meta:
		model=Author
		fields='__all__'

class BookForm(forms.ModelForm):

	class Meta:
		model=Book 
		fields='__all__'
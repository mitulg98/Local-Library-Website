from django.test import TestCase
from catalog.models import Author

class AuthorTestCase(TestCase):
	@classmethod
	def setUpTestData(cls):
		Author.objects.create(first_name='Big',last_name='Bob')

	def test_first_name_label(self):
		author=Author.objects.get(pk=1)
		first_name=author._meta.get_field('first_name').verbose_name
		self.assertEquals(first_name,'first name')

	def test_last_name_label(self):
		author=Author.objects.get(pk=1)
		last_name=author._meta.get_field('last_name').verbose_name
		self.assertEquals(last_name,'last name')

	def test_date_of_death(self):
		author=Author.objects.get(pk=1)
		date_of_death=author._meta.get_field('date_of_death').verbose_name
		self.assertEquals(date_of_death,'died')

	def test_date_of_birth(self):
		author=Author.objects.get(pk=1)
		date_of_birth=author._meta.get_field('date_of_birth').verbose_name
		self.assertEquals(date_of_birth,'date of birth')

	def test_first_name_max_length(self):
		author=Author.objects.get(pk=1)
		max_len=author._meta.get_field('first_name').max_length
		self.assertEquals(max_len,100)

	def test_object_name_is_first_name_comma_last_name(self):
		author=Author.objects.get(pk=1)
		first_name=author.first_name
		last_name=author.last_name
		self.assertEquals(f'{first_name} {last_name}',str(author))

	def test_get_absolute_url(self):
		author=Author.objects.get(pk=1)
		self.assertEquals(author.get_absolute_url(),'/catalog/author/1')

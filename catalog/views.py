from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.decorators import login_required,permission_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import render, get_object_or_404,redirect
from .forms import RenewBookForm, AuthorForm, BookForm
from .models import Book, BookInstance, Author, Genre
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.template import loader
from django.views import generic
import datetime


# Create your views here.
@login_required
def index(request):
	"""view function for the home page of the web site"""

	"""count of some important objects in database"""
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.count()

	"""count of available books (status='a')"""
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()

	num_authors = Author.objects.count()
	num_genres = Genre.objects.count()

	num_visits = request.session.get('num_visits',0)
	request.session['num_visits']=num_visits+1

	request.session.set_expiry(0)

	context={
		'num_books':num_books,
		'num_instances':num_instances,
		'num_instances_available':num_instances_available,
		'num_authors':num_authors,
		'num_genres':num_genres,
		'num_visits':num_visits,
	}

	template = loader.get_template('catalog/index.html')
	return HttpResponse(template.render(context,request))

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request,pk):
	bookinstance=get_object_or_404(BookInstance,pk=pk)

	if request.method=='POST':
		renewal_form=RenewBookForm(request.POST)

		if renewal_form.is_valid():
			bookinstance.due_back = renewal_form.cleaned_data['due_back']
			bookinstance.save()
			return redirect(reverse('all-borrowed'))

	else:
		proposed_renewal_date=datetime.date.today()+datetime.timedelta(weeks=3)
		renewal_form=RenewBookForm({'due_back':proposed_renewal_date})

	context={
		'book':bookinstance,
		'form':renewal_form,
	}
	return render(request,'catalog/book_renewal_librarian.html',context)

@permission_required('catalog.can_mark_returned')
def create_author(request):

	if request.method=="POST":
		form=AuthorForm(request.POST)

		if form.is_valid():
			new_author=form.save()
			return redirect(reverse('author-detail',args=[(new_author.pk)]))

	else:
		initial_date_of_death=datetime.date.today()
		initial_date_of_birth=datetime.date.today()
		data={'date_of_birth':initial_date_of_birth,'date_of_death':initial_date_of_death}
		form=AuthorForm()

	context={
		'form':form
	}
	return render(request,'catalog/author_create_form.html',context)

@permission_required('catalog.can_mark_returned')
def update_author(request,pk):
	author=get_object_or_404(Author,pk=pk)

	if request.method=="POST":
		form=AuthorForm(request.POST,instance=author)

		if form.is_valid():
			form.save()
			return redirect(reverse('author-detail',args=[(author.pk)]))

	else:
		form=AuthorForm(instance=author)

	context={
		'author':author,
		'form':form
	}
	return render(request,'catalog/author_update_form.html',context)

@permission_required('catalog.can_mark_returned')
def create_book(request):

	if request.method=="POST":
		form=BookForm(request.POST)

		if form.is_valid():
			new_book=form.save(commit=False)
			new_book.save()
			new_book.save_m2m()
			return redirect(reverse('book-detail',args=[(new_book.pk)]))

	else:
		form=BookForm()

	context={
		'form':form
	}
	return render(request,'catalog/book_create_form.html',context)

class BookListView(LoginRequiredMixin,generic.ListView):

	model=Book
	template_name='catalog/books.html'
	context_object_name='my_book_list'

class BookDetailView(LoginRequiredMixin,generic.DetailView):

	model=Book

class AuthorListView(LoginRequiredMixin,generic.ListView):

	model=Author
	template_name='catalog/author.html'
	context_object_name='author_list'

	def get_queryset(self):
		return Author.objects.all().order_by('first_name')

class AuthorDetailView(LoginRequiredMixin,generic.DetailView):

	model=Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):

	model=BookInstance
	template_name="catalog/bookinstance_list_borrowed_user.html"
	paginate_by=10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllBorrowedBooksListView(PermissionRequiredMixin,generic.ListView):

	model=BookInstance
	template_name="catalog/all_borrowed_books.html"
	paginate_by=10
	permission_required='catalog.can_mark_returned'

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')

class AuthorDelete(DeleteView,PermissionRequiredMixin):

	model=Author
	success_url=reverse_lazy('author')
	template_name_suffix='_delete_form'

class BookUpdate(UpdateView,PermissionRequiredMixin):

	model=Book
	fields='__all__'
	template_name_suffix='_update_form'

class BookDelete(DeleteView,PermissionRequiredMixin):

	model=Book
	success_url=reverse_lazy('books')
	template_name_suffix='_delete_form'
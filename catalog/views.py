from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.decorators import login_required,permission_required
from .forms import RenewBookForm, AuthorForm, BookForm, UserRegistrationForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404,redirect
from django.utils.encoding import force_bytes, force_text
from .models import Book, BookInstance, Author, Genre
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail
from .tokens import account_activation_token
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.template import loader
from django.views import generic
import datetime


# Create your views here.
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

def register(request): 

	if request.method == 'POST':
		registration_form = UserRegistrationForm(request.POST)

		if(registration_form.is_valid()):
			user = registration_form.save(commit=False)
			user.is_active = False
			user.save()
			mail_subject = 'Email verification for Local Library Website'
			current_site = get_current_site(request)
			message = render_to_string('catalog/email_template.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
        	})
			to_email = registration_form.cleaned_data['email']
			send_mail(mail_subject, message, None, [to_email])
			return render(request, 'catalog/email_sent.html')

	else: 
		registration_form = UserRegistrationForm()
		
	context = {
		'form': registration_form
	}	
	return render(request, 'catalog/register.html', context)

def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.save()
		login(request, user)
	
	return render(request, 'catalog/registration_completed.html')

@permission_required('catalog.can_mark_returned', raise_exception=True)
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

@permission_required('catalog.can_mark_returned', raise_exception=True)
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

@permission_required('catalog.can_mark_returned', raise_exception=True)
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

@permission_required('catalog.can_mark_returned', raise_exception=True)
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

class AuthorDelete(PermissionRequiredMixin,DeleteView):

	model=Author
	success_url=reverse_lazy('author')
	template_name_suffix='_delete_form'
	permission_required='catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin,UpdateView):

	model=Book
	fields='__all__'
	template_name_suffix='_update_form'
	permission_required='catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin,DeleteView):

	model=Book
	success_url=reverse_lazy('books')
	template_name_suffix='_delete_form'
	permission_required='catalog.can_mark_returned'
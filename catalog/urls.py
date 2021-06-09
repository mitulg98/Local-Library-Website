from django.urls import path, include
from . import views

urlpatterns = [
	path('',views.index,name='index'),
	path('register/',views.register,name='register'),
	path('activate/<uidb64>/<token>/', views.activate, name='activate'),
	path('books/',views.BookListView.as_view(),name='books'),
	path('book/create/',views.create_book,name='book-create'),
	path('authors/',views.AuthorListView.as_view(),name='author'),
	path('author/create/',views.create_author,name='author-create'),
	path('book/<int:pk>',views.BookDetailView.as_view(),name='book-detail'),
	path('author/update/<int:pk>',views.update_author,name='author-update'),
	path('book/update/<int:pk>',views.BookUpdate.as_view(),name='book-update'),
	path('book/delete/<int:pk>',views.BookDelete.as_view(),name='book-delete'),
	path('author/<int:pk>',views.AuthorDetailView.as_view(),name='author-detail'),
	path('mybooks/',views.LoanedBooksByUserListView.as_view(),name='my-borrowed'),
	path('allbooks/',views.AllBorrowedBooksListView.as_view(),name='all-borrowed'),
	path('author/delete/<int:pk>',views.AuthorDelete.as_view(),name='author-delete'),
	path('book/<uuid:pk>/renew/',views.renew_book_librarian,name='renew-book-librarian'),
]
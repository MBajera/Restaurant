"""coderslab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from exercises_app.views import (HomeView, ErrorView, RestaurantListView, RestaurantView, MenuListView, MenuView,
                                 AddRestaurantView, RestaurantUnauthorisedView, AddRestaurantMenuView,
                                 ModifyRestaurantMenuView, DeleteRestaurantMenuView, DishView, AddNewDishView,
                                 ModifyDishView, RemoveFromMenuView, AddExistingDishToMenuView, LoginView, LogoutView,
                                 AddUserView, UserPanelView, UserRestaurantsView, UserRestaurantNotesView,
                                 UserRestaurantNoteDeleteView, UserReservationsView, ContactView, RestaurantAuthorisedView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('error/', ErrorView.as_view(), name='error'),
    path('restaurant/', RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurant/<int:pk>/', RestaurantView.as_view(), name='restaurant'),
    path('menu/', MenuListView.as_view(), name='menu-list'),
    path('menu/<int:pk>/', MenuView.as_view(), name='menu'),
    path('user_panel/restaurants/add', AddRestaurantView.as_view(), name='restaurant-add'),
    path('user_panel/restaurant/<int:pk>/unauthorized/', RestaurantUnauthorisedView.as_view(), name='restaurant-auth'),
    #dopisanie autoryzacji
    path('user_panel/restaurant/<int:pk>/authorized/', RestaurantAuthorisedView.as_view(), name='restaurant-autPL'),
    path('user_panel/restaurants/<int:pk>/menu/add', AddRestaurantMenuView.as_view(), name='menu-add'),
    path('user_panel/menu/<int:pk>/', ModifyRestaurantMenuView.as_view(), name='menu-modify'),
    path('user_panel/menu/<int:pk>/delete/', DeleteRestaurantMenuView.as_view(), name='menu-delete'),
    path('user_panel/dish/<int:pk>', DishView.as_view(), name='dish'),
    path('user_panel/menu/<int:pk>/dish/add', AddNewDishView.as_view(), name='dish-add'),
    path('user_panel/dish/<int:pk>/modify', ModifyDishView.as_view(), name='dish-modify'),
    path('user_panel/menu/<int:m_pk>/dish/<int:d_pk>/remove', RemoveFromMenuView.as_view(), name='dish-menu-remove'),
    path('user_panel/menu/<int:pk>/dish/add_existing', AddExistingDishToMenuView.as_view(), name='dish-add-existing'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('add_user/', AddUserView.as_view(), name='add-user'),
    path('user_panel/', UserPanelView.as_view(), name='user-panel'),
    path('user_panel/restaurants/', UserRestaurantsView.as_view(), name='user-restaurants'),
    path('user_panel/restaurants/<int:pk>/notes', UserRestaurantNotesView.as_view(), name='restaurant-notes'),
    path('user_panel/note/<int:pk>/delete', UserRestaurantNoteDeleteView.as_view(), name='restaurant-note-delete'),
    #może byc do skasowania
    path('user_panel/reservations/', UserReservationsView.as_view(), name='user-reservations'),
    path('restaurant/<int:pk>/contact/', ContactView.as_view(), name='contact'),
]

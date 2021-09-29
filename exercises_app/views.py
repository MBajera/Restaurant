from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Restaurant, OpeningHours, Menu, Dish, Note, Reservation
from .forms import (NoteForm, AddRestaurantForm, AddRestaurantMenuForm, ModifyRestaurantMenuForm, AddNewDishForm,
                    AddExistingDishForm, LoginForm, AddUserForm)


class HomeView(View):
    def get(self, request):
        return render(request, "home.html")


class ErrorView(View):
    def get(self, request):
        error = 'DEFEAT'
        return render(request, 'error.html', {'error':error})


class ContactView(View): #LoginRequiredMixin
    def get(self, request, pk):
        form = NoteForm()
        return render(request, "contact.html", {"form": form})

    def post(self, request, pk):
        form = NoteForm(request.POST)
        if form.is_valid():
            note = Note.objects.create(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                email=form.cleaned_data['email'],
                restaurant=Restaurant.objects.get(pk=pk),
                user=request.user
            )
            return render(request, "succesnote.html", {"note":note})
        else:
            return render(request, "contact.html", {"form": form})


class RestaurantListView(View):
    def get(self, request):
        restaurants = Restaurant.objects.filter(authorized=True) #wracam do orginału
        # restaurants = Restaurant.objects.all() #chyba tak to powinno być napisane bez tych authorized
        return render(request, "restaurantlist.html", {"restaurants": restaurants})


class RestaurantView(View):
    def get(self, request, pk):
        restaurant = Restaurant.objects.get(pk=pk)
        return render(request, "restaurant.html", {"restaurant": restaurant})


class MenuListView(View):
    def get(self, request):
        menus = Menu.objects.filter(authorized=True) #wracam do orginału
        # menus = Menu.objects.all() ##chyba tak to powinno być napisane bez tych authorized - nie jestem do konca pewny
        return render(request, "menulist.html", {"menus": menus})


class MenuView(View):
    def get(self, request, pk):
        menu = Menu.objects.get(pk=pk)
        return render(request, "menu.html", {"menu": menu})


class AddRestaurantView(View):

    def get(self, request):
        form = AddRestaurantForm()
        return render(request, "addrestaurant.html", {"form": form})

    def post(self, request):
        form = AddRestaurantForm(request.POST)
        if form.is_valid():
            restaurant = Restaurant.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
                user=request.user,
            )
            opening_hours = (
                (1, form.cleaned_data["monday_from"], form.cleaned_data["monday_to"]),
                (2, form.cleaned_data["tuesday_from"], form.cleaned_data["tuesday_to"]),
                (3, form.cleaned_data["wednesday_from"], form.cleaned_data["wednesday_to"]),
                (4, form.cleaned_data["thursday_from"], form.cleaned_data["thursday_to"]),
                (5, form.cleaned_data["friday_from"], form.cleaned_data["friday_to"]),
                (6, form.cleaned_data["saturday_from"], form.cleaned_data["saturday_to"]),
                (7, form.cleaned_data["sunday_from"], form.cleaned_data["sunday_to"]),
            )
            for day in opening_hours:
                OpeningHours.objects.create(
                    day_of_the_week=day[0],
                    from_hour=int(day[1]),
                    to_hour=int(day[2]),
                    restaurant=restaurant
                )
            return redirect('user-restaurants')
        return render(request, "addrestaurant.html", {"form": form})


class RestaurantUnauthorisedView(View):
    def get(self, request, pk):
        restaurant = Restaurant.objects.get(pk=pk)
        if restaurant.user == request.user:
            restaurant.authorized = False
            restaurant.save()
            for menu in restaurant.menu_set.all():
                menu.authorized = False
                menu.save()
            return redirect("user-restaurants")
        return redirect("user-restaurants")

#tworzenie autoryzacji
class RestaurantAuthorisedView(View):
    def get(self, request, pk):
        restaurant = Restaurant.objects.get(pk=pk)
        if restaurant.user == request.user:
            restaurant.authorized = True
            restaurant.save()
            for menu in restaurant.menu_set.all():
                menu.authorized = False
                menu.save()
            return redirect("user-restaurants")
        return redirect("user-restaurants")


class AddRestaurantMenuView(View):

    def get(self, request, pk):
        form = AddRestaurantMenuForm()
        return render(request, "addmenu.html", {"form": form})

    def post(self, request, pk):
        form = AddRestaurantMenuForm(request.POST)
        if form.is_valid():
            Menu.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                restaurant=Restaurant.objects.get(pk=pk),
                user=request.user,
                authorized=False
            )
            return redirect('user-restaurants')
        return render(request, "addmenu.html", {"form": form})


class ModifyRestaurantMenuView(View):

    def get(self, request, pk):
        menu = Menu.objects.get(pk=pk)
        form = ModifyRestaurantMenuForm(initial={
            'name': menu.name,
            'description': menu.description,
            'authorized': menu.authorized
        })
        return render(request, "modifymenu.html", {"form": form, "menu": menu})

    def post(self, request, pk):
        menu = Menu.objects.get(pk=pk)
        form = ModifyRestaurantMenuForm(request.POST, instance=menu)
        if form.is_valid():
            menu.name = form.cleaned_data['name']
            menu.description = form.cleaned_data['description']
            if not menu.restaurant.authorized:
                if form.cleaned_data['authorized']:
                    return render(request, "modifymenu.html", {"form": form, "menu": menu,
                                                               "error":"You can not set menu to authorized "
                                                                       "when restaurant is unauthorized."})
            else:
                menu.authorized = form.cleaned_data['authorized']
            menu.save()
            return redirect('user-restaurants')
        return render(request, "modifymenu.html", {"form": form, "menu": menu})


class DeleteRestaurantMenuView(View):

    def get(self, request, pk):
        menu = Menu.objects.get(pk=pk)
        if menu.user == request.user:
            menu.delete()
            return redirect("user-restaurants")
        return redirect("user-restaurants")


class DishView(View):

    def get(self, request, pk):
        dish = Dish.objects.get(pk=pk)
        return render(request, "dish.html", {"dish":dish})


class AddNewDishView(View):

    def get(self, request, pk):
        form = AddNewDishForm()
        return render(request, "addnewdish.html", {"form": form})

    def post(self, request, pk):
        form = AddNewDishForm(request.POST)
        if form.is_valid():
            dish = Dish.objects.create(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                price=form.cleaned_data["price"],
                preparation_time=form.cleaned_data["preparation_time"],
                is_wegetarian=form.cleaned_data["is_wegetarian"],
                user=request.user,
            )
            menu = Menu.objects.get(pk=pk)
            menu.dish_set.add(dish)
            return redirect("menu-modify", pk)
        return render(request, "addnewdish.html", {"form": form})


class ModifyDishView(View):

    def get(self, request, pk):
        dish = Dish.objects.get(pk=pk)
        form = AddNewDishForm(initial={
            "name": dish.name,
            "description": dish.description,
            "price": dish.price,
            "preparation_time":dish.preparation_time,
            "is_wegetarian":dish.is_wegetarian
        })
        return render(request, "modifydish.html", {"form": form})

    def post(self, request, pk):
        dish = Dish.objects.get(pk=pk)
        form = AddNewDishForm(request.POST, instance=dish)
        if form.is_valid():
            dish.name = form.cleaned_data["name"]
            dish.description = form.cleaned_data["description"]
            dish.price = form.cleaned_data["price"]
            dish.preparation_time = form.cleaned_data["preparation_time"]
            dish.is_wegetarian = form.cleaned_data["is_wegetarian"]
            dish.save()
            return redirect("dish", dish.id)
        return render(request, "modifydish.html", {"form": form})


class RemoveFromMenuView(View):

    def get(self, request, m_pk, d_pk):
        try:
            dish = Dish.objects.get(pk=d_pk)
            menu = Menu.objects.get(pk=m_pk)
        except:
            return redirect("error")
        if dish in menu.dish_set.all():
            menu.dish_set.remove(dish)
            return redirect("menu-modify", m_pk)
        else:
            return redirect("error")


class AddExistingDishToMenuView(View):

    def get(self, request, pk):
        form = AddExistingDishForm(user=request.user)
        menu = Menu.objects.get(pk=pk)
        return render(request, "addexistingdish.html", {"form":form, "menu":menu})

    def post(self, request, pk):
        form = AddExistingDishForm(request.POST, user=request.user)
        menu = Menu.objects.get(pk=pk)
        if form.is_valid():
            dish = form.cleaned_data['dishes']
            menu.dish_set.add(dish)
            return redirect("menu-modify", pk)
        return render(request, "addexistingdish.html", {"form": form, "menu": menu})


# USER
class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            if User.objects.filter(username=username):
                user = authenticate(username=username, password=form.cleaned_data['password'])
                if user:
                    login(request, user)
                    next_url = request.GET.get("next", None)
                    if next_url is None:
                        return redirect("user-panel")
                    else:
                        return redirect(next_url)
                else:
                    return render(request, "login.html", {"form": form, "error": "Wrong password"})
            return render(request, "login.html", {"form": form, "error": "User not found"})
        else:
            return render(request, "login.html", {"form": form})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("home")


class AddUserView(View):
    def get(self, request):
        form = AddUserForm()
        return render(request, "adduser.html", {"form": form})

    def post(self, request):
        form = AddUserForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data["login"],
                first_name=form.cleaned_data['name'],
                last_name=form.cleaned_data['surname'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email']
            )
            return redirect('login')
        return render(request, "adduser.html", {"form": form})


class UserPanelView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "userpanel.html")


class UserRestaurantsView(View):

    def get(self, request):
        restaurants = Restaurant.objects.filter(user=request.user)
        return render(request, "userrestaurants.html", {"restaurants": restaurants})


#REZERWACJA USERA
class UserReservationsView(LoginRequiredMixin, View):
    def get(self, request):
        reservations = Reservation.objects.filter(user=request.user)
        return render(request, "userreservations.html", {"reservations":reservations})


class UserRestaurantNotesView(View):
    def get(self, request, pk):
        notes = Note.objects.filter(restaurant_id=pk)
        return render(request, "restaurantnotes.html", {"notes":notes})


class UserRestaurantNoteDeleteView(View):
    def get(self, request, pk):
        try:
            note = Note.objects.get(pk=pk)
        except:
            return redirect("error")
        if note.restaurant.user == request.user:
            note_restaurant = note.restaurant
            note.delete()
            return redirect("restaurant-notes", note_restaurant.id)
        else:
            return redirect("error")





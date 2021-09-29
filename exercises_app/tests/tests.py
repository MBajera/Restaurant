import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from exercises_app.models import Restaurant, Note, Menu, Dish



# Create your tests here.
@pytest.mark.django_db
def test_home_view(client):
    response = client.get(reverse("home"))
    assert response.status_code == 200\


@pytest.mark.django_db
def test_error_view(client):
    response = client.get(reverse("error"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_view_1(client, normal_user):
    response = client.post(reverse("login"), {'login': normal_user.username, 'password': 'qwe'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_view_2(client, normal_user):
    response2 = client.post(reverse("login") + "?next=/user_panel/", {'login': normal_user.username, 'password': 'qwe'})
    assert response2.status_code == 302


@pytest.mark.django_db
def test_login_view_wrong_password(client, normal_user):
    response3 = client.post(reverse("login"), {'login': normal_user.username, 'password': 'abcd2'})
    assert response3.status_code == 200
    assert response3.context["error"] == "Wrong password"


@pytest.mark.django_db
def test_login_view_no_user(client, normal_user):
    response4 = client.post(reverse("login"), {'login': "asd", 'password': 'abcd2'})
    assert response4.status_code == 200
    assert response4.context["error"] == "User not found"


@pytest.mark.django_db
def test_logout_view(client, normal_user):
    client.login(username=normal_user.username, password='qwe')
    response = client.get(reverse("logout"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_restaurant_list_view(client, fake_restaurant_db):
    restaurants = fake_restaurant_db
    response = client.get(reverse("restaurant-list"))
    assert response.status_code == 200
    for restaurant in restaurants:
        assert restaurant in response.context["restaurants"]


@pytest.mark.django_db
def test_restaurant_view(client, fake_restaurant_db):
    restaurants = fake_restaurant_db
    for restaurant in restaurants:
        response = client.get(reverse("restaurant", args=[restaurant.id]))
        assert response.status_code == 200
        assert restaurant == response.context["restaurant"]


@pytest.mark.django_db
def test_menu_list_view(client, fake_menu_db):
    menus = fake_menu_db
    response = client.get(reverse("menu-list"))
    assert response.status_code == 200
    for menu in menus:
        assert menu in response.context["menus"]


@pytest.mark.django_db
def test_menu_view(client, fake_menu_db):
    menus = fake_menu_db
    for menu in menus:
        response = client.get(reverse("menu", args=[menu.id]))
        assert response.status_code == 200
        assert menu == response.context["menu"]


@pytest.mark.django_db
def test_contact_view(client, normal_user, fake_restaurant_db):
    client.login(username=normal_user.username, password='qwe')
    restaurants = fake_restaurant_db
    for restaurant in restaurants:
        response = client.get(reverse("contact", args=[restaurant.id]))
        assert response.status_code == 200
    count = Note.objects.filter(restaurant=restaurants.first()).count()
    response = client.post(reverse("contact", args=[restaurants.first().id]), {
        "title": "title1",
        "content": "content1",
        "email": "em@a.il",
    })
    assert response.status_code == 200
    assert Note.objects.filter(restaurant=restaurants.first()).count() == count + 1
    assert response.context["note"].title == "title1"
    assert response.context["note"].content == "content1"
    assert response.context["note"].email == "em@a.il"
    assert response.context["note"].restaurant == restaurants.first()
    assert response.context["note"].user == normal_user
    response2 = client.post(reverse("contact", args=[restaurants.first().id]), {
        "title": "title1",
        "content": "content1",
        "email": "email",
    })
    assert response2.status_code == 200
    assert b"Enter a valid email address." in response2.content


@pytest.mark.django_db
def test_user_restaurants_view(client, owner_user, fake_restaurant_db):
    client.login(username=owner_user.username, password='qwe')
    restaurants = Restaurant.objects.filter(user=owner_user)
    response = client.get(reverse("user-restaurants"))
    assert response.status_code == 200
    assert restaurants.count() != 0
    for restaurant in restaurants:
        assert restaurant in response.context["restaurants"]


@pytest.mark.django_db
def test_user_restaurant_notes_view(client, owner_user, fake_note_db):
    client.login(username=owner_user.username, password='qwe')
    restaurant = Restaurant.objects.first()
    notes = Note.objects.filter(restaurant=restaurant)
    response = client.get(reverse("restaurant-notes", args=[restaurant.id]))
    assert notes.count() != 0
    assert response.status_code == 200
    for note in notes:
        assert note in response.context["notes"]


@pytest.mark.django_db
def test_user_restaurant_note_delete_view(client, owner_user, fake_note_db):
    client.login(username=owner_user.username, password='qwe')
    restaurant = Restaurant.objects.first()
    notes = Note.objects.filter(restaurant=restaurant)
    note = notes.first()
    count = notes.count()
    response = client.get(reverse("restaurant-note-delete", args=[note.id]))
    assert response.status_code == 302
    assert count - 1 == Note.objects.filter(restaurant=restaurant).count()
    assert note not in Note.objects.all()


@pytest.mark.django_db
def test_add_restaurant_view(client, owner_user, fake_restaurant_db):
    client.login(username=owner_user.username, password='qwe')
    get_response = client.get(reverse("restaurant-add"))
    assert get_response.status_code == 200
    count = Restaurant.objects.all().count()
    post_response = client.post((reverse("restaurant-add")), {
        "name": "testowa1",
        "description": "description1",
        "category": "Polish",
        "monday_from": 11,
        "monday_to": 21,
        "tuesday_from": 11,
        "tuesday_to": 21,
        "wednesday_from": 11,
        "wednesday_to": 21,
        "thursday_from": 11,
        "thursday_to": 21,
        "friday_from": 11,
        "friday_to": 21,
        "saturday_from": 11,
        "saturday_to": 21,
        "sunday_from": 11,
        "sunday_to": 21
    })
    assert post_response.status_code == 302
    assert count + 1 == Restaurant.objects.all().count()
    count2 = Restaurant.objects.all().count()
    bad_post_response = client.post((reverse("restaurant-add")), {
        "name": "testowa1",
        "description": "description1",
        "category": "Polish",
        "monday_from": 11,
        "monday_to": 21,
        "tuesday_from": 11,
        "tuesday_to": 21,
        "wednesday_from": 11,
        "wednesday_to": 10,  # wrong hour
        "thursday_from": 11,
        "thursday_to": 21,
        "friday_from": 11,
        "friday_to": 21,
        "saturday_from": 11,
        "saturday_to": 21,
        "sunday_from": 11,
        "sunday_to": 21
    })
    assert bad_post_response.status_code == 200
    assert count2 == Restaurant.objects.count()


@pytest.mark.django_db
def test_add_restaurant_menu_view(client, owner_user, fake_menu_db):
    client.login(username=owner_user.username, password='qwe')
    restaurant = Restaurant.objects.first()
    get_response = client.get(reverse("menu-add", args=[restaurant.id]))
    assert get_response.status_code == 200
    count = Menu.objects.filter(restaurant=restaurant).count()
    post_response = client.post(reverse("menu-add", args=[restaurant.id]), {
        "name": "testowe menu",
        "description": "testowe description"
    })
    assert post_response.status_code == 302
    assert count + 1 == Menu.objects.filter(restaurant=restaurant).count()
    count2 = Menu.objects.filter(restaurant=restaurant).count()
    bad_post_response = client.post(reverse("menu-add", args=[restaurant.id]), {
        "name": "",
        "description": ""
    })
    assert bad_post_response.status_code == 200
    assert count2 == Menu.objects.filter(restaurant=restaurant).count()


@pytest.mark.django_db
def test_modify_restaurant_menu_view(client, owner_user, fake_menu_db):
    client.login(username=owner_user.username, password='qwe')
    menu = Menu.objects.first()
    get_response = client.get(reverse("menu-modify", args=[menu.id]))
    assert get_response.status_code == 200
    post_response = client.post(reverse("menu-modify", args=[menu.id]), {
        "name": "name after modify",
        "description": "description after modify"
    })
    assert post_response.status_code == 302
    assert Menu.objects.get(pk=menu.id).name == "name after modify"
    assert Menu.objects.get(pk=menu.id).description == "description after modify"
    bad_post_response = client.post(reverse("menu-modify", args=[menu.id]), {
        "name": "",
        "description": "description after modify2"
    })
    assert bad_post_response.status_code == 200
    assert Menu.objects.get(pk=menu.id).description != "description after modify2"


@pytest.mark.django_db
def test_add_new_dish_view(client, owner_user, fake_menu_db):
    client.login(username=owner_user.username, password='qwe')
    menu = Menu.objects.first()
    get_response = client.get(reverse("dish-add", args=[menu.id]))
    assert get_response.status_code == 200
    count = Dish.objects.filter(menu=menu).count()
    post_response = client.post(reverse("dish-add", args=[menu.id]), {
        "name": "test dish",
        "description": "description",
        "price": 123,
        "preparation_time": 123,
        "is_wegetarian": "on"
    })
    assert post_response.status_code == 302
    assert count + 1 == Dish.objects.filter(menu=menu).count()
    count2 = Dish.objects.filter(menu=menu).count()
    bad_post_response = client.post(reverse("dish-add", args=[menu.id]), {
        "name": "",
        "description": "sdsadasd",
        "price": 123,
        "preparation_time": 123,
        "is_wegetarian": "on"
    })
    assert bad_post_response.status_code == 200
    assert count2 == Dish.objects.filter(menu=menu).count()
    count3 = Dish.objects.filter(menu=menu).count()
    bad_post_response2 = client.post(reverse("dish-add", args=[menu.id]), {
        "name": "asdasda",
        "description": "",
        "price": 123,
        "preparation_time": 123,
        "is_wegetarian": True
    })
    assert bad_post_response2.status_code == 200
    assert count3 == Dish.objects.filter(menu=menu).count()


@pytest.mark.django_db
def test_add_existing_dish_view(client, owner_user, fake_dish_db):
    client.login(username=owner_user.username, password='qwe')
    menu = Menu.objects.first()
    dish_id = Dish.objects.filter(user=owner_user).filter(~Q(menu=menu)).first().id
    get_response = client.get(reverse("dish-add-existing", args=[menu.id]))
    assert get_response.status_code == 200
    for dish in menu.dish_set.all():
        assert dish in get_response.context["menu"].dish_set.all()
    count = menu.dish_set.all().count()
    post_response = client.post(reverse("dish-add-existing", args=[menu.id]), {
        "dishes": dish_id
    })
    assert post_response.status_code == 302
    assert count + 1 == menu.dish_set.count()
    count2 = menu.dish_set.all().count()
    bad_post_response = client.post(reverse("dish-add-existing", args=[menu.id]), {
        "dishes": "asdasd"
    })
    assert bad_post_response.status_code == 200
    assert count2 == menu.dish_set.count()


@pytest.mark.django_db
def test_remove_from_menu_view(client, owner_user, fake_dish_db):
    client.login(username=owner_user.username, password='qwe')
    menu = Menu.objects.first()
    dish = menu.dish_set.first()
    count = menu.dish_set.count()
    get_response = client.get(reverse("dish-menu-remove", args=[menu.id, dish.id]))
    assert get_response.status_code == 302
    assert count - 1 == menu.dish_set.count()
    dish_id = Dish.objects.filter(user=owner_user).filter(~Q(menu=menu)).first().id
    count2 = menu.dish_set.count()
    bad_get_response = client.get(reverse("dish-menu-remove", args=[menu.id, dish_id]))
    assert bad_get_response.status_code == 302
    assert count2 == menu.dish_set.count()


@pytest.mark.django_db
def test_modify_dish_view(client, owner_user, fake_dish_db):
    client.login(username=owner_user.username, password='qwe')
    dish = Menu.objects.first().dish_set.first()
    get_response = client.get(reverse("dish-modify", args=[dish.id]))
    assert get_response.status_code == 200
    assert dish.name.encode('utf-8') in get_response.content
    assert dish.description.encode('utf-8') in get_response.content
    post_response = client.post(reverse("dish-modify", args=[dish.id]), {
        "name": "new name",
        "description": "new description",
        "price": 12141241,
        "preparation_time": 1241513251,
        "is_wegetarian": False
    })
    assert post_response.status_code == 302
    dish_after_mod = Dish.objects.get(pk=dish.id)
    assert dish_after_mod.name == "new name"
    assert dish_after_mod.description == "new description"
    assert dish_after_mod.price == 12141241
    assert dish_after_mod.preparation_time == 1241513251
    assert dish_after_mod.is_wegetarian == False
    bad_post_response = client.post(reverse("dish-modify", args=[dish.id]), {
        "name": "",
        "description": "new description2",
        "price": 12141241,
        "preparation_time": 1241513251,
        "is_wegetarian": False
    })
    assert bad_post_response.status_code == 200
    dish_after_mod2 = Dish.objects.get(pk=dish.id)
    assert dish_after_mod2.name != ""
    assert dish_after_mod2.description != "new description2"


@pytest.mark.django_db
def test_dish_view(client, owner_user, fake_dish_db):
    client.login(username=owner_user.username, password='qwe')
    dish = Dish.objects.filter(user=owner_user).first()
    response = client.get(reverse("dish", args=[dish.id]))
    assert response.status_code == 200
    assert dish == response.context["dish"]


@pytest.mark.django_db
def test_delete_restaurant_menu_view(client, owner_user, fake_menu_db):
    client.login(username=owner_user.username, password='qwe')
    restaurant = Restaurant.objects.filter(user=owner_user).first()
    menu = restaurant.menu_set.first()
    count = restaurant.menu_set.count()
    response = client.get(reverse("menu-delete", args=[menu.id]))
    assert response.status_code == 302
    assert count - 1 == restaurant.menu_set.count()


@pytest.mark.django_db
def test_restaurant_unauthorised_view(client, owner_user, fake_menu_db):
    client.login(username=owner_user.username, password='qwe')
    restaurant = Restaurant.objects.filter(user=owner_user).first()
    response = client.get(reverse("restaurant-auth", args=[restaurant.id]))
    assert response.status_code == 302
    restaurant_mod = Restaurant.objects.get(pk=restaurant.id)
    assert restaurant_mod.authorized == False
    assert restaurant_mod.menu_set.first().authorized == False


@pytest.mark.django_db
def test_restaurant_authorised_view(client, owner_user, fake_menu_db):
    client.login(username=owner_user.username, password='qwe')
    restaurant = Restaurant.objects.filter(user=owner_user).first()
    response = client.get(reverse("restaurant-autPL", args=[restaurant.id]))
    assert response.status_code == 302
    restaurant_mod = Restaurant.objects.get(pk=restaurant.id)
    assert restaurant_mod.authorized == True
    assert restaurant_mod.menu_set.first().authorized == False


@pytest.mark.django_db
def test_add_user_view(client):
    response = client.get(reverse('add-user'))
    assert response.status_code == 200
    response2 = client.post(reverse('add-user'), {
        "login": "testowy",
        "name": "testowy",
        "surname": "testowy",
        "password": "Qwert12#",
        "password2": "Qwert12#",
        "email": "test@ow.yy"
    })
    assert response2.status_code == 302


@pytest.mark.django_db
def test_add_user_view_password_dont_mach(client):
    response = client.get(reverse('add-user'))
    assert response.status_code == 200
    response3 = client.post(reverse('add-user'), {
        "login": "testowy2",
        "name": "testowy2",
        "surname": "testowy2",
        "password": "Qwert12#",
        "password2": "Qwert12#y",
        "email": "test2@ow.yy"
    })
    assert response3.status_code == 200
    assert "Passwords don&#x27;t match." in str(response3.content)


@pytest.mark.django_db
def test_add_user_view_password_length(client):
    response4 = client.post(reverse('add-user'), {
            "login": "testowy2",
            "name": "testowy2",
            "surname": "testowy2",
            "password": "Qwe",
            "password2": "Qwe",
            "email": "test2@ow.yy"
        })
    assert response4.status_code == 200
    assert b"Password must be at least 8 characters long." in response4.content


@pytest.mark.django_db
def test_add_user_view_password_uppercase(client):
    response5 = client.post(reverse('add-user'), {
        "login": "testowy2",
        "name": "testowy2",
        "surname": "testowy2",
        "password": "qwertyui",
        "password2": "qwertyui",
        "email": "test2@ow.yy"
    })
    assert response5.status_code == 200
    assert b"Password must contain at least 1 uppercase letter" in response5.content


@pytest.mark.django_db
def test_user_panel_view_normal_user(client, normal_user):
    client.login(username=normal_user.username, password='qwe')
    response = client.get(reverse('user-panel'))
    assert response.status_code == 200
    assert b"My restaurants" in response.content  #not in
    assert b"My reservations" in response.content
    client.logout()


@pytest.mark.django_db
def test_user_panel_view_owner_user(client, owner_user):
    client.login(username=owner_user.username, password='qwe')
    response2 = client.get(reverse('user-panel'))
    assert response2.status_code == 200
    assert b"My restaurants" in response2.content
    assert b"My reservations" in response2.content

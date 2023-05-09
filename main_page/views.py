from django.shortcuts import render, redirect
from .import models
from .forms import SearchForm
from telebot import TeleBot

bot = TeleBot('5913303773:AAE4uMViYX9G4qGaF-FEeiLktLR6pMva0GI', parse_mode='HTML')

# Create your views here.
def homepage(request):
    all_products = models.Product.objects.all()
    search_bar = SearchForm()
    all_categories = models.Category.objects.all()


    # создаем словарь
    context = {
        'categories': all_categories,
        'products': all_products,
        'registration': search_bar,
    }

    if request.method == "POST":
        product_find = request.POST.get('search_product')
        try:
            search_result = models.Product.objects.get(product_name=product_find)
            return redirect(f'/item/{search_result.id}')
        except:
            return redirect("/")

    # передаем во фронт
    return render(request, 'index.html', context)

def current_product(request, pk):
    category = models.Product.objects.get(id=pk)

    context = {'products': category}

    return render(request, 'current_category.html', context)

def get_exact_category(request, pk):
    all_products = models.Product.objects.filter(product_category=pk)

    return render(request, 'exact_category.html', {'products': all_products})

# получить определенный продукт
def get_exact_product(request, pk):
    product = models.Product.objects.get(id=pk)
    context = {'product': product}
    if request.method == 'POST':
        models.UserCart.objects.create(user_id=request.user.id,
                                user_product=product,
                                user_product_quantity=request.POST.get('user_product_quantity'),
                                total_for_product=product.product_price * int(request.POST.get('user_product_quantity')))
        return redirect('/cart')
    return render(request, 'exact_product.html', context)

def get_user_cart(request):
    user_cart = models.UserCart.objects.filter(user_id=request.user.id)
    context = {'cart': user_cart}
    return render(request, 'user_cart.html', context)

# оформление заказа
def complete_order(request):
    # получаем корзину пользователя
    user_cart = models.UserCart.objects.filter(user_id=request.user.id)


    # формируем сообщение для тг админа
    result_message = 'Новый заказ(сайт):\n\n'
    total_for_all_cart= 0
    for cart in user_cart:
        result_message += f'<b>{cart.user_product}</b> x {cart.user_product_quantity} = {cart.total_for_product} сум\n'
        total_for_all_cart += cart.total_for_product

    result_message += f'\n----------------------------\n<b>Итого: {total_for_all_cart} сум</b>'

    # отправляем админу сообщение в тг
    bot.send_message(1097387511, result_message)


    return redirect('/')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Order, OrderItem
from .forms import ProductForm, OrderForm, RegisterForm, LoginForm


def _get_cart(session):
    return session.get('cart', {})


def _save_cart(session, cart):
    session['cart'] = cart
    session.modified = True


def index(request):
    featured = Product.objects.filter(is_featured=True)[:6]
    categories = Category.objects.all()
    latest = Product.objects.all()[:6]
    return render(request, 'menu/index.html', {
        'featured': featured,
        'categories': categories,
        'latest': latest,
    })


def menu(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.all()
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return render(request, 'menu/menu.html', {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'menu/product_detail.html', {'product': product})


@login_required
def product_create(request):
    if not request.user.is_staff:
        messages.error(request, 'Нет прав')
        return redirect('menu:index')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Блюдо добавлено')
            return redirect('menu:menu')
    else:
        form = ProductForm()
    return render(request, 'menu/product_form.html', {'form': form, 'action': 'Добавить'})


@login_required
def product_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Нет прав')
        return redirect('menu:index')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Блюдо обновлено')
            return redirect('menu:product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'menu/product_form.html', {'form': form, 'action': 'Редактировать'})


@login_required
def product_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Нет прав')
        return redirect('menu:index')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Блюдо удалено')
        return redirect('menu:menu')
    return render(request, 'menu/product_confirm_delete.html', {'product': product})


def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = _get_cart(request.session)
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    _save_cart(request.session, cart)
    messages.success(request, f'{product.name} добавлен в корзину')
    return redirect(request.META.get('HTTP_REFERER', 'menu:menu'))


def cart_remove(request, pk):
    cart = _get_cart(request.session)
    cart.pop(str(pk), None)
    _save_cart(request.session, cart)
    return redirect('menu:cart')


def cart_view(request):
    cart = _get_cart(request.session)
    items = []
    total = 0
    for pk, qty in cart.items():
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            continue
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
    return render(request, 'menu/cart.html', {'items': items, 'total': total})


def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.warning(request, 'Корзина пуста')
        return redirect('menu:menu')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            total = 0
            for pk, qty in cart.items():
                try:
                    product = Product.objects.get(pk=pk)
                except Product.DoesNotExist:
                    continue
                total += product.price * qty
            order.total = total
            order.save()
            for pk, qty in cart.items():
                try:
                    product = Product.objects.get(pk=pk)
                except Product.DoesNotExist:
                    continue
                OrderItem.objects.create(
                    order=order, product=product,
                    quantity=qty, price=product.price,
                )
            _save_cart(request.session, {})
            return redirect('menu:order_success', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'menu/checkout.html', {'form': form})


def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'menu/order_success.html', {'order': order})


def contacts(request):
    return render(request, 'menu/contacts.html')


# ===== АВТОРИЗАЦИЯ =====
def register_view(request):
    if request.user.is_authenticated:
        return redirect('menu:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('menu:index')
    else:
        form = RegisterForm()
    return render(request, 'menu/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('menu:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'С возвращением, {user.username}!')
                return redirect('menu:index')
            else:
                messages.error(request, 'Неверный логин или пароль')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'menu/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('menu:index')
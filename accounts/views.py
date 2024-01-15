from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only
# Create your views here.

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    # reemplazamos usecretionform por el form customizado CreateUserForm solo son los 4 campos de fields
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            # form.save()
            user = form.save()
            username = form.cleaned_data.get('username')

            # hacer q el nuevo usuario sea agregado al grupo customer
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            # agregamos en campo user al Customer segun el modelo y la relacion One to One
            Customer.objects.create(
                user=user,
            )

            messages.success(request, 'Cuenta creada para ' + username)

            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):
    # usamos autenticate y login para enviar a home
    if request.method == 'POST':
       username = request.POST.get('username')
       password = request.POST.get('password')

       user = authenticate(request, username=username, password=password)
       if user is not None:
          login(request, user)
          return redirect('home')
       else:
          messages.info(request, 'Usuario o Contraseña invalidos.')

    context = {}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_orders = orders.count()
    total_customers = customers.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders': orders, 'customers': customers,
               'total_orders': total_orders, 'delivered': delivered,
               'pending': pending}

    return render(request, 'accounts/dashboard.html', context)

# configuramos la pagina de usuario para q solo un cliente vea sus pedidos
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {'orders':orders,'total_orders': total_orders, 'delivered': delivered,'pending': pending}
    return render(request,'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products': products})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)

    # query al hijo de customer, en este caso order
    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs

    context = {'customer': customer, 'orders': orders, 'order_count': order_count, 'myFilter': myFilter}
    return render(request, 'accounts/customer.html', context)


''' crea orden en una sola linea
def createOrder(request):
    form = OrderForm()
    if request.method == 'POST':
        # enviamos los datos dentro del form
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            # retornamos al mismo template
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/order_form.html', context)
'''


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    # creamos una instancia multiple, padre , hijo , y que columnas mostraremos
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    # asignamos el cliente de acuerdo a su pk como valor inicial por defecto. luego CAMBIAMOS
    # form = OrderForm(initial={'customer':customer})

    # luego creamos una instancia para el formset y luego INSTANCIAMOS
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)

    if request.method == 'POST':
        # enviamos los datos dentro del form
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            # retornamos al mismo template
            return redirect('/')

    context = {'formset': formset}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    # instanciar order con los valores de order cuanto de damos actualizar
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    # form=OrderForm()

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            # retornamos al mismo template llamador
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    # aqui usamos item porque esta es la variable que enviamos y usamos en el template {{item}}
    context = {'item': order}
    return render(request, 'accounts/delete.html', context)
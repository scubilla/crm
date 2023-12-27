from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .forms import OrderForm


# Create your views here.

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


def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products': products})


def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)

    # query al hijo de customer, en este caso order
    orders = customer.order_set.all()
    order_count = orders.count()

    context = {'customer': customer, 'orders': orders, 'order_count' : order_count}
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
def createOrder(request, pk):

    # creamos una instancia multiple, padre , hijo , y que columnas mostraremos
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra = 10 )
    customer = Customer.objects.get(id=pk)
    # asignamos el cliente de acuerdo a su pk como valor inicial por defecto. luego CAMBIAMOS
    #form = OrderForm(initial={'customer':customer})

    # luego creamos una instancia para el formset y luego INSTANCIAMOS
    formset = OrderFormSet(queryset=Order.objects.none(), instance = customer)

    if request.method == 'POST':
        # enviamos los datos dentro del form
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            # retornamos al mismo template
            return redirect('/')

    context = {'formset': formset}
    return render(request, 'accounts/order_form.html', context)


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


def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    # aqui usamos item porque esta es la variable que enviamos y usamos en el template {{item}}
    context = {'item': order}
    return render(request, 'accounts/delete.html', context)
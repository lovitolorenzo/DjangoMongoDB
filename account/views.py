from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from django.core import serializers
from web3 import Web3
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, request
from django.contrib import messages
from django.utils import timezone
from django.core import serializers
import numpy
#from itertools import chain per combinare due querystes in una lista

import random
import requests

from .forms import *

#wallet features
address = "0xf329CE0cBE53D2b66D3113D3074b8cE5E057e446"
private_key = "0x86ad07d7614d1a4db8dc4b3f7630a5eabd934dc3649fa10fbcbb853324821e44"




def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            #messages.success(request,'Congratulations {come inserire username?}! Your account has been created successfully, now you are able to log-in'.format(username))
            createProfile(request, username)
            return redirect('home')

    else:
        form = CreateUserForm()
    context = {'form': form}
    return render(request, 'account/register.html', context)



def createProfile(request, username):
    #user = User.objects.get(username=username)
    random_given = random.randint(1,10)
    bitcoin_current = BitCoinCurrentPrice().get_best()
    tot_amount = random_given * bitcoin_current[0]
    user = User.objects.get(username=username)
    #profile = Profile.objects.create(user=user, random_given=random_given, BitCoin=BitCoin, starting_balance=tot_amount, balance= tot_amount)
    form = CreateProfileForm(request.POST)
    messages.info(request, form)
    if form.is_valid():
        profile = form.save(commit=False)
        profile.user = user
        profile.random_given = random_given
        profile.BitCoin = random_given
        profile.starting_balance = tot_amount
        profile.balance = tot_amount
        profile.save()
        messages.info(request, 'Il form è valido')
    else:
        form = CreateProfileForm()
        messages.info(request, 'Form non valido')



class BitCoinCurrentPrice:
    def __init__(self):

        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

        self.params = {
            'start':'1',
            'limit':'100',
            'convert':'EUR',
            'sort':'market_cap',
            'sort_dir':'desc'
        }

        self.headers = {
            'Accepts':'applications/json',
            'X-CMC_PRO_API_KEY':'b8ee0ea1-ae9b-44ab-9132-02e6e5430eb1'
        }

    def get_best(self,):
        r = requests.get(url=self.url,headers=self.headers,params=self.params).json()
        currencies = []
        for currency in r['data']:
            currencies.append(
            currency['quote']['EUR']['price']
            )
        tot_amount = (currencies[:1])
        return tot_amount

    def get_supply(self, ):
        r = requests.get(url=self.url, headers=self.headers, params=self.params).json()
        currencies = []
        for currency in r['data']:
            currencies.append(
                currency['total_supply']
            )
        total_supply = (currencies[:1])
        return total_supply



def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request,'Username or password is incorrect')
    context = {}
    return render(request, 'account/login.html', context)



@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('/login')



@login_required(login_url='login')
def home(request):
    if request.method == "GET":
        complete_orders()
        sell_on_blockchain()
        buy_on_blockchain()
        orders_list = Sell.objects.filter(pending = True).order_by('datetime')
        if orders_list.count() <= 0:
            messages.success(request, "There are no pending sell orders")

        #data = pd.read_csv('C:/Users/alber/Downloads/market-price.csv')
        #tail = data.tail()
        #chart = data.plot.line()
        #plt.show()
        orders = pagination(request, orders_list)
        bitcoin_current = BitCoinCurrentPrice().get_best()
        bitcoin_supply = BitCoinCurrentPrice().get_supply()

    return render(request, 'account/home.html', { 'orders': orders, 'bitcoin_current': bitcoin_current, 'bitcoin_supply': bitcoin_supply})



def pagination(request, orders_list):
    page = request.GET.get('page', 1)
    paginator = Paginator(orders_list, 8)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    return orders



@login_required(login_url='login')
def contact(request):
    return render(request, 'account/contact.html', {})



@login_required(login_url='login')
def buy_order(request):
    form = CreateBuyForm()
    if request.method == "POST":
        profile = Profile.objects.get(user=request.user)
        form = CreateBuyForm(request.POST)
        if form.is_valid():
            buy = form.save(commit=False)
            buy.user = profile
            buy.datetime = timezone.now()
            buy.pending = True
            price_each_one = request.POST.get('buy_price')
            quantity = request.POST.get('buy_quantity')
            buy.offer = float(price_each_one) * float(quantity)
            buy.demand_quantity = request.POST.get('buy_quantity')
            buy.save()
            return redirect('home')
    else:
        form = CreateBuyForm()
    return render(request, 'account/buy_order.html', {'form':form})


@login_required(login_url='login')
def sell_order(request):
    form = CreateSellForm()
    if request.method == "POST":
        form = CreateSellForm(request.POST)
        profile = Profile.objects.get(user=request.user)
        Btc_quantity = profile.BitCoin
        bitcoin_range = numpy.linspace(0.5, Btc_quantity, num=int(Btc_quantity / 0.5))
        context = {'form':form, 'bitcoin_range': bitcoin_range}
        if form.is_valid():
            sell_quantity = request.POST.get('sell_quantity')
            sell = form.save(commit=False)
            sell.user = profile
            sell.datetime = timezone.now()
            sell.pending = True
            sell.selling_price = request.POST.get('sell_price')
            sell.selling_quantity = sell_quantity
            sell.save()
            messages.success(request,'Congratulations! Your sell order has been created successfully')
            profile.BitCoin = Btc_quantity - float(sell_quantity)
            profile.save()
            updating_balance(profile)

            return redirect('home')
        else:
            messages.info(request,form,'form non valido')
    else:
        profile = Profile.objects.get(user=request.user)
        Btc_quantity = profile.BitCoin
        bitcoin_range = numpy.linspace(0.5, Btc_quantity, num=int(Btc_quantity/0.5))
        form = CreateBuyForm()
        context = {'form':form, 'bitcoin_range': bitcoin_range}
    return render(request, 'account/sell_order.html', context)


@login_required(login_url='login')
def your_orders(request):
    if request.method == "GET":
        complete_orders()
        user = User.objects.get(username=request.user.username)
        profile = Profile.objects.get(user=request.user)#lo user(chiave) va preso da Profile in modo da passare alla classe Order poi
        #l'intero oggetto user e non solo l'attributo user
        orders_list_sell = Sell.objects.filter(user=profile).order_by('datetime')
        orders_sell = pagination(request, orders_list_sell)
        if orders_list_sell.count() <= 0:
            messages.info(request,'You have not create sell order yet')

        orders_list_buy = Buy.objects.filter(user=profile).order_by('datetime')
        orders_buy = pagination(request, orders_list_buy)
        if orders_list_buy.count() <= 0:
            messages.info(request,'You have not create buy order yet')


    return render(request, 'account/your_orders.html', {'user': user, 'orders_buy': orders_buy, 'orders_sell': orders_sell })



@staff_member_required
def all_pending_orders(request):
    if request.method == "GET":
        complete_orders()
        sell_list = Sell.objects.filter(pending = True).order_by('datetime')
        buy_list = Buy.objects.filter(pending = True).order_by('datetime')
        #all_order_list = list(chain(buy_list, sell_list)) per combinare due querysets in una lista
        sell_seriealized = serializers.serialize('json', list(sell_list), fields=('user','datetime', 'selling_price', 'selling_quantity'))
        buy_seriealized = serializers.serialize('json', list(buy_list), fields=('user','datetime', 'offer', 'demand_quantity'))

        return JsonResponse ({'sell_list': sell_seriealized, 'buy_list': buy_seriealized}, json_dumps_params={'indent':2})



@staff_member_required
def all_closed_orders(request):
    if request.method == "GET":
        sell_list = Sell.objects.filter(pending=False).order_by('datetime')
        buy_list = Buy.objects.filter(pending=False).order_by('datetime')
        sell_seriealized = serializers.serialize('json', list(sell_list), fields=('user', 'datetime', 'selling_price', 'selling_quantity', 'transaction_id'))
        buy_seriealized = serializers.serialize('json', list(buy_list), fields=('user', 'datetime', 'offer', 'demand_quantity', 'transaction_id'))

        return JsonResponse ({'sell_list': sell_seriealized, 'buy_list': buy_seriealized}, json_dumps_params={'indent':2})



@login_required(login_url='login')
def my_data(request):
    if request.method == 'GET':
        complete_orders()
        user_data = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_data)
        variations = updating_balance(user_profile)
        b_order = Buy.objects.filter(user=user_profile).count()
        s_order = Sell.objects.filter(user=user_profile).count()
        context = {'user_data': user_data, 'user_profile': user_profile, "b_order": b_order, "s_order": s_order, "variations": float(variations)}
        return render(request, 'account/my_data.html', {'context': context})


def updating_balance(user):
    start = user.starting_balance
    converter = BitCoinCurrentPrice()
    bitcoin_current = converter.get_best()
    current = int(user.BitCoin) * bitcoin_current[0]
    user.balance = current
    user.save()
    variations = current - int(start)
    return variations



def change_after_buying(buy, sell):
    bitcoin_current = BitCoinCurrentPrice().get_best()
    buyer = buy.user
    buyer.balance = buyer.balance - sell.selling_price
    buyer.BitCoin = buyer.BitCoin - (sell.selling_price / bitcoin_current[0]) + buy.demand_quantity
    buyer.save()
    buy.pending = False
    buy.save()


def change_after_selling(buy, sell):
    seller = sell.user
    seller.balance = seller.balance + sell.selling_price
    seller.save()
    sell.pending = False
    sell.save()

def match_orders(buy, sell):
    btc_buy = buy.demand_quantity
    btc_sell = sell.selling_quantity
    buy_price = buy.offer
    sell_price = sell.selling_price
    if btc_buy == btc_sell and buy_price >= sell_price:
        return True
    else:
        return False



def complete_orders():
    buys = Buy.objects.filter(pending = True)
    sells = Sell.objects.filter(pending = True)
    if len(sells) > 0 and len(buys) > 0:
        for buy in buys:
            price = float('inf')
            order = None
            for sell in sells:
                if match_orders(buy, sell):
                    if sell.selling_price < price:
                        order = sell
                        price = sell.selling_price
            if type(order) == None:
                continue
            else:
                change_after_buying(buy, sell)
                change_after_selling(buy, sell)
    else:
        pass



def buy_on_blockchain():
    buy_orders = Buy.objects.filter(pending = False)
    for buy_order in buy_orders:
        if buy_order.on_blockchain == False:
            buyer = buy_order.user
            price = buy_order.offer
            quantity = buy_order.demand_quantity
            data = (f"{buyer}, {price}, {quantity}")
            manage_buy_transaction(str(data), buy_order)
        else:
            pass



def manage_buy_transaction(data, order):
    infura_url = "https://ropsten.infura.io/v3/de19542993aa47f98c02ebc4b5eb7bed"
    web3 = Web3(Web3.HTTPProvider(infura_url))
    nonce = web3.eth.getTransactionCount(address)
    gasPrice = web3.eth.gasPrice
    tx = {
        'nonce': nonce,
        'to': "0x0000000000000000000000000000000000000000",
        'value': web3.toWei(0, 'ether'),
        'gas': 100000,
        'gasPrice': gasPrice,
        'data': data.encode('utf-8')
    }
    signed_tx = web3.eth.account.signTransaction(tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    relevant_order = Buy.objects.get(id=order.id)
    relevant_order.transaction_id = web3.toHex(tx_hash)
    relevant_order.on_blockchain = True
    relevant_order.save()



def buy_transaction_verification(request):
    infura_url = "https://ropsten.infura.io/v3/de19542993aa47f98c02ebc4b5eb7bed"
    web3 = Web3(Web3.HTTPProvider(infura_url))
    orders = Buy.objects.filter(on_blockchain=True)
    data = []
    for order in orders:
        transaction = order.transaction_id
        data.append(web3.eth.getTransaction(transaction))
    return HttpResponse(data)



def sell_on_blockchain():
    sell_orders = Sell.objects.filter(pending = False)
    for sell_order in sell_orders:
        if sell_order.on_blockchain == False:
            seller = sell_order.user
            price = sell_order.selling_price
            quantity = sell_order.selling_quantity
            data = (f"{seller}, {price}, {quantity}")
            manage_sell_transaction(str(data), sell_order)
        else:
            pass



def manage_sell_transaction(data, order):
    infura_url = "https://ropsten.infura.io/v3/de19542993aa47f98c02ebc4b5eb7bed"
    web3 = Web3(Web3.HTTPProvider(infura_url))
    nonce = web3.eth.getTransactionCount(address)
    gasPrice = web3.eth.gasPrice
    tx = {
        'nonce': nonce,
        'to': "0x0000000000000000000000000000000000000000",
        'value': web3.toWei(0, 'ether'),
        'gas': 100000,
        'gasPrice': gasPrice,
        'data': data.encode('utf-8')
    }
    signed_tx = web3.eth.account.signTransaction(tx, private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    relevant_order = Sell.objects.get(id=order.id)
    relevant_order.transaction_id = web3.toHex(tx_hash)
    relevant_order.on_blockchain = True
    relevant_order.save()



def sell_transaction_verification(request):
    infura_url = "https://ropsten.infura.io/v3/de19542993aa47f98c02ebc4b5eb7bed"
    web3 = Web3(Web3.HTTPProvider(infura_url))
    orders = Sell.objects.filter(on_blockchain=True)
    data = []
    for order in orders:
        transaction = order.transaction_id
        data.append(web3.eth.getTransaction(transaction))
    return HttpResponse(data)





import json
from requests import get
import sys
import time

from Model import register_trader_save,login_trader_save,buy_stock,view_stock,sell_stock,admin_access_model



def register_trader():
    trader_email = input('Enter your email id:')
    trader_pass = input('Enter your password:')

    register_trader_save(trader_email,trader_pass)
    print('Successfully Registered.')



def login_trader():
    trader_email = input('Enter your email id:')
    trader_pass = input('Enter your password:')

    query_login=login_trader_save(trader_email,trader_pass)

    return query_login



def company_search():

    symbol=input('Enter Company Name or Symbol(Partial Works too.):\n')
    q = {'input': symbol}
    s = 'http://dev.markitondemand.com/Api/v2/Lookup/json/'

    try:
        res = get(s, q)
        r = res.json()

    except:
        print('Connection Error',sys.exc_info())
        i=5
        while(i!=0):
            print("Retrying in ",i)
            i-=1
            time.sleep(1)
            res = get(s, q)
            r = res.json()


    for i in r:
        print(i)




def get_quote():
    symbol = input('Enter the Company Symbol:\n')

    q = {'symbol': symbol}
    s = "http://dev.markitondemand.com/Api/v2/Quote/json/"

    try:
        res = get(s, q)
        r = res.json()

    except:
        print('Connection Error',sys.exc_info())
        i=5
        while(i!=0):
            print("Retrying in ",i)
            i-=1
            time.sleep(1)
            res = get(s, q)
            r = res.json()


    ka=list(r.keys())
    va = list(r.values())

    return va[2],va[1],va[3]#bug





def portfolio():
    trader_email = input('Enter your email id:')
    trader_pass = input('Enter your password:')

    query_login = login_trader_save(trader_email, trader_pass)

    if query_login==1:
        stock_option_index=-1
        while(stock_option_index!=0):

            stock_option_index=int(input("0. To Quit\n"
                  "1. To Buy Stocks\n"
                  "2. To Sell Stocks\n"
                  "3. To View Stocks\n"))

            if stock_option_index==0:
                break
            elif stock_option_index==1:
                stock_symbol,stock_name,stock_price=get_quote()#1 check
                print(stock_name,'--',stock_price)
                stock_volume=int(input('Choose the Volume of Shares.'))
                buy_stock(trader_email,trader_pass,stock_symbol,stock_name,stock_price,stock_volume)

            elif stock_option_index==2:
                 #stock_symbol_remove=input("Enter the stock symbol you want to remove.")
                 a,b,c=get_quote()
                 sell_stock(trader_email,a,c)


            elif stock_option_index==3:
                view_stock(trader_email)

            else:
                print("You pressed the wrong key.")


def admin_access():
    admin_password=input("Enter Admin Password.\n")
    if admin_password in 'admin123':
        admin_access_model()





def get_quote_symbol(symbol):

    q = {'symbol': symbol}
    s = "http://dev.markitondemand.com/Api/v2/Quote/json/"

    try:
        res = get(s, q)
        r = res.json()

    except:
        print('Connection Error',sys.exc_info())
        i=5
        while(i!=0):
            print("Retrying in ",i)
            i-=1
            time.sleep(1)
            res = get(s, q)
            r = res.json()


    ka=list(r.keys())
    va = list(r.values())

    return va[3]
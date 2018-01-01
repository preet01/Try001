from sqlalchemy import Column
from sqlalchemy import DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sqlite3,sys
import os
import json
from requests import get
import sys
import time


def register_trader_save(trader_email,trader_pass):

    Base = declarative_base()

    class Customer(Base):
        __tablename__ = 'customer_register'
        id = Column(Integer, primary_key=True)
        email_customer = Column(String)
        password_customer = Column(String)
        Total_money       =Column(Integer)

    class Stock(Base):
        __tablename__ = 'stock_register'
        id = Column(Integer, primary_key=True)
        stock_symbol = Column(String)
        stock_name=Column(String)
        stock_price = Column(Integer)  # amount has to made too
        stock_quantity = Column(Integer)
        total_stock_price=Column(Integer)

        customer_id = Column(Integer, ForeignKey('customer_register.id'))
        customer_connect = relationship(Customer, backref=backref('xyz', uselist=True, cascade='delete,all'))

    engine = create_engine('sqlite:///market_database.sqlite')

    session = sessionmaker()
    session.configure(bind=engine)  # need a new session?does it overwrite? does it find a new row
    Base.metadata.create_all(engine)
    s = session()

    d = Customer(email_customer=trader_email,password_customer=trader_pass,Total_money=100000)

    s.add(d)
    s.commit()


def login_trader_save(trader_email,trader_pass):


    Base = declarative_base()

    class Customer(Base):
        __tablename__ = 'customer_register'
        id = Column(Integer, primary_key=True)
        email_customer = Column(String)
        password_customer = Column(String)
        Total_money       =Column(Integer)

    engine = create_engine('sqlite:///market_database.sqlite')

    session = sessionmaker()
    session.configure(bind=engine)  # need a new session?does it overwrite? does it find a new row
    Base.metadata.create_all(engine)
    s = session()

    session_data=s.query(Customer).all()

    for i in session_data:
        if i.email_customer==trader_email:
            if i.password_customer==trader_pass:
                return 1


    return 0

def buy_stock(trader_email,trader_pass,stock_symbol,stock_name,stock_price,stock_volume):
    Base = declarative_base()

    class Customer(Base):
        __tablename__ = 'customer_register'
        id = Column(Integer, primary_key=True)
        email_customer = Column(String)
        password_customer = Column(String)
        Total_money = Column(Integer)

    class Stock(Base):
        __tablename__ = 'stock_register'
        id = Column(Integer, primary_key=True)
        stock_symbol = Column(String)
        stock_name = Column(String)
        stock_price = Column(Integer)  # amount has to made too
        stock_quantity = Column(Integer)
        total_stock_price = Column(Integer)

        customer_id = Column(Integer, ForeignKey('customer_register.id'))
        customer_connect = relationship(Customer, backref=backref('xyz', uselist=True, cascade='delete,all'))

    engine = create_engine('sqlite:///market_database.sqlite')

    session = sessionmaker()
    session.configure(bind=engine)  # need a new session?does it overwrite? does it find a new row
    Base.metadata.create_all(engine)
    s = session()

    total_stock_money = (stock_volume * stock_price)
    total_money_present=0

    cust_id_1 = s.query(Customer).all()

    for i in cust_id_1:
        if i.email_customer==trader_email:
            total_money_present=i.Total_money
            # cust_id=i
    if total_money_present>=total_stock_money:
        for i in cust_id_1:
            if i.email_customer == trader_email:
                i.Total_money-=total_stock_money
                cust_id=i

        st=Stock(stock_symbol=stock_symbol,stock_name=stock_name,stock_price=stock_price,stock_quantity=stock_volume,total_stock_price=total_stock_money,customer_connect=cust_id)

        s.add(st)
        s.commit()
    else:
        print("Insufficient funds...")


def view_stock(trader_email):

    Base = declarative_base()

    class Customer(Base):
        __tablename__ = 'customer_register'
        id = Column(Integer, primary_key=True)
        email_customer = Column(String)
        password_customer = Column(String)
        Total_money = Column(Integer)

    class Stock(Base):
        __tablename__ = 'stock_register'
        id = Column(Integer, primary_key=True)
        stock_symbol = Column(String)
        stock_name = Column(String)
        stock_price = Column(Integer)  # amount has to made too
        stock_quantity = Column(Integer)
        total_stock_price = Column(Integer)

        customer_id = Column(Integer, ForeignKey('customer_register.id'))
        customer_connect = relationship(Customer, backref=backref('xyz', uselist=True, cascade='delete,all'))

    engine = create_engine('sqlite:///market_database.sqlite')

    session = sessionmaker()
    session.configure(bind=engine)  # need a new session?does it overwrite? does it find a new row
    Base.metadata.create_all(engine)
    s = session()

    total_balance=0
    viewing=s.query(Customer).all()
    id_customer=0
    for i in viewing:
        if i.email_customer==trader_email:
            id_customer=i.id
            total_balance=i.Total_money

    print("Total balance in account:",total_balance)

    viewing_1=s.query(Stock).all()

    print("stock_symbol--stock_name--stock_price--stock_quantity--total_stock_price")

    for i in viewing_1:
        if i.customer_id==id_customer:
            print(i.stock_symbol,i.stock_name,i.stock_price,i.stock_quantity,i.total_stock_price)


    s.commit()

def sell_stock(trader_email,stock_symbol_remove,stock_latest_price):
    Base = declarative_base()

    class Customer(Base):
        __tablename__ = 'customer_register'
        id = Column(Integer, primary_key=True)
        email_customer = Column(String)
        password_customer = Column(String)
        Total_money = Column(Integer)

    class Stock(Base):
        __tablename__ = 'stock_register'
        id = Column(Integer, primary_key=True)
        stock_symbol = Column(String)
        stock_name = Column(String)
        stock_price = Column(Integer)  # amount has to made too
        stock_quantity = Column(Integer)
        total_stock_price = Column(Integer)

        customer_id = Column(Integer, ForeignKey('customer_register.id'))
        customer_connect = relationship(Customer, backref=backref('xyz', uselist=True, cascade='delete,all'))

    engine = create_engine('sqlite:///market_database.sqlite')

    session = sessionmaker()
    session.configure(bind=engine)  # need a new session?does it overwrite? does it find a new row
    Base.metadata.create_all(engine)
    s = session()

    view_id = s.query(Customer).all()
    id_customer = 0
    for i in view_id:
        if i.email_customer == trader_email:
            id_customer = i.id

    num_stock_sell = int(input("Number of stock you want to sell:"))
    num_stock_present_query=s.query(Stock).all()
    num_stock_present=0




    for i in num_stock_present_query:
        if i.customer_id==id_customer:
            if i.stock_symbol==stock_symbol_remove:
                num_stock_present=i.stock_quantity

    if num_stock_sell>num_stock_present:
        print("Insufficient Stocks..")

    elif num_stock_sell<num_stock_present:
        num_stock_left=num_stock_present-num_stock_sell
        total_new_stock_money=num_stock_left*stock_latest_price

        stock_num_change=s.query(Stock).all()

        for i in stock_num_change:
            if i.customer_id==id_customer:
                if i.stock_symbol==stock_symbol_remove:
                    i.stock_quantity-=num_stock_sell
                    i.total_stock_price=total_new_stock_money

        total_amt_change=s.query(Customer).all()


        for i in total_amt_change:
            if i.email_customer==trader_email:
                i.Total_money+=(num_stock_sell*stock_latest_price)


    elif num_stock_sell==num_stock_present:
        total_amt_change = s.query(Customer).all()
        id_customer = 0

        for i in total_amt_change:
             if i.email_customer == trader_email:
                    i.Total_money += (num_stock_sell * stock_latest_price)
                    id_customer = i.id

        del_row=s.query(Stock).all()

        for i in del_row:
            if i.customer_id==id_customer:
                if i.stock_symbol==stock_symbol_remove:
                    s.delete(i)#it is possible??
    s.commit()



def admin_access_model():
    Base = declarative_base()

    class Customer(Base):
        __tablename__ = 'customer_register'
        id = Column(Integer, primary_key=True)
        email_customer = Column(String)
        password_customer = Column(String)
        Total_money = Column(Integer)

    engine = create_engine('sqlite:///market_database.sqlite')

    session = sessionmaker()
    session.configure(bind=engine)  # need a new session?does it overwrite? does it find a new row
    Base.metadata.create_all(engine)
    s = session()

    admin_view=s.query(Customer).all()

    for i in admin_view:
        print(i.email_customer,i.Total_money)

    s.commit()

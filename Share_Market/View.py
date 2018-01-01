from Controller import register_trader,login_trader,company_search,get_quote,portfolio,admin_access

print('Welcome to Goldman Sachs High Trading Unit.')


option=-1
while(option!=0):
    print('0. Exit Application\n'
          '1. For Register\n'
          '2. For Login\n'
          '3. ADMIN**\n')

    option=int(input())

    if option==1:
        register_trader()

    elif option==2:

        if login_trader()==1:

            option_controller=-1
            while(option_controller!=0):

                print('0. Logout:\n'
                      '1. To find Company Symbol:\n'
                      '2. To find Prices:\n'
                      '3. Access Portfolio\n')
                try:
                    option_controller=int(input())
                except:
                    print('Wrong Input.\nTry Again.\n')
                    option_controller=int(input())

                if option_controller==1:
                    company_search()

                elif option_controller==2:
                    a,b,c=get_quote()
                    print(a,b,c)

                elif option_controller==3:
                    print("Securing Connection...\n")
                    portfolio()# add the functionality of not taking the username again

                elif option_controller==0:
                    break
                elif option_controller>2:
                    print('Pressed Wrong number try again.\n')

        else:
            print('Wrong username or password.\n'
                  'Try Again.')

    elif option==3:
        admin_access()
    elif option>4:
        print('Wrong key Pressed.\nTry again.')






print('Thanks for Using High Trading Unit by Goldman Sachs.')
print('Shutting down...')
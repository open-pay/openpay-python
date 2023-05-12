![Openpay Python](https://www.openpay.mx/img/github/python.jpg)

Python Client for Openpay API Services

This is a client implementing the payment services for Openpay at www.openpay.mx

Installation
=============

You don't need this source code unless you want to modify the package. If you just want use the Openpay Python bindings,
you should run:

    pip install "setuptools<58.0"
    pip install openpay

or

    pip install openpay --udgrade

See www.pip-installer.org/en/latest/index.html for instructions on installing pip.


Implementation
==============



Usage for México
==============

#### Configuration ####

Before use the library will be necessary to set up your Merchant ID and Private key.

```python
import openpay

openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
openpay.production = True  # By default this works in sandbox mode
openpay.country = 'mx'  # 'mx' is default value, to use for Colombia set country='co'
```

Once configured the library, you can use it to interact with Openpay API services.

##### Tokens #####

Creating a token:

```python
openpay.Token.create(
    card_number="4111111111111111",
    holder_name="Juan Perez Ramirez",
    expiration_year="20",
    expiration_month="12",
    cvv2="110",
    address={
        "city": "Querétaro",
        "country_code": "MX",
        "postal_code": "76900",
        "line1": "Av 5 de Febrero",
        "line2": "Roble 207",
        "line3": "col carrillo",
        "state": "Queretaro"
    })
```

##### Customer #####

Creating a customer:

```python
customer = openpay.Customer.create(
    name="Juan",
    email="somebody@example.com",
    address={
        "city": "Queretaro",
        "state": "Queretaro",
        "line1": "Calle de las penas no 10",
        "postal_code": "76000",
        "line2": "col. san pablo",
        "line3": "entre la calle de la alegria y la calle del llanto",
        "country_code": "MX"
    },
    last_name="Perez",
    phone_number="44209087654"
)
```

Once you have a customer, you have access to few resources for current customer. According to the current version of the
Openpay API, these resources are:

- cards
- charges
- transfers
- payouts
- bank accounts
- subscriptions

You can access all of these resources as public variables of the root instance (customer in this example), so, if you
want to add a new card you will be able to do it as follows:

```python
card = customer.cards.create(
    card_number="4111111111111111",
    holder_name="Juan Perez Ramirez",
    expiration_year="20",
    expiration_month="12",
    cvv2="110",
    address={
        "city": "Querétaro",
        "country_code": "MX",
        "postal_code": "76900",
        "line1": "Av 5 de Febrero",
        "line2": "Roble 207",
        "line3": "col carrillo",
        "state": "Queretaro"
    })
```

Get a customer

```python
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
```

Update a customer

```python
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
customer.last_name = "Lopez"
customer.save()
```

Get all customers

```python
customers = openpay.Customer.all()
```

###### Customer Cards ######

Get all customer cards

```python
cards = customer.cards.all()
```

Get specific customer card

```python
card = customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')
```

Delete a customer card

```python
card = customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')
card.delete()
```

###### Customer Transfers ######

Get all customer transfers (inbound and outbound)

```python
transfers = customer.transfers.all()
```

Create a customer transfer

```python
transfer1 = customer.transfers.create(
    customer_id="acuqxruyv0hi1wfdwmym",
    amount=100,
    description="Test transfer",
    order_id="oid-00059"
)
```

Get specific transfer

```python
transfer2 = customer.transfers.retrieve(transfer1.id)
```

###### Bank Accounts ######

Add bank account to customer

```python
bank_account = customer.bank_accounts.create(
    clabe="032180000118359719",
    alias="Cuenta principal",
    holder_name="Juan Perez"
)
```

Get all customer bank accounts

```python
accounts = customer.bank_accounts.all()
```

Get specific bank account

```python
account = customer.back_accounts.retrieve("bsbg7igxh3yukpu8t2q4")
```

###### Subscriptions ######

Add subscription to customer

```python
customer.subscriptions.create(plan_id="pbkliysxavp8bvvp8f0k", trial_days="5", card_id="kvxvccpsesm4pwmtgnjb")
```

Cancel subscription

```python
subscription = customer.subscriptions.all()[0]
subscription.delete()
```

List all customers subscriptions

```python
customer.subscriptions.all()
```

Update subscription

```python
subscription = customer.subscriptions.all()[0]
subscription.cancel_at_end_period = True
subscription.save()
```

###### Payouts ######

Add payout for customer

```python
bank_account = customer.bank_accounts.all().data[0]  # We get the first account
customer.payouts.create(
    method='bank_account',  # possible values ['bank_accunt', 'card']
    destination_id=bank_account.id,
    amount="100",
    description="First payout",
    order_id="oid-00058"
)
```

Get all payouts

```python
customer.payouts.all()
```

Get specific payout

```python
customer.payouts.retrieve("tbs6a7g4pypww4eq640d")
```

##### Plan #####

Create new plan

```python
plan = openpay.Plan.create(
    amount=150.00,
    status_after_retry="cancelled",
    retry_times=2,
    name="Curso de Ingles",
    repeat_unit="month",
    trial_days=30,
    repeat_every=1
)
```

Get specific plan

```python
plan2 = openpay.Plan.retrieve(plan.id)
```

Update a plan

```python
plan = openpay.Plan.retrieve('pbkliysxavp8bvvp8f0k')
plan.name = "Curso de Ingles II"
plan.save()
```

Delete plan

```python
plan = openpay.Plan.retrieve('pbkliysxavp8bvvp8f0k')
plan.delete()
```

##### Fee #####

You may charge a fee as follows:

```python
fee = openpay.Fee.create(
    customer_id="amce5ycvwycfzyarjf8l",
    amount=12.50,
    description="Fee Charge",
    order_id="oid=1245"
)
````

List all charged fees

```python
fees = openpay.Fee.all()
```

Usage for Perú
==============

#### Configuration ####

Before use the library will be necessary to set up your Merchant ID and Private key.

```python
import openpay

openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
openpay.production = True  # By default this works in sandbox mode
openpay.country = 'pe'  # 'mx' is default value, to use for Peru set country='pe'
```
Once configured the library, you can use it to interact with Openpay API services.

##### Tokens #####

Creating a token:

```python
openpay.Token.create(
    card_number="4111111111111111",
    holder_name="Juan Perez Ramirez",
    expiration_year="20",
    expiration_month="12",
    cvv2="110",
    address={
        "city": "Lima",
        "country_code": "PE",
        "postal_code": "15076",
        "line1": "Av 5 de Febrero",
        "line2": "Roble 207",
        "line3": "Lince",
        "state": "Lima"
    })
```

##### Customer #####

Creating a customer:

```python
customer = openpay.Customer.create(
    name="Juan",
    email="somebody@example.com",
    address={
        "city": "Lima",
        "country_code": "PE",
        "postal_code": "15076",
        "line1": "Av 5 de Febrero",
        "line2": "Roble 207",
        "line3": "Lince",
        "state": "Lima"
    },
    last_name="Perez",
    phone_number="44209087654"
)
```

Once you have a customer, you have access to few resources for current customer. According to the current version of the
Openpay API, these resources are:

- cards
- charges
- transfers
- payouts
- bank accounts
- subscriptions

You can access all of these resources as public variables of the root instance (customer in this example), so, if you
want to add a new card you will be able to do it as follows:

```python
card = customer.cards.create(
    card_number="4111111111111111",
    holder_name="Juan Perez Ramirez",
    expiration_year="20",
    expiration_month="12",
    cvv2="110",
    address={
        "city": "Lima",
        "country_code": "PE",
        "postal_code": "15076",
        "line1": "Av 5 de Febrero",
        "line2": "Roble 207",
        "line3": "Lince",
        "state": "Lima"
    })
```

Get a customer

```python
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
```

Update a customer

```python
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
customer.last_name = "Lopez"
customer.save()
```

Get all customers

```python
customers = openpay.Customer.all()
```

###### Customer Cards ######

Get all customer cards

```python
cards = customer.cards.all()
```

Get specific customer card

```python
card = customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')
```

Delete a customer card

```python
card = customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')
card.delete()
```

###### Customer Transfers ######

Get all customer transfers (inbound and outbound)

```python
transfers = customer.transfers.all()
```

Create a customer transfer

```python
transfer1 = customer.transfers.create(
    customer_id="acuqxruyv0hi1wfdwmym",
    amount=100,
    description="Test transfer",
    order_id="oid-00059"
)
```

Get specific transfer

```python
transfer2 = customer.transfers.retrieve(transfer1.id)
```

###### Bank Accounts ######

Add bank account to customer

```python
bank_account = customer.bank_accounts.create(
    clabe="032180000118359719",
    alias="Cuenta principal",
    holder_name="Juan Perez"
)
```

Get all customer bank accounts

```python
accounts = customer.bank_accounts.all()
```

Get specific bank account

```python
account = customer.back_accounts.retrieve("bsbg7igxh3yukpu8t2q4")
```

###### Subscriptions ######

Add subscription to customer

```python
customer.subscriptions.create(plan_id="pbkliysxavp8bvvp8f0k", trial_days="5", card_id="kvxvccpsesm4pwmtgnjb")
```

Cancel subscription

```python
subscription = customer.subscriptions.all()[0]
subscription.delete()
```

List all customers subscriptions

```python
customer.subscriptions.all()
```

Update subscription

```python
subscription = customer.subscriptions.all()[0]
subscription.cancel_at_end_period = True
subscription.save()
```

###### Checkouts ######

Add checkout to customer

```python
customer.checkouts.create(
    {
        "amount": 250,
        "currency": "PEN",
        "description": "Cargo cobro con link",
        "redirect_url": "https://misitioempresa.pe",
        "order_id": "oid-12331",
        "expiration_date": "2021-08-31 12:50",
        "send_email": True
    })
```

List all customers checkouts

```python
customer.checkouts.all()
```

Update checkout

```python
subscription = customer.subscriptions.all()[0]
subscription.cancel_at_end_period = True
subscription.save()
```

##### Plan ######

Create new plan

```python
plan = openpay.Plan.create(
    amount=150.00,
    status_after_retry="cancelled",
    retry_times=2,
    name="Curso de Ingles",
    repeat_unit="month",
    trial_days=30,
    repeat_every=1
)
```

Get specific plan

```python
plan2 = openpay.Plan.retrieve(plan.id)
```

Update a plan

```python
plan = openpay.Plan.retrieve('pbkliysxavp8bvvp8f0k')
plan.name = "Curso de Ingles II"
plan.save()
```

Delete plan

```python
plan = openpay.Plan.retrieve('pbkliysxavp8bvvp8f0k')
plan.delete()
```

Usage for Colombia
==============

```python
import openpay

openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
openpay.production = True  # By default this works in sandbox mode
openpay.country = 'co'  # 'mx' is default value, to use for Colombia set country='co'
```

Once configured the library, you can use it to interact with Openpay API services for Colombia.

##### Tokens #####

Creating a token:

```python
openpay.Token.create(
    holder_name="Juan Perez Ramirez",
    card_number="4111111111111111",
    cvv2="110",
    expiration_month="12",
    expiration_year="25",
    address={
        "city": "Bogotá",
        "country_code": "CO",
        "postal_code": "76900",
        "line1": "bogota",
        "line2": "colombia",
        "line3": "col carrillo",
        "state": "Bogota"
    })
```

##### Customer #####

Creating a customer:

```python
customer = openpay.Customer.create(
    name="Juan",
    last_name="Perez",
    email="somebody@example.com",
    {
        "name": "Pedro Diego",
        "last_name": "Alatorre Martínez",
        "email": "pedro.alatorre@comercio.com",
        "phone_number": "5744484951",
        "status": "active",
        "customer_address": {
            "department": "Medellín",
            "city": "Antioquía",
            "additional": "Avenida 7f bis # 138-58 Apartamento 942"
        }
    },
    phone_number="7711234567"
)
```

Once you have a customer, you have access to few resources for current customer. According to the current version of the
Openpay API, these resources are:

- cards
- charges
- subscriptions
- pse

You can access all of these resources as public variables of the root instance (customer in this example), so, if you
want to add a new card you will be able to do it as follows:

```python
card = customer.cards.create(
    card_number="4111111111111111",
    holder_name="Juan Perez Ramirez",
    expiration_year="25",
    expiration_month="12",
    cvv2="110",
    address={
        "city": "Bogotá",
        "country_code": "CO",
        "postal_code": "76900",
        "line1": "bogota",
        "line2": "colombia",
        "line3": "col carrillo",
        "state": "Bogota"
    })
```

Get a customer

```python
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
```

Update a customer

```python
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
customer.last_name = "Lopez"
customer.save()
```

Get all customers

```python
customers = openpay.Customer.all()
```

###### Customer Cards ######

Get all customer cards

```python
cards = customer.cards.all()
```

Get specific customer card

```python
card = customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')
```

Delete a customer card

```python
card = customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')
card.delete()
```

###### PSE ######

Add pse to customer

```python
pse = customer.pse.create(
    method='bank_account',
    currency="COP",
    iva="1900",
    description="description",
    redirect_url="/"
)
```

```python
pse = pse.create(
    method='bank_account',
    currency="COP",
    iva="1900",
    description="description",
    redirect_url="/",
    customer={
        "name": "Cliente Colombia",
        "last_name": "Vazquez Juarez",
        "email": "juan.vazquez@empresa.co",
        "phone_number": "4448936475",
        "requires_account": False,
        "customer_address": {
            "department": "Medellín",
            "city": "Antioquía",
            "additional": "Avenida 7m bis #174-25 Apartamento 637"
        }
    }
)
```

###### Subscriptions ######

Add subscription to customer

```python
customer.subscriptions.create(plan_id="pbkliysxavp8bvvp8f0k", trial_days="5", card_id="kvxvccpsesm4pwmtgnjb")
```

Cancel subscription

```python
subscription = customer.subscriptions.all()[0]
subscription.delete()
```

List all customers subscriptions

```python
customer.subscriptions.all()
```

Update subscription

```python
subscription = customer.subscriptions.all()[0]
subscription.cancel_at_end_period = True
subscription.save()
```

##### Plan #####

Create new plan

```python
plan = openpay.Plan.create(
    amount=150.00,
    status_after_retry="cancelled",
    retry_times=2,
    name="Curso de Ingles",
    repeat_unit="month",
    trial_days=30,
    repeat_every=1
)
```

Get specific plan

```python
plan2 = openpay.Plan.retrieve(plan.id)
```

Update a plan

```python
plan = openpay.Plan.retrieve('pbkliysxavp8bvvp8f0k')
plan.name = "Curso de Ingles II"
plan.save()
```

Delete plan

```python
plan = openpay.Plan.retrieve('pbkliysxavp8bvvp8f0k')
plan.delete()
```

#### Error handling ####

The Openpay API generates several types of errors depending on the situation, to handle this, the Python client has
implemented four type of exceptions:

- InvalidRequestError: This category includes requests when format is not JSON and Requests with non existents urls
- AuthenticationError: missing Private key
- CardError: Transfer not accepted, Declined card, Expired card, Inssuficient funds, Stolen Card, Fraudulent card.
- APIError: All other types API errors

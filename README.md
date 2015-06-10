![Openpay Python](http://www.openpay.mx/img/github/python.jpg)

Python Client for Openpay API Services

This is a client implementing the payment services for Openpay at www.openpay.mx

Installation
=============

You don't need this source code unless you want to modify the package. If you just want use the Openpay
Python bindings, you should run:

    pip install openpay 

or

    pip install openpay --udgrade

See www.pip-installer.org/en/latest/index.html for instructions on installing pip.

Implementation
==============

#### Configuration ####

Before use the library will be necessary to set up your Merchant ID and Private key. 

```python
import openpay

openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
openpay.production = True  # By default this works in sandbox mode
```

#### Usage ####

##### Customer #####

Once configured the library, you can use it to interact with Openpay API services. You can start creating a customer:

```python
customer = openpay.Customer.create(
    name="Juan",
    email="somebody@example.com",
    address={
        "city": "Queretaro",
        "state":"Queretaro",
        "line1":"Calle de las penas no 10",
        "postal_code":"76000",
        "line2":"col. san pablo",
        "line3":"entre la calle de la alegria y la calle del llanto",
        "country_code":"MX"
    },
    last_name="Perez",
    phone_number="44209087654"
)
```

Once you have a customer, you have access to few resources for current customer. According to the current version 
of the Openpay API, these resources are:

  - cards
  - charges
  - transfers
  - payouts
  - bank accounts
  - subscriptions

You can access all of these resources as public variables of the root instance (customer in this example), 
so, if you want to add a new card you will be able to do it as follows:

```python
card = customer.cards.create(
	card_number="4111111111111111",
	holder_name="Juan Perez Ramirez",
	expiration_year="20",
	expiration_month="12",
	cvv2="110",
	address={
		"city":"Querétaro",
		"country_code":"MX",
		"postal_code":"76900",
		"line1":"Av 5 de Febrero",
		"line2":"Roble 207",
		"line3":"col carrillo",
		"state":"Queretaro"
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
bank_account = customer.bank_accounts.all()[0]  # We get the first account
customer.payouts.create(
    method='bank_account',   # possible values ['bank_accunt', 'card']
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
plan.name="Curso de Ingles II"
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

#### Error handling ####

The Openpay API generates several types of errors depending on the situation,
to handle this, the Python client has implemented four type of exceptions:

  - InvalidRequestError: This category includes requests when format is not JSON and Requests with non existents urls
  - AuthenticationError: missing Private key
  - CardError: Transfer not accepted, Declined card, Expired card, Inssuficient funds, Stolen Card, Fraudulent card.
  - APIError: All other types API errors

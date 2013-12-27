Openpay Python Bindings
========================

[ ![Codeship Status for darkness51/openpay-python](https://www.codeship.io/projects/4a7d6990-4505-0131-27b3-4afe5eaaa101/status?branch=master)](https://www.codeship.io/projects/10830)

Python Client for Openpay API Services

This is a client implementing the payment services for Openpay at openpay.mx

Installation
=============

You don't need this source code unless you want to modify the package. If you just want use the Openpay
Python bindings, you should run:

    pip install openpay

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

Get all customer cards

```python
cards = customer.cards.all()
```

Get specific customer card

```python
card = customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')
```

#### Error handling ####

The Openpay API generates several types of errors depending on the situation,
to handle this, the Python client has implemented four type of exceptions:

  - InvalidRequestError: This category includes requests when format is not JSON and Requests with non existents urls
  - AuthenticationError: missing Private key
  - CardError: Transfer not accepted, Declined card, Expired card, Inssuficient funds, Stolen Card, Fraudulent card.
  - APIError: All other types API errors

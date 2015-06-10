import sys
import datetime
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"


charge = openpay.Charge.create_as_merchant(
    method="card",
    amount=100.00,
    description="Testing card charges from python",
    order_id="GHSasd",
    device_session_id="kjsadkjnnkjfvknjdfkjnvdkjnfvkj",
    card={
        "holder_name":"HOLDER NAME",
        "card_number":"4111111111111111",
        "cvv2":"123",
        "expiration_month":"12",
        "expiration_year":"20",
        "address":{
            "city": "Queretaro",
            "state":"Queretaro",
            "line1":"Calle de las penas no 10",
            "postal_code":"76000",
            "line2":"col. san pablo",
            "line3":"entre la calle de la alegria y la calle del llanto",
            "country_code":"MX"
        }
    },
    customer={
        "name":"Heber",
        "last_name":"Robles",
        "email":"xxxxx@example.com",
        "phone_number":"4429938834",
        "address":{
            "city": "Queretaro",
            "state":"Queretaro",
            "line1":"Calle de las penas no 10",
            "postal_code":"76000",
            "line2":"col. san pablo",
            "line3":"entre la calle de la alegria y la calle del llanto",
            "country_code":"MX"
        }
    },
    metadata={
        "data1":"value1",
        "data2":"value2"
    }
);

print(charge)
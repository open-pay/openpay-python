import sys
import datetime
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"

newCustomer = openpay.Customer.create(
    external_id="AA_00003",
    name="Oswaldo",
    last_name="Perez",
    email="nklnkfv@example.com",
    requires_account=False,
    phone_number="4429938834",
    address={
        "city": "Queretaro",
        "state":"Queretaro",
        "line1":"Calle de las penas no 10",
        "postal_code":"76000",
        "line2":"col. san pablo",
        "line3":"entre la calle de la alegria y la calle del llanto",
        "country_code":"MX"
    }
);

print(newCustomer);

import json
import os

from datetime import datetime, timedelta

from baked.lib.admin.service.credentialservice import CredentialService
from baked.lib.admin.service.userservice import UserService
from baked.lib.datetime import DATETIME_FORMAT
from baked.lib.email.emailservice import EmailService
from baked.lib.globals.setting import get_local, get_global
from baked.lib.systems.wrexhamshop.service.wrexhamshopservice import WrexhamShopService


class WrexhamShopAgent:

    def __init__(self):
        self._last_check = os.path.join(get_global("rtshares")["temp"], "lastcheck.json")
        if not os.path.exists(self._last_check):
            with open(self._last_check, "w") as fh:
                json.dump({}, fh)
    
    def process(self):
        service = None
        lastcheck = None
        local = get_local()

        notify = False
        price = None
        stock = None

        with open(os.path.join(local["root"], "config/wrexhamshop/products.json", "r")) as fh:
            service = WrexhamShopService(json.load(fh))

        try:
            price, stock = service.find_product("snapbackcap")

        except ValueError:
            price = "NOT FOUND"
            stock = "NOT FOUND"
            notify = True

        if stock.upper() != "OUT OF STOCK":
            notify = True

        else:
            with open(self._last_check, "w") as fh:
                lastcheck = json.load(fh)

            if not lastcheck:
                notify = True

            elif lastcheck and datetime.strptime(lastcheck, DATETIME_FORMAT) >= datetime.now() - timedelta(hours=6):
                notify = True

        if notify:
            # Piggy back off of supersix to send the email.
            user_service = UserService("supersix")
            admin_user = user_service.get_admin_user()
            my_user = user_service.get(user_id="SSX-MB")
            credential = CredentialService().get_credential(admin_user, "gmail")
            
            with EmailService("smtp").connect(credential.username, credential.password) as email:
                email.set_from(credential.username)
                email.add_recipient(my_user.email)
                email.set_subject(f"[{stock.upper()}] Wrexham Snapback Cap.")
                email.set_body(f"<html><body>Wrexham Snapback Cap:\n\nPrice: {price}\nStock Status: {stock}</body></html>")
                email.send()

from sqlalchemy import desc
from models import Mas_Bill
import random
import string

def generate_token(length=20):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def generate_passcode(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_Billing_data_head_id(length=7):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def generate_id(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))
from sqlalchemy import desc

def generate_new_bill_id(token):
    prefix = 'BIL'
    start_number = 1
    padding = 5  # Number of digits in the numeric part

    # Get the last bill for the token
    chk_bill = Mas_Bill.query.filter_by(token=token).order_by(Mas_Bill.Bill_id.desc()).first()

    if chk_bill and chk_bill.Bill_id.startswith(prefix):
        try:
            # Extract and increment numeric part
            current_number = int(chk_bill.Bill_id[len(prefix):])
            new_number = current_number + 1
        except ValueError:
            new_number = start_number
    else:
        new_number = start_number

    # Format new Bill_id
    new_bill_id = f"{prefix}{str(new_number).zfill(padding)}"
    return new_bill_id
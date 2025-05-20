from sqlalchemy import CheckConstraint # type: ignore
from database import db
from datetime import datetime, date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # User Name
    email = db.Column(db.String(100), unique=True, nullable=False) # User Email
    password = db.Column(db.String(64), nullable=False) # User Password
    token = db.Column(db.String(20), unique=True, nullable=False) # User Token
    bill_token = db.Column(db.String(10), unique=True, nullable=False) # User Bill Id
    label_token = db.Column(db.String(10), unique=True, nullable=False) # User Bill Id
    group = db.Column(db.String(20), unique=False, nullable=False) # User permission Group
    user_verification = db.Column(db.Integer, unique=False, nullable=False) # 0 = not verified, 1 = verified
    
    __table_args__ = (
        CheckConstraint('user_verification IN (0, 1)', name='check_user_verification'),
    )
    
    def __repr__(self):
        return f'<User {self.email}>'
        
class Otp_verify(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20), unique=True, nullable=False) # User Token
    email = db.Column(db.String(30), unique=True, nullable=False) # PASSCODE RECEIVED ADDRESS
    passcode = db.Column(db.String(6), unique=False, nullable=False) # OTP = `876567`
    validate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # OTP Expiry DateTime
    otp_flag = db.Column(db.Integer, unique=False, nullable=False) # 0, 1
    
    __table_args__ = (
        CheckConstraint('otp_flag IN (0, 1)', name='check_otp_flag'),
    )
    
    def __repr__(self):
        return f'<User {self.token, {self.email}}>'
    
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20), unique=True, nullable=False) #MAPPING THE USER TABLE TOKEN
    label = db.Column(db.Integer, unique=False, nullable=False) #PERMISSION FOR LABEL CREATION
    applicationDate = db.Column(db.Boolean, nullable=False, default=False) #True OR False #PERMISSION FOR APPLICATION COMPONENT NEED CHANGE THE DATE EDIT

    __table_args__ = (
        CheckConstraint('label IN (0, 1)', name='check_label'),
    )
    
    def __repr__(self):
        return f'<Permission {self.token}>'
    
    
class Opoc_mas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20), nullable=False, unique=False) #MAP THE USER TABLE TO JOIN THE USER TOKEN
    openingBalance = db.Column(db.Float, unique=False, nullable=False,) #WRITE
    closingBalance = db.Column(db.Float, unique=False, nullable=False,) #WRITE
    dateofbalance = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #DEFAULT
    
    def __repr__(self):
        return f'<Opoc_mas {self.id}, {self.token}>'
    
    
class BillingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    head = db.Column(db.String(20), unique=True, nullable=False) #head
    path = db.Column(db.String(2000), unique=False, nullable=False) #svg icon
    head_id = db.Column(db.String(5), unique=True, nullable=False) #tag id
    status = db.Column(db.Boolean, nullable=False, default=True) #True OR False
    essential = db.Column(db.Integer, unique=False, nullable=False) #0 OR 1
    nonessential = db.Column(db.Integer, unique=False, nullable=False) #0 OR 1
    
    __table_args__ = (
        CheckConstraint('essential IN (0, 1)', name='check_essential'),
        CheckConstraint('nonessential IN (0, 1)', name='check_nonessential'),
    )
    
    def __repr__(self):
        return f'<Billing_data {self.head}>'
    
    
class Label_Mas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    labelname = db.Column(db.String(60), unique=False, nullable=False) #WRITE
    labelid = db.Column(db.String(5), unique=False, nullable=False) #AUTO-GENERATE
    mapuserid = db.Column(db.String(10), unique=False, nullable=False) #MAP THE USER TABLE IN LABEL-ID
    status = db.Column(db.Integer, unique=False, nullable=False) #IF SHOW 'OR' NOT SHOW
    
    __table_args__ = (
        CheckConstraint('status IN (0, 1)', name='check_status'),
    )
    
    def __repr__(self):
        return f"<Label_Mas {self.labelname}>"
    
    
class Mas_Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20), unique=False, nullable=False) #MAP THE USER TABLE IN TOKEN ID
    Bill_id = db.Column(db.String(8), unique=False, nullable=False) #AUTO-GENERATE
    headid = db.Column(db.String(6), unique=False, nullable=False) #MAP THE BILLINGDATA TO GET THE HEADID
    amount = db.Column(db.Float, unique=False, nullable=False) #WRITE
    reason = db.Column(db.String(1000), unique=False, nullable=False) #WRITE
    date = db.Column(db.Date, nullable=False, default=date.today)
    paymentmode = db.Column(db.String(10), nullable=False, unique=False) #MAP THE PAYMODE MAS TABLE TO GET THE ID
    
    def __repr__(self):
        return f"<Mas_BIll {self.token} {self.reason}>"
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from models import User, Otp_verify, BillingData, Mas_Bill, Label_Mas, Permission
from database import db, init_db
from utils import generate_token, generate_passcode, generate_Billing_data_head_id, generate_id, generate_new_bill_id
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BudgetBountry.db'  # Change to your DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
db.init_app(app)
init_db(app)

@app.route('/')
def Index():
    return render_template('Index.html')

# @app.route('/api/permission', methods=['POST'])
# def Permission():
#     data = request.get_json()
    
#     token = data.get('token')
#     label = data.get('label')
#     applicationDate = data.get('applicationDate')
    
#     chk_user = Permission.query.filter_by(token=token).first()
#     if not chk_user:
#         return jsonify(
#             { 'warn' : 'User not found.'}
#         ), 404
    
    
#     try:
#         db.session.commit()
#         return jsonify(
#             {'message': 'Permission will be Saved.'}
#         ), 200
#     except IntegrityError:
#         db.session.rollback()
#         return jsonify(
#             {'error': 'Internal Server Error'}
#         ), 500

@app.route('/api/create_user', methods=['POST'])
def create_user():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    address = data.get('address')

    # Check required fields
    if not all([name, email, password]):
        return jsonify({'warn': 'Name, email, and password are required'}), 400

    # Check if user exists
    if User.query.filter_by(email=email).first():
        print(False)
        return jsonify({'error': 'User already exists'}), 409

    token = generate_token()
    bill_token = generate_id()
    label_token = generate_id()
    group = 'user'
    passcode = generate_passcode()
    validate = (datetime.now()) + timedelta(seconds=300)
    otp_flag = 0
    user_verification = 0
    applicationDate = False

    # Create and store user
    new_user = User(name=name, email=email, password=password, token=token, bill_token=bill_token, label_token=label_token, group=group,  user_verification=user_verification, address=address)
    new_otp = Otp_verify(token=token, email=email, passcode=passcode, validate=validate, otp_flag=otp_flag)
    new_permission = Permission(token=token, label=0, applicationDate=applicationDate)
    
    db.session.add(new_user)
    db.session.add(new_otp)
    db.session.add(new_permission)
    try:
        db.session.commit()
        return jsonify({
            'message': 'User created successfully. Please verify the One Time Password.',
            'token': token,
            'user': {
                'name': name,
                'email_id': email,
                'otp': passcode,
            },
            }), 201
    except IntegrityError as e:
        db.session.rollback()
        print("IntegrityError:", e)
        return jsonify({'error': 'Internal Server Error.'}), 500
    except Exception as e:
        db.session.rollback()
        print("Unexpected Error:", e)
        return jsonify({'error': 'Unexpected Server Error.'}), 500

    
@app.route("/api/otp_verify", methods=['POST'])
def otp_verify():
    data = request.get_json()
    
    email = data.get('email')
    token = data.get('token')
    
    print(email, token)
    
    passcode = data.get('passcode')
    
    chk_passcode = Otp_verify.query.filter_by(token=token).first()
    chk_user = User.query.filter_by(email=email, token=token).first()
    
    if not chk_user:
        return jsonify({
            'error': 'User not found. Please try signing up again.'
        }), 404
        
    original_passcode = chk_passcode.passcode
    
    current_datetime = datetime.now()
    validatetime = chk_passcode.validate
    
    if current_datetime > validatetime:
        return jsonify({
            "warn": "One Time Passcode has expired. Please resend the passcode."
        }), 419
        
    if original_passcode == passcode:
        chk_passcode.otp_flag = 0
        chk_user.user_verification = 1
        db.session.commit()
        return jsonify({
            "message": "User verified successfully."
        }), 200
    else:
        return jsonify({
            "warn": "Incorrect OTP entered."
        }), 400 
            
@app.route("/api/login_user", methods=['POST'])
def login_user():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    # Check required fields
    if not all([email, password]):
        return jsonify({'warn': 'Email and Password are required'}), 400


    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': f'User not found. Please sign up with the email {email}.'}), 404
        
    chk_password = User.query.filter_by(email=email, password=password).first()
    if not chk_password:
        return jsonify(
            {'warn': f"Password does not match. Please enter the correct password {password}."}
        ), 401
        
    # Generate token
    tkn = user.token
    print(tkn)
        
    # OTP
    chk_passcode = Otp_verify.query.filter_by(token=tkn).first()
        
    if user.user_verification != 1:
        chk_passcode.otp_flag = 0
        passcode = generate_passcode()
        chk_passcode.passcode = passcode
        db.session.commit()
        return jsonify({
            "error": f"User {email} Not verified.",
            "message": f"OTP send this email: {email}",
            "passcode_details": {
                'email': user.email,
                'token': chk_passcode.token,
            }
        }), 409

    return jsonify({
        'message': 'Login successful',
        'token': tkn,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
    }), 200

@app.route('/api/get_session', methods=['GET'])
def get_session():
    sessions = User.query.all()
    
    data = [
        {
            'email' : session.email,
            'token' : session.token,
            'group' : session.group,
        }
        for session in sessions
    ]
    return jsonify(data)

@app.route('/api/add_Billing_data', methods=['POST'])
def add_Billing_data():
    data = request.get_json()
    
    head = data.get('head')
    path = data.get('path')
    status = data.get('status')
    essential = data.get('essential')
    nonessential = data.get('nonessential')
    
    head_id = generate_Billing_data_head_id()
    
    if not all([head, path]):
        return jsonify(
            { 'warn' : "All field are required." }
        ), 400
    
    chk_head = BillingData.query.filter_by(head=head, head_id=head_id).first()
    if chk_head:
        return jsonify(
            { 'warn' : f"this head {head} is already exist's."}
        ), 403
        
    new_data = BillingData(head=head, path=path, head_id=head_id, status=status, essential=essential, nonessential=nonessential)
    db.session.add(new_data)
    try:
        db.session.commit()
        return jsonify(
            { "message" : f"{head} is added Successfully."}
        ), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify(
            {'error': 'Internal Server Error.'}
        ), 500
        
@app.route('/api/update_billing_data', methods=['POST'])
def update_billing_data():
    data = request.get_json()
    
    head = data.get('head')
    head_id = data.get('head_id')
    path = data.get('path')
    status = data.get('status')
    essential = data.get('essential')
    nonessential = data.get('nonessential')
    
    chk_tag = BillingData.query.filter_by(head_id=head_id, head=head).first()
    
    if not chk_tag:
        return jsonify(
            { 'warn' : f'{head} does not found'}
        ), 404
    
    head.chk_tag = head
    head_id.chk_tag = head_id
    path.chk_tag = path
    status.chk_tag = status
    essential.chk_tag = essential
    nonessential.chk_tag = nonessential
    
    try:
        db.session.commit()
        return jsonify(
            { 'message' : f'{head} Updated Successfully.'}
        ), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify(
            { 'error' : 'Internal server Error.'}
        ), 500

@app.route('/api/Billing_data', methods=['GET'])
def Billing_data():
    Bill_datas = BillingData.query.all()
    
    data = [
        {
            'head': Bill_data.head,
            'path': Bill_data.path,
            'head_id': Bill_data.head_id,
            'status': Bill_data.status,
            'essential': Bill_data.essential,
            'nonessential': Bill_data.nonessential,
        }
        for Bill_data in Bill_datas
    ]
    return jsonify(data)

@app.route('/api/create_label', methods=['POST'])
def Create_Label():
    status = 1
    
    data = request.get_json()
    
    labelname = data.get('labelname')
    mapuserid = data.get('token')
    
    labelid = generate_id()
    
    if not all([labelname, mapuserid]):
        return jsonify(
            { 'warn' : 'All field Required.'}
        ), 403
        
    chk_label = Label_Mas.query.filter(mapuserid=mapuserid, labelname=labelname).all()
    
    if chk_label:
        return jsonify(
            { 'warn' : f'This {labelname} is already Exists.' }
        ), 403
        
    new_data = Label_Mas(labelname=labelname, mapuserid=mapuserid, labelid=labelid, status=status)
    db.session.add(new_data)
    
    try:
        db.session.commit()
        return jsonify(
            { 'message' : f'Label is {labelname} Created Successfully!.'}
        ), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify(
            { 'error' : 'Internal Server Error'}
        ), 501
        
@app.route('/api/mas_billing_data', methods=['POST'])
def Mas_Billing_data():
    data = request.get_json()
    
    token = data.get('token')
    headid = data.get('headid')
    amount = data.get('amount')
    date_str = data.get("date") 
    reason = data.get('description')
    paymentmode = data.get('paymentmode')

    
    if not all([token, headid, amount, date_str, reason, paymentmode]):
        return jsonify({
            'warn' : 'All field are required.'
        }), 400
        
    Bill_id = generate_new_bill_id(token)
    
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
    new_data = Mas_Bill(token=token, Bill_id=Bill_id, headid=headid, amount=amount, date=date, reason=reason, paymentmode=paymentmode)
    db.session.add(new_data)
    try:
        db.session.commit()
        return jsonify({
            'message':'Bill Raised Successfully.'
        }), 200
    except IntegrityError as e:
        db.session.rollback()
        print(e)
        return jsonify(
            { 'error' : 'Internal server Error.'}
        ), 500

if __name__ == '__main__':
    app.run(debug=True)
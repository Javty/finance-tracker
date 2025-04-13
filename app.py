import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'finance.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Wallet(db.Model):
    
    initial_balance = db.Column(db.Float, default=0.0)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    cutoff_day = db.Column(db.Integer, nullable=True)
    limit = db.Column(db.Float, nullable=True)
    payment_day = db.Column(db.Integer, nullable=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    note = db.Column(db.String(100))
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    wallet = db.relationship('Wallet', backref='transactions')

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lender = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), default='open')
    note = db.Column(db.String(200), nullable=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=True)
    wallet = db.relationship('Wallet', backref='loans')

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    from_wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    to_wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    note = db.Column(db.String(200), nullable=True)

    from_wallet = db.relationship('Wallet', foreign_keys=[from_wallet_id])
    to_wallet = db.relationship('Wallet', foreign_keys=[to_wallet_id])

@app.route('/')
def index():
    category_filter = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Transaction.query

    if category_filter:
        query = query.filter(Transaction.category.ilike(f"%{category_filter}%"))
    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d'))

    transactions = query.order_by(Transaction.date.desc()).all()

    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expense = sum(t.amount for t in transactions if t.amount < 0)
    balance = total_income + total_expense

    active_loans = Loan.query.filter_by(status='open').all()
    total_active_loans = sum(l.amount for l in active_loans)

    return render_template(
        'index.html',
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        total_active_loans=total_active_loans
    )

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    wallets = Wallet.query.all()

    if request.method == 'POST':
        raw_amount = float(request.form['amount'])
        t_type = request.form['type']
        category = request.form['category']
        note = request.form['note']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        amount = raw_amount if t_type == 'income' else -abs(raw_amount)
        wallet_id = request.form.get('wallet_id') or None

        new_transaction = Transaction(
            amount=amount,
            category=category,
            note=note,
            date=date,
            type=t_type,
            wallet_id=int(wallet_id) if wallet_id else None
        )

        db.session.add(new_transaction)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_transaction.html', wallets=wallets)

@app.route('/wallets', methods=['GET', 'POST'])
def manage_wallets():
    if request.method == 'POST':
        name = request.form['name']
        wallet_type = request.form['type']
        cutoff_day = request.form.get('cutoff_day') or None
        limit = request.form.get('limit') or None

        new_wallet = Wallet(
            name=name,
            type=wallet_type,
            cutoff_day=int(cutoff_day) if cutoff_day else None,
            limit=float(limit) if limit else None
        )

        db.session.add(new_wallet)
        db.session.commit()
        return redirect(url_for('manage_wallets'))

    wallets = Wallet.query.all()
    return render_template('wallets.html', wallets=wallets)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    wallets = Wallet.query.all()

    if request.method == 'POST':
        raw_amount = float(request.form['amount'])
        transaction.amount = raw_amount if transaction.type == 'income' else -abs(raw_amount)
        transaction.category = request.form['category']
        transaction.note = request.form['note']
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        wallet_id = request.form.get('wallet_id')
        transaction.wallet_id = int(wallet_id) if wallet_id else None

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_transaction.html', transaction=transaction, wallets=wallets)

@app.route('/loans', methods=['GET', 'POST'])
def manage_loans():
    wallets = Wallet.query.all()

    if request.method == 'POST':
        lender = request.form['lender']
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        note = request.form.get('note') or None
        wallet_id = request.form.get('wallet_id') or None

        loan = Loan(
            lender=lender,
            amount=amount,
            date=date,
            note=note,
            wallet_id=int(wallet_id) if wallet_id else None,
            status='open'
        )

        db.session.add(loan)
        db.session.commit()
        return redirect(url_for('manage_loans'))

    loans = Loan.query.filter_by(status='open').order_by(Loan.date.desc()).all()
    paid_loans = Loan.query.filter_by(status='paid').all()

    total_active = sum(l.amount for l in loans)
    total_paid = sum(l.amount for l in paid_loans)

    return render_template('loans.html', loans=loans, wallets=wallets, total_active=total_active, total_paid=total_paid)

@app.route('/loans/<int:id>/pay', methods=['POST'])
def pay_loan(id):
    loan = Loan.query.get_or_404(id)
    loan.status = 'paid'
    db.session.commit()
    return redirect(url_for('manage_loans'))

@app.route('/transfers', methods=['GET', 'POST'])
def manage_transfers():
    wallets = Wallet.query.all()

    if request.method == 'POST':
        from_wallet_id = int(request.form['from_wallet'])
        to_wallet_id = int(request.form['to_wallet'])
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        note = request.form.get('note')

        if from_wallet_id == to_wallet_id:
            return "No se puede transferir entre la misma cartera."

        transfer = Transfer(
            amount=amount,
            date=date,
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            note=note
        )

        db.session.add(transfer)
        db.session.commit()
        return redirect(url_for('manage_transfers'))

    transfers = Transfer.query.order_by(Transfer.date.desc()).all()
    return render_template('transfers.html', wallets=wallets, transfers=transfers)

@app.route('/wallet-summary')
def wallet_summary():
    wallets = Wallet.query.all()
    summaries = []

    for wallet in wallets:
        income = sum(t.amount for t in wallet.transactions if t.type == 'income')
        expense = sum(abs(t.amount) for t in wallet.transactions if t.type == 'expense')
        loan_total = sum(l.amount for l in wallet.loans if l.status == 'open')
        transfer_in = sum(t.amount for t in Transfer.query.filter_by(to_wallet_id=wallet.id).all())
        transfer_out = sum(t.amount for t in Transfer.query.filter_by(from_wallet_id=wallet.id).all())

        # 👇 Balance inicial: si es crédito, se suma a la deuda
        adjusted_initial = wallet.initial_balance
        if wallet.type.lower() == 'crédito':
            loan_total += adjusted_initial
        else:
            income += adjusted_initial

        net_balance = income - expense + transfer_in - transfer_out - loan_total

        summaries.append({
            'wallet': wallet,
            'income': income,
            'expense': expense,
            'transfer_in': transfer_in,
            'transfer_out': transfer_out,
            'loan_total': loan_total,
            'net_balance': net_balance,
            'initial_balance': adjusted_initial
        })

    total_balance = sum(summary['net_balance'] for summary in summaries)
    total_loans = sum(summary['loan_total'] for summary in summaries)

    return render_template(
        'wallet_summary.html',
        summaries=summaries,
        total_balance=total_balance,
        total_loans=total_loans
    )

@app.route('/wallets/add', methods=['GET', 'POST'])
def add_wallet():
    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']
        limit = request.form.get('limit') or None
        cutoff_day = request.form.get('cutoff_day') or None
        payment_day = request.form.get('payment_day') or None

        # Usamos los campos separados según el tipo de cartera
        credit_balance = request.form.get('credit_initial_balance')
        non_credit_balance = request.form.get('non_credit_initial_balance')
        initial_balance = float(credit_balance or non_credit_balance or 0)


        new_wallet = Wallet(
            name=name,
            type=type_,
            initial_balance=initial_balance,
            limit=float(limit) if limit else None,
            cutoff_day=int(cutoff_day) if cutoff_day else None,
            payment_day=int(payment_day) if payment_day else None
        )

        db.session.add(new_wallet)
        db.session.commit()

        return redirect(url_for('wallet_summary'))

    return render_template('add_wallet.html')


@app.route('/wallets/<int:wallet_id>/edit', methods=['GET', 'POST'])
def edit_wallet(wallet_id):
    wallet = Wallet.query.get_or_404(wallet_id)

    if request.method == 'POST':
        wallet.name = request.form['name']
        wallet.type = request.form['type']

        # Tomar balances según el tipo
        credit_balance = request.form.get('credit_initial_balance')
        non_credit_balance = request.form.get('non_credit_initial_balance')
        wallet.initial_balance = float(credit_balance or non_credit_balance or 0)

        # Otros campos opcionales
        wallet.limit = float(request.form.get('limit')) if request.form.get('limit') else None
        wallet.cutoff_day = int(request.form.get('cutoff_day')) if request.form.get('cutoff_day') else None
        wallet.payment_day = int(request.form.get('payment_day')) if request.form.get('payment_day') else None

        db.session.commit()
        return redirect(url_for('wallet_summary'))

    return render_template('edit_wallet.html', wallet=wallet)




if __name__ == '__main__':
    app.run(debug=True)

import json
from datetime import date
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)


app.jinja_env.globals['enumerate'] = enumerate

DATA_FILE = 'expenses.json'


def load_expenses():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_expenses(expenses):
    with open(DATA_FILE, 'w') as f:
        json.dump(expenses, f, indent=2)


@app.route('/')
def index():
    expenses = load_expenses()
    total = sum(e['price'] * e['quantity'] for e in expenses)
    count = len(expenses)
    biggest = max((e['price'] * e['quantity'] for e in expenses), default=0)
    category_totals = {}
    for e in expenses:
        line_total = e['price'] * e['quantity']
        if e['category'] in category_totals:
            category_totals[e['category']] += line_total
        else:
            category_totals[e['category']] = line_total

    category_breakdown = []
    for cat, amt in category_totals.items():
        percentage = (amt / total * 100) if total > 0 else 0
        category_breakdown.append({'category': cat, 'amount': amt, 'percentage': percentage})

    return render_template(
        'index.html',
        expenses=expenses,
        total=total,
        count=count,
        biggest=biggest,
        category_breakdown=category_breakdown

    )


@app.route('/add', methods=['POST'])
def add_expense():
    description = request.form['description']
    price = float(request.form['price'])
    category = request.form['category']
    quantity = int(request.form['quantity'])
    expense_date = str(date.today())

    expenses = load_expenses()
    found = False
    for e in expenses:
        if (e['date'] == expense_date) and (e['category'] == category) and (e['description'] == description):
            e['quantity'] += quantity
            found = True
            break
    if not found:
        expenses.append({'category': category, 'description': description,
                         'price': price, 'date': expense_date, 'quantity': quantity})
    save_expenses(expenses)

    return redirect(url_for('index'))


@app.route('/delete/<int:index>')
def delete_expense(index):
    expenses = load_expenses()
    expenses.pop(index)
    save_expenses(expenses)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# EasySplitter by Alex Cheng

from sample_bill_data import add_sample_bills
import login
import datetime

from flask import Flask, render_template, redirect, url_for, request, flash

from wtforms import Form, StringField, FloatField, RadioField, DateField
from wtforms.validators import InputRequired

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, desc, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

application = Flask(__name__)
Base = declarative_base()

# Defining table columns.
class BillSpending(Base):
    __tablename__ = 'spending'

    id = Column('spending', Integer, primary_key=True,autoincrement=True)
    user_id = Column('user_id', Integer)  # either 0 or 1
    amt_spent = Column('amt_spent', Integer)
    detail = Column('detail', Integer, ForeignKey('detail.detail'))


class BillDetail(Base):
    __tablename__ = 'detail'

    id = Column('detail', Integer, primary_key=True, autoincrement=True)
    date = Column('date', Date)
    restaurant = Column('restaurant', String(30))
    notes = Column('notes', String(60))
    who_paid = Column('who_paid', Integer)


# Form object for bill input on add.html
class BillForm(Form):
    user_0_spending = FloatField('Alex Spending', [InputRequired()])
    user_1_spending = FloatField('Jenn Spending', [InputRequired()])
    restaurant = StringField('Restaurant', [InputRequired()])
    date = DateField('Date (YYYY-MM-DD)', [InputRequired()])
    notes = StringField('Notes', [InputRequired()])
    who_paid = RadioField('Who Paid?', choices=[(0, 'Alex'), (1, 'Jenn'), (2, 'Split')], default=2)


# MySQL database login details, username, password, and address from login.py.
connection_string = 'mysql+pymysql://' + login.database_str

# Connect to database via engine creation.
engine = create_engine(connection_string, echo=False)
Base.metadata.create_all(bind=engine)

# Create SQLAlchemy session
SQL_Session = sessionmaker(engine)
sql_sess = SQL_Session()

# Uncomment to add sample data to database
# if __name__ == '__main__':
#     add_sample_bills(sql_sess)

# Creating home route, includes SQLAlchemy queries for displaying data
@application.route('/')
def home():
    # Query for spending to display bills for each user
    bill_qry_list = []
    for i in range(0, 2):
        bill_qry_list.append(
            sql_sess.query(BillSpending, BillDetail).join(BillDetail, BillSpending.detail == BillDetail.id).
            filter(BillSpending.user_id == i).
            order_by(desc(BillDetail.date)))

    # Calculate when two weeks ago was for calculating spending in the last two weeks
    two_weeks_ago = (datetime.datetime.today() - datetime.timedelta(days=14)).strftime('%Y-%m-%d')

    # Query for spending in the last two weeks
    two_weeks_spending_list = [0,0]
    for i in range(0, 2):
        spending = sql_sess.query(func.sum(BillSpending.amt_spent)). \
            join(BillDetail, BillSpending.detail == BillDetail.id). \
            filter(BillSpending.user_id == i). \
            filter(BillDetail.date >= two_weeks_ago).scalar()
        if spending:
            two_weeks_spending_list[i] = spending

    # Calculate how much each person spent on the other, recycles query for general bill spending
    user_0_cover_spending = 0
    user_1_cover_spending = 0

    for bills in bill_qry_list[0]:
        if bills.BillDetail.who_paid == 1:
            user_1_cover_spending += bills.BillSpending.amt_spent

    for bills in bill_qry_list[0]:
        if bills.BillDetail.who_paid == 0:
            user_0_cover_spending += bills.BillSpending.amt_spent

    # Create string to display who covered how much money
    if user_0_cover_spending > user_1_cover_spending:
        spent_more = "Alex has covered $" + str((user_0_cover_spending - user_1_cover_spending) / 100) + " for Jenn"
    else:
        spent_more = "Jenn has covered $" + str((user_1_cover_spending - user_0_cover_spending) / 100) + " for Alex"

    # Pass information to HTML files for display
    return render_template(
        'home.html', bill_qry_list=bill_qry_list,
        spent_more=spent_more, two_weeks_spending_list=two_weeks_spending_list)


# Creating about route
@application.route('/about')
def about():
    return render_template('about.html')


# Creating route for adding a bill to the database
@application.route('/addbill', methods = ['GET', 'POST'])
def addbill():
    # Use WTForms to input data into database
    form = BillForm(request.form)
    if request.method == 'POST':
        detail = BillDetail()
        detail.restaurant = form.restaurant.data
        detail.date = form.date.data
        detail.notes = form.notes.data
        detail.who_paid = form.who_paid.data

        # Flush so the detail ID is created to be used as the BillSpending object's foreign key
        sql_sess.add(detail)
        sql_sess.flush()

        # Creating user 0 spending object
        spending_0 = BillSpending()
        spending_0.user_id = 0
        spending_0.amt_spent = int(form.user_0_spending.data * 100)
        spending_0.detail = detail.id

        # Creating user 1 spending object
        spending_1 = BillSpending()
        spending_1.user_id = 1
        spending_1.amt_spent = int(form.user_1_spending.data * 100)
        spending_1.detail = detail.id

        # Adding the spending objects to the database
        sql_sess.add(spending_0)
        sql_sess.add(spending_1)

        sql_sess.commit()
        sql_sess.close()

        # Creating flash message for adding bill
        # flash("Bill Added!", 'success')

        # After POST writes to database, return home from '/addbill'
        return redirect(url_for('home'))

    # Pass form object to html page
    return render_template('add.html', form=form)


# Starts the Flask app
if __name__ == '__main__':
    application.secret_key = login.secret_key
    application.run(debug=False)

# data for adding sample bills to MySQL database
def sample_bills():
    bill_list = [
        {
            'spending_0': 12.12,
            'spending_1': 14.78,
            'date': '2018-04-23',
            'restaurant': 'Seto',
            'notes': 'sushi was good',
            'who_paid': 0
        },
        {
            'spending_0': 17.29,
            'spending_1': 16.87,
            'date': '2018-04-29',
            'restaurant': 'Falafel House',
            'notes': 'crispy falafels',
            'who_paid': 1
        },
        {
            'spending_0': 9.23,
            'spending_1': 10.98,
            'date': '2018-05-02',
            'restaurant': 'Whole Foods',
            'notes': 'quick lunch',
            'who_paid': 0
        },
        {
            'spending_0': 25.24,
            'spending_1': 27.28,
            'date': '2018-05-06',
            'restaurant': 'Benihana',
            'notes': 'anniversary date',
            'who_paid': 1
        },
        {
            'spending_0': 13.14,
            'spending_1': 14.20,
            'date': '2018-05-03',
            'restaurant': 'Pizza Kitchen',
            'notes': 'great mushrooms',
            'who_paid': 0
        },
        {
            'spending_0': 4.21,
            'spending_1': 5.89,
            'date': '2018-06-08',
            'restaurant': '7-11',
            'notes': 'chips and drink',
            'who_paid': 1
        },
        {
            'spending_0': 17.80,
            'spending_1': 20.31,
            'date': '2018-06-10',
            'restaurant': 'Orenchi Ramen',
            'notes': 'wait was long',
            'who_paid': 0
        }
    ]
    return bill_list


# adds sample data to MySQL database
def add_sample_bills(sql_sess):
    from application import BillDetail, BillSpending
    for bill in sample_bills():
        detail = BillDetail()
        detail.restaurant = bill['restaurant']
        detail.date = bill['date']
        detail.notes = bill['notes']
        detail.who_paid = bill['who_paid']
        sql_sess.add(detail)
        sql_sess.flush()

        # Creating user 0 spending object
        bill_0 = BillSpending()
        bill_0.user_id = 0
        bill_0.amt_spent = int(bill['spending_0'] * 100)
        bill_0.detail = detail.id

        # Creating user 1 spending object
        bill_1 = BillSpending()
        bill_1.user_id = 1
        bill_1.amt_spent = int(bill['spending_1'] * 100)
        bill_1.detail = detail.id

        sql_sess.add(bill_0)
        sql_sess.add(bill_1)

    sql_sess.commit()
    sql_sess.close()

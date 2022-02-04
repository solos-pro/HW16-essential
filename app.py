from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import raw_data
import json
import prettytable


app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CONTENT_TYPE = {'Content-Type': 'application/json; charset=utf-8'}

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
        }


class Offer(db.Model):
    __tablename__ = 'offer'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "executor_id": self.executor_id,
        }


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    start_date = db.Column(db.String(100))
    end_date = db.Column(db.String(100))
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "address": self.address,
            "price": self.price,
            "customer_id": self.customer_id,
            "executor_id": self.executor_id,
        }


db.create_all()


for data_user in raw_data.users:
    new_user = User(
        id=data_user["id"],
        first_name=data_user["first_name"],
        last_name=data_user["last_name"],
        age=data_user["age"],
        email=data_user["email"],
        role=data_user["role"],
        phone=data_user["phone"],
    )
    db.session.add(new_user)
    db.session.commit()

for data_order in raw_data.orders:
    new_order = Order(
        id=data_order["id"],
        name=data_order["name"],
        description=data_order["description"],
        start_date=data_order["start_date"],
        end_date=data_order["end_date"],
        price=data_order["price"],
        customer_id=data_order["customer_id"],
        executor_id=data_order["executor_id"],
    )
    db.session.add(new_order)
    db.session.commit()

for data_offer in raw_data.offers:
    new_offer = Offer(
        id=data_offer["id"],
        order_id=data_offer["order_id"],
        executor_id=data_offer["executor_id"],
    )
    db.session.add(new_offer)
    db.session.commit()


@app.route("/users", methods=['GET', 'POST'])
def users():
    if request.method == "GET":
        res = []
        for u in User.query.all():
            res.append(u.to_dict())
        return json.dumps(res), 200, CONTENT_TYPE


@app.route("/user/<int:uid>", methods=['GET', 'POST', 'DELETE', 'PUT'])
def user(uid):
    if request.method == "GET":
        return json.dumps(User.query.get(uid).to_dict()), 200, CONTENT_TYPE
    elif request.method == "DELETE":
        del_user = User.query.get(uid)
        db.session.delete(del_user)
        db.session.commit()
        return "", 204
    elif request.method == "POST":
        u = User.query.get(uid)
        # user_data = json.loads(request.form)
        u.first_name = request.form.get('first_name')
        u.last_name = request.form.get('last_name')
        u.age = request.form.get('age')
        u.email = request.form.get('email')
        u.role = request.form.get('role')
        u.phone = request.form.get('phone')
        db.session.add(u)
        db.session.commit()

        rows = [[x.id, x.first_name, x.last_name,
                 x.age, x.email, x.role, x.phone] for x in do_request()]
        mytable.add_rows(rows)
        print(mytable)
        return "", 204


@app.route("/test_test", methods=['GET', 'POST'])
def testtt():
    if request.method == "GET":
        return render_template("test.html")


def do_request():
    result = db.session.query(User).limit(5).all()
    return result


mytable = prettytable.PrettyTable()
mytable.field_names = [
    'id', 'first_name', 'last_name',
    'age', 'email', 'role', 'phone']

rows = [[x.id, x.first_name, x.last_name,
         x.age, x.email, x.role, x.phone] for x in do_request()]
mytable.add_rows(rows)
mytable.max_width = 25


# print('Запрос возвращает следующие записи:')
# print(mytable)

if __name__ == '__main__':
    app.run(debug=True)


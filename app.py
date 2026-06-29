from flask import Flask, request, jsonify
from models.classes import User, Meal
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

login_manager = LoginManager()
db.init_app(app)
login_manager.login_view = 'login'

"""
===============================================================GERENCIAMENTO SOBRE USUARIO==============================================================================
"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(str.encode(password), user.password):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Autenticação realizada com sucesso"})
        
    return jsonify({"message": "Credenciais inválidas"}), 400

@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso"})

@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if email and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(email=email, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuario cadastrado com sucesso"})
    return jsonify({"message": "Credenciais inválidas"}), 400

@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return {"username": user.username}
    return jsonify({"message": "Usuario não encontrado"}), 404

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if id_user != current_user.id and current_user.role == 'user':
        return jsonify({"message": "Operação não permitida"}), 403
    
    if user and data.get("password"):
        user.password = data.get("password")
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} atualizado com sucesso"})
    return jsonify({"message": "Usuário não encontrado"}), 404

@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if current_user.role != 'admin':
        return jsonify({"message": "Operação não permitida"}), 403
    if id_user == current_user.id:
        return jsonify({"message": "Deleção não permitida"})
    
    if user:
        db.session.delte(user)
        db.session.commit()

        return jsonify({"message": f"Usuario {id_user} deletado com sucesso"})
    
    return jsonify({"message": "Usuário não encontrado"}), 404


"""
===============================================================GERENCIAMENTO SOBRE DIETA==============================================================================
"""

def verificacao_user(id_user):
    if id_user != current_user.id:
        return jsonify({"message": "Tentando acessar outro usuario! Não vai conseguir(Credenciais Inválidas)"}), 400

@app.route("/user/<int:id_user>/refeicao", methods=["POST"])
@login_required
def create_meal(id_user):
    user = User.query.get(id_user)
    data = request.json
    name = data.get("name")
    description = data.get("description")
    meal_time = data.get("meal_time")
    in_diet = data.get("in_diet")

    verificacao_user(user.id)

    if name and meal_time and in_diet:
        meal = Meal(name=name, description=description, meal_time=meal_time, in_diet=in_diet)
        db.session.add(meal)
        db.session.commit()
        return jsonify({"message": "Refeição cadastrada com sucesso!"})
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
from flask import Flask, request, jsonify
from models.classes import User, Meal
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt 
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = '1234'
login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

"""
===============================================================GERENCIAMENTO SOBRE USUARIO==============================================================================
"""

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

#Login de usuario
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get('email')
    #username = data.get('username')
    password = data.get('password')

    if email and password:
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(str.encode(password), user.password):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Autenticação realizada com sucesso"})
        
    return jsonify({"message": "Credenciais inválidas"}), 401

#Logout de usuario
@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso"})

#Cadastro de usuario novo
@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if email and username and password:
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"message": "Email já cadastrado"}), 409
        
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(email=email, username=username, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuario cadastrado com sucesso"})
    return jsonify({"message": "Input errado"}), 400

#Busca por um usuario
@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return {"username": user.username}
    return jsonify({"message": "Usuario não encontrado"}), 404

#Atualização de usuario
@app.route("/user/<int:id_user>", methods=["PATCH"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)
    
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if user:
        if id_user != current_user.id and current_user.role == 'user':
            return jsonify({"message": "Operação não permitida"}), 403

        if not (email or username or password):
            return jsonify({"message": "Nenhum campo alterado"}), 400
        if email:
            user.email = email
        if password:
            user.password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        if username:
            user.username = username
        db.session.commit()
        return jsonify({"message": f"Usuário {id_user} atualizado com sucesso"})
        
    return jsonify({"message": "Usuário não encontrado"}), 404

#Deleção de usuario
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

# def verificacao_user(id_user):
#     if id_user != current_user.id:
#         return jsonify({"message": "Tentando acessar outro usuario! Não vai conseguir(Credenciais Inválidas)"}), 400

#Cadastro de refeicao por usuario
@app.route("/user/<int:id_user>/refeicao", methods=["POST"])
@login_required
def create_meal(id_user):
    data = request.json
    name = data.get("name")
    description = data.get("description")
    meal_time = data.get("meal_time")
    in_diet = data.get("in_diet")

    if id_user != current_user.id:
        return jsonify({"message": "olha tentando fazer pro outro user KKKKKKKKKKKKKKKKKKKKKKK"}), 401

    if name and meal_time and in_diet is not None:
        meal_time_convertido = datetime.strptime(meal_time, "%d/%m/%Y %H:%M:%S")
        meal = Meal(name=name, description=description, meal_time=meal_time_convertido, in_diet=in_diet, id_user=id_user)
        db.session.add(meal)
        db.session.commit()
        return jsonify({"message": "Refeição cadastrada com sucesso!"})

#Listagem de todas as refeicoes por usuario
@app.route("/user/<int:id_user>/lista_refeicoes", methods=["GET"])
@login_required
def read_refeicoes(id_user):
    if id_user != current_user.id:
        return jsonify({"message": "olha tentando fazer pro outro user KKKKKKKKKKKKKKKKKKKKKKK"}), 401

    user = User.query.get(id_user)
    """filter_by(id_user=id_user).all()
    gera o SQL equivalente a SELECT * FROM meal WHERE id_user = :id_user.
    .all()
    """
    meals = Meal.query.filter_by(id_user=id_user).all()
    if user:
        resultado = [
            {
            "id": meal.id,
            "name": meal.name,
            "description": meal.description,
            "meal_time": meal.meal_time.strftime("%d/%m/%Y %H:%M:%S"),
            "in_diet": meal.in_diet
            }
            for meal in meals
        ]
        if resultado:
            return jsonify({f"meal's {user.username}": resultado})
        else:
            return jsonify({f"meal's {user.username}": "Nenhuma refeição cadastrada"})
    
#Rota de alteração de refeicao
@app.route("/user/<int:id_user>/<int:id_meal>", methods=["PATCH"])
@login_required
def update_meal(id_user, id_meal):
    if id_user != current_user.id: 
        return jsonify({"message": "olha tentando fazer pro outro user KKKKKKKKKKKKKKKKKKKKKKK"}), 401
    user = User.query.get(id_user)
    meal = Meal.query.get(id_meal)

    data = request.json
    name = data.get("name")
    description = data.get("description")
    meal_time = data.get("meal_time")
    in_diet = data.get("in_diet")

    if user and meal:
        if id_user != current_user.id and current_user.role == "user":
            return jsonify({"message": "Operação não permitida"}), 403
        
        if not (name or description, meal_time, in_diet):
            return jsonify({"message": "Nenhum campo alterado"}), 400
        if name:
            meal.name = name
        if description:
            meal.description = description
        if meal_time:
            meal_time_convertido = datetime.strptime(meal_time, "%d/%m/%Y %H:%M:%S")
            meal.meal_time = meal_time_convertido
        if in_diet:
            meal.in_diet = in_diet
        db.session.commit()
        return jsonify({"message": f"Refeição {meal.name} atualizada com sucesso!"})
    
    return jsonify({"message": "Refeição não encontrada"}), 404

@app.route("/user/<int:id_user>/<int:id_meal>", methods=["DELETE"])
@login_required
def delete_meal(id_user, id_meal):
    user = User.query.get(id_user)
    meal = Meal.query.get(id_meal)
    if id_user != current_user.id: 
        return jsonify({"message": "olha tentando fazer pro outro user KKKKKKKKKKKKKKKKKKKKKKK"}), 401

    if user and meal:
        if id_user != current_user.id and current_user.role == "user":
            return jsonify({"message": "Operação não permitida"}), 403
    
    if user:
        db.session.delete(meal)
        db.session.commit()
        return jsonify({"message": f"Refeição {meal.name} deletada com sucesso!"})
    
    return jsonify({"message": "Refeição não encontrada"}), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
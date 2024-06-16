from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import google.oauth2.credentials
import base64
import os
import requests
from functools import wraps

app = Flask(__name__)


app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_users'

db = SQLAlchemy(app)

# Substitua pelos seus próprios valores do Google OAuth2
app.config["GOOGLE_OAUTH_CLIENT_ID"] = "477235057610-9dsr7gv8h8t0u3l2jvrft0jub3uoj0jn.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "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"

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id='477235057610-9dsr7gv8h8t0u3l2jvrft0jub3uoj0jn.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
)

#--------------------------------- Funções -----------------------------------

# Chave API
os.environ['STABILITY_API_KEY'] = 'sk-Yfp99POrmHO0N7bAUHO5ptUgPBkG9Q5t9Sln3kHkm3HFq5LC'

engine_id = "stable-diffusion-xl-1024-v1-0"
api_host = os.getenv('API_HOST', 'https://api.stability.ai')
api_key = os.getenv("STABILITY_API_KEY")

if api_key is None:
    raise Exception("Missing Stability API key.")

@app.route('/generate_image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt', '')

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1536,
            "width": 640,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        return jsonify({"error": "Non-200 response: " + str(response.text)}), response.status_code

    data = response.json()

    if "artifacts" not in data:
        return jsonify({"error": "No artifacts found in response"}), 500

    image_urls = []

    for i, image in enumerate(data["artifacts"]):
        image_path = f"static/out/v1_txt2img_{i}.png"
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image["base64"]))
        image_urls.append(f"/{image_path}")

    return jsonify({"urls": image_urls})

# Criando login de usuário com a conta Google
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))

    def __init__(self, email, name, password=None):
        self.email = email
        self.name = name
        if password:
            self.password = generate_password_hash(password)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            # Aqui você pode redirecionar para o modal ou para outra página
            # Pode ser útil definir uma variável de sessão para a página atual
            return redirect(url_for('show_modal_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ------------------------------- Rotas -----------------------

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('name', None)
    session.pop('user_id', None)
    
    return redirect('/')

@app.route('/auth')
def authorize():
    try:
        token = google.authorize_access_token()
        user_info_resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo', token=token)
        user_info = user_info_resp.json()
        email = user_info.get('email')
        name = user_info.get('name')
        
        if not email:
            raise ValueError("Email not found in user_info", user_info)
        
        session['email'] = email
        session['name'] = name

        # Verifica se o usuário já existe no banco de dados
        user = User.query.filter_by(email=email).first()
        if not user:
                new_user = User(email=email, name=name)
                db.session.add(new_user)
                db.session.commit()
        
        # Simulação de um user_id
        session['user_id'] = email.split('@')[0]
        print('Usuário autenticado com sucesso:', email)
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        print('Erro durante a autorização:', e)
    
    return redirect('/')

@app.route('/create')
def create():
    image_url = request.args.get('imageUrl')
    return render_template('create.html', image_url=image_url)

# Run app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

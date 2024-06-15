from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import base64
import os
import requests
import google.oauth2.credentials


app = Flask(__name__)
app.secret_key = os.urandom(24)

# Substitua pelos seus próprios valores do Google OAuth2
app.config["GOOGLE_OAUTH_CLIENT_ID"] = "477235057610-9dsr7gv8h8t0u3l2jvrft0jub3uoj0jn.apps.googleusercontent.com"
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "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"

google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        resp = google.get("/plus/v1/people/me")
        assert resp.ok, resp.text
    except InvalidGrantError:
        return redirect(url_for("google.login"))

    user_info = resp.json()
    session["user_info"] = user_info
    return f"Logged in as {user_info['displayName']}"

@app.route("/logout")
def logout():
    session.pop("user_info", None)
    return redirect(url_for("index"))



# Run app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

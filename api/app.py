from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth
import os, json

# importa lógica da API
from api.API import gerar_novas_perguntas, gerar_nota_perguntas, ApiGeminiException

app = Flask(__name__, static_folder="../", static_url_path="")
CORS(app)

# inicializa firebase
firebase_credentials_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
if not firebase_credentials_json:
    raise RuntimeError("Variável FIREBASE_SERVICE_ACCOUNT_JSON não encontrada!")
firebase_credentials_dict = json.loads(firebase_credentials_json)
cred = credentials.Certificate(firebase_credentials_dict)
firebase_admin.initialize_app(cred)

# --- Rotas API ---
@app.route('/api/gerar-pergunta', methods=['POST'])
def gerar_pergunta_route():
    try:
        id_token = request.headers.get('Authorization').split('Bearer ')[1]
        auth.verify_id_token(id_token)
    except Exception as e:
        return jsonify({"erro": f"Autenticação falhou: {e}"}), 401

    data = request.json
    tema = data.get('tema', 'curiosidades gerais')
    dificuldade = data.get('dificuldade', 'fácil')
    quantidade = data.get('quantidade', 1)

    try:
        perguntas = gerar_novas_perguntas(tema, dificuldade, quantidade)
        return jsonify({"perguntas": perguntas})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/avaliar-resposta', methods=['POST'])
def avaliar_resposta_route():
    try:
        id_token = request.headers.get('Authorization').split('Bearer ')[1]
        auth.verify_id_token(id_token)
    except Exception as e:
        return jsonify({"erro": f"Autenticação falhou: {e}"}), 401

    data = request.json
    pergunta = data.get('pergunta')
    resposta_usuario = data.get('respostaUsuario')
    if not pergunta or not resposta_usuario:
        return jsonify({"erro": "pergunta e respostaUsuario obrigatórios"}), 400

    try:
        resultado = gerar_nota_perguntas(resposta_usuario, pergunta)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# --- Servir frontend ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

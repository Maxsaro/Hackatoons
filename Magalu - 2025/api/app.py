from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth
import os
import json

# ✅ IMPORTA AS FUNÇÕES E O ERRO CUSTOMIZADO DO SEU FICHEIRO 'API.py'
# Garanta que o seu outro ficheiro se chama 'API.py' e está na mesma pasta.
try:
    from API import gerar_novas_perguntas, gerar_nota_perguntas, ApiGeminiException
except ImportError:
    print("!!! ERRO CRÍTICO: Não foi possível encontrar o ficheiro 'API.py' ou as funções necessárias nele.")
    # Encerra o programa se a importação falhar, pois o servidor não pode funcionar.
    exit()

# --- CONFIGURAÇÃO DO SERVIDOR ---
app = Flask(__name__)
# Habilita o CORS para permitir que o seu frontend JavaScript aceda a esta API
CORS(app)

# Inicializa o Firebase Admin SDK (para segurança)
try:
    # Pega o conteúdo JSON da variável de ambiente
    firebase_credentials_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
    if not firebase_credentials_json:
        raise ValueError("A variável de ambiente FIREBASE_SERVICE_ACCOUNT_JSON não foi definida.")

    # Converte a string JSON para um dicionário Python
    firebase_credentials_dict = json.loads(firebase_credentials_json)

    # Inicializa o Firebase com as credenciais do dicionário
    cred = credentials.Certificate(firebase_credentials_dict)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK inicializado com sucesso a partir de variável de ambiente.")

except Exception as e:
    print(f"!!! ERRO CRÍTICO ao inicializar o Firebase: {e}")
    exit()


# --- ROTA PARA GERAR PERGUNTAS ---
@app.route('/api/gerar-pergunta', methods=['POST'])
def gerar_pergunta_route():
    # 1. SEGURANÇA: Verifica o token do Firebase
    try:
        auth_header = request.headers.get('Authorization')
        id_token = auth_header.split('Bearer ')[1]
        decoded_token = auth.verify_id_token(id_token)
        print(f"Pedido para gerar pergunta autorizado para: {decoded_token['uid']}")
    except Exception as e:
        return jsonify({"erro": f"Autenticação falhou: {e}"}), 401

    # 2. RECEBE OS DADOS do JavaScript
    try:
        data = request.json
        tema = data.get('tema', 'curiosidades gerais')
        dificuldade = data.get('dificuldade', 'fácil')
        quantidade = data.get('quantidade', 1)
    except Exception:
        return jsonify({"erro": "Corpo da requisição JSON inválido ou ausente."}), 400

    # 3. CHAMA A LÓGICA do ficheiro API.py
    try:
        lista_de_perguntas = gerar_novas_perguntas(
            tema=tema, 
            dificuldade=dificuldade, 
            quantidade=quantidade
        )
        print(f"Perguntas sobre '{tema}' geradas com sucesso.")
        return jsonify({"perguntas": lista_de_perguntas}), 200

    except ApiGeminiException as e:
        print(f"ERRO da API do Gemini ao gerar perguntas: {e}")
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        print(f"ERRO inesperado no servidor: {e}")
        return jsonify({"erro": f"Um erro inesperado ocorreu no servidor: {e}"}), 500

# --- ROTA PARA AVALIAR RESPOSTAS ---
@app.route('/api/avaliar-resposta', methods=['POST'])
def avaliar_resposta_route():
    # 1. SEGURANÇA
    try:
        id_token = request.headers.get('Authorization').split('Bearer ')[1]
        decoded_token = auth.verify_id_token(id_token)
        print(f"Pedido de avaliação autorizado para: {decoded_token['uid']}")
    except Exception as e:
        return jsonify({"erro": f"Autenticação falhou: {e}"}), 401

    # 2. RECEBE OS DADOS
    try:
        data = request.json
        pergunta = data.get('pergunta')
        resposta_usuario = data.get('respostaUsuario')
        if not pergunta or not resposta_usuario:
            return jsonify({"erro": "'pergunta' e 'respostaUsuario' são obrigatórios."}), 400
    except Exception:
        return jsonify({"erro": "Corpo da requisição JSON inválido."}), 400

    # 3. CHAMA A LÓGICA
    try:
        resultado_avaliacao = gerar_nota_perguntas(pergunta=pergunta, resposta=resposta_usuario)
        print(f"Avaliação da resposta concluída com nota: {resultado_avaliacao.get('nota')}")
        return jsonify(resultado_avaliacao), 200 # Devolve diretamente o objeto {"nota": ..., "analise": ...}
        
    except ApiGeminiException as e:
        print(f"ERRO da API do Gemini ao avaliar: {e}")
        return jsonify({"erro": str(e)}), 500
    except Exception as e:
        print(f"ERRO inesperado no servidor ao avaliar: {e}")
        return jsonify({"erro": f"Um erro inesperado ocorreu no servidor: {e}"}), 500


# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == "__main__":
    # Esta linha "liga" o servidor e o faz esperar por requisições
    app.run(port=5000, debug=True)


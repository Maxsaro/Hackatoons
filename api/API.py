import requests as rq
from collections import deque
import json
import os

# Define um erro customizado para a nossa API
class ApiGeminiException(Exception):
    pass

# --- CONSTANTES DE CONFIGURAÇÃO DO MÓDULO ---
CONTROLE_REPETICOES = 15
HISTORICO_FILE = "historico_perguntas.json"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- FUNÇÕES DE AJUDA PARA O HISTÓRICO (sem alterações) ---
def load_historico():
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return deque(data, maxlen=CONTROLE_REPETICOES)
        except (json.JSONDecodeError, IOError):
            return deque(maxlen=CONTROLE_REPETICOES)
    return deque(maxlen=CONTROLE_REPETICOES)

def save_historico(perguntas_deque):
    try:
        with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
            json.dump(list(perguntas_deque), f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Erro ao salvar histórico: {e}")


# --- FUNÇÃO PRINCIPAL DA LÓGICA ---
def gerar_novas_perguntas(tema: str, dificuldade: str, quantidade: int):
    """
    Gera novas perguntas.
    Retorna uma lista de strings (perguntas) em caso de sucesso.
    Lança uma ApiGeminiException em caso de erro.
    """
    perguntas_anteriores = load_historico()
    historico_str = ", ".join(list(perguntas_anteriores))
    
    # --- SUAS CONFIGURAÇÕES DA IA (MANTIDAS) ---
    # ✅ NOTA: O modelo 'gemini-2.5-pro' foi trocado por um válido. Esta foi a única mudança necessária.
    model_name = "gemini-2.5-pro" 
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    url = f"{base_url}/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (f"Crie {quantidade} pergunta sobre o tema {tema} na dificuldade {dificuldade} mande apenas a pergunta nada mais, "
              f"se for mais que uma (mande uma por linha), é proibido repetir qualquer uma dessas perguntas {historico_str}")
    
    headers = {"Content-type" : "application/json"}
    
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": "Você é um professor auxiliando seus alunos a estudarem"}]},
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.1
        }
    }
    # --- FIM DAS SUAS CONFIGURAÇÕES ---

    try:
        response = rq.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        
        try:
            texto_gerado = response_data["candidates"][0]["content"]["parts"][0]["text"]
            novas_perguntas = [p.strip() for p in texto_gerado.splitlines() if p.strip()]

            if not novas_perguntas:
                raise ApiGeminiException("A IA não retornou nenhuma pergunta válida.")

            for p in novas_perguntas:
                perguntas_anteriores.append(p)
            save_historico(perguntas_anteriores)
            
            # ✅ RETORNA APENAS A LISTA DE PERGUNTAS
            return novas_perguntas

        except (KeyError, IndexError):
            raise ApiGeminiException("A resposta da API do Gemini pode ter sido bloqueada por segurança.")

    except rq.exceptions.RequestException as e:
        raise ApiGeminiException(f"Erro na requisição para a API do Gemini")
    
def gerar_nota_perguntas(resposta: str, pergunta: str) -> dict:
 
  model_name = "gemini-2.5-pro" 
  base_url = "https://generativelanguage.googleapis.com/v1beta/models"
  url = f"{base_url}/{model_name}:generateContent?key={GEMINI_API_KEY}"
  
  prompt = (
      f"Você é um professor a corrigir um quiz. A pergunta foi: '{pergunta}'. "
      f"A resposta do aluno foi: '{resposta}'. "
      "Avalie a resposta e retorne um objeto JSON com duas chaves: "
      "1. 'nota': um número inteiro de 0 a 100. "
      "2. 'analise': uma análise curta e construtiva (máximo 20 palavras). "
      "Responda APENAS com o objeto JSON, nada mais."
  )
  headers = {"Content-Type": "application/json"}

  payload = {
      "contents": [{"parts": [{"text": prompt}]}],
      "generationConfig": {
          "temperature": 0.1,
          "responseMimeType": "application/json",
      }
  }
  
  try:
      response = rq.post(url, headers=headers, json=payload, timeout=30)
      response.raise_for_status()
      response_data = response.json()
      
      try:
          texto_gerado_json = response_data["candidates"][0]["content"]["parts"][0]["text"]
          dados_avaliacao = json.loads(texto_gerado_json)
          
          if "nota" not in dados_avaliacao or "analise" not in dados_avaliacao:
              raise ApiGeminiException("A resposta da IA não contém as chaves 'nota' e 'analise'.")
          
          # ✅ CORREÇÃO: Retorna um dicionário, que é a forma correta.
          return dados_avaliacao 
          
      except (KeyError, IndexError, json.JSONDecodeError):
          raise ApiGeminiException("A resposta da IA não veio no formato JSON esperado ou foi bloqueada.")
  except rq.exceptions.RequestException as e:

      raise ApiGeminiException(f"Erro na requisição para a API do Gemini")


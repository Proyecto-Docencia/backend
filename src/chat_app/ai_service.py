# chat_app/ai_service.py
import os
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")
# La API key se toma de la variable de entorno GEMINI_API_KEY
# Si no existe, evitamos inicializar el cliente para no fallar en tests o dev sin clave.
client = genai.Client() if os.environ.get("GEMINI_API_KEY") else None

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
# Si quieres desactivar "thinking" por costo/latencia, usa 0 (recomendado para respuestas rápidas)
THINKING_BUDGET = int(os.environ.get("GEMINI_THINKING_BUDGET", "0"))

def consultar_gemini(prompt_usuario: str) -> str:
    """
    Llama al modelo Gemini con un prompt estructurado.
    """
    print(f"--- DEBUG: Recibido en backend: '{prompt_usuario}' ---") # LOG DE DEBUG

    if not prompt_usuario.strip():
        return "Por favor ingresa un mensaje."
    if client is None:
        return "La IA (Gemini) no está configurada. Define GEMINI_API_KEY para habilitarla."

    # Prompt estructurado para guiar al modelo
    prompt_estructurado = f"""
    Eres un asistente virtual para docentes de la Universidad San Sebastián.
    Tu rol es ser amable, servicial y responder preguntas sobre material educativo, planificaciones de clases y temas académicos.
    Mantén tus respuestas concisas y directas.

    Pregunta del docente: "{prompt_usuario}"
    
    Respuesta:
    """

    try:
        # Configuración correcta según la nueva documentación
        cfg = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET)
        )

        # Llamada correcta: client.models.generate_content y parámetro 'config'
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt_estructurado],
            config=cfg,
        )
        
        text = getattr(resp, "text", "") or ""
        print(f"--- DEBUG: Respuesta generada por IA: '{text.strip()}' ---") # LOG DE DEBUG
        return text.strip() or "La IA no devolvió contenido."
    except Exception as e:
        print(f"--- ERROR en Gemini: {e} ---") # LOG DE ERROR
        return f"Error al contactar con la IA: {e}"
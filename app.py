from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import base64
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
# Estas importaciones ya no son necesarias para la nueva implementación

# Cargar variables de entorno
load_dotenv()

# Configurar la API de Gemini
# Prioriza la variable de entorno, con fallback a la API key proporcionada
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or "AIzaSyA8fA0WW1rh72YU1W4pbxevrY_MwfiJbnw"  # Nueva API para Gemini 2.5 Pro
genai.configure(api_key=GEMINI_API_KEY)

# Habilitar registro detallado para diagnosticar problemas
import logging
logging.basicConfig(level=logging.INFO)

# Configurar el modelo generativo con manejo de errores
try:
    # Intentar obtener la lista de modelos disponibles
    print("Obteniendo lista de modelos disponibles...")
    models = genai.list_models()
    available_model_names = [model.name for model in models]
    print(f"Modelos disponibles: {available_model_names}")
    
    # Intentar diferentes nombres de modelos en este orden de preferencia
    model_options = [
        'gemini-1.5-pro',
        'gemini-pro',
        'models/gemini-pro',
        'models/gemini-1.5-pro',
        'gemini-1.0-pro'  # Fallback a una versión antigua si existe
    ]
    
    # Usar específicamente Gemini 2.5 Pro para nuestra aplicación
    model_name = "gemini-1.5-pro"
    print(f"Usando modelo: {model_name}")
    
    if model_name:
        model = genai.GenerativeModel(model_name)
    else:
        # Si no encontramos ninguno, usar el primer modelo disponible
        if available_model_names:
            model_name = available_model_names[0]
            print(f"Fallback al primer modelo disponible: {model_name}")
            model = genai.GenerativeModel(model_name)
        else:
            # Si no hay modelos disponibles, usar una función alternativa
            raise Exception("No se encontraron modelos disponibles")

except Exception as e:
    print(f"Error al configurar el modelo de Gemini: {e}")
    # Definir una función que simulará el modelo si hay problemas
    class MockModel:
        def generate_content(self, prompt):
            # Simular una respuesta para evitar que la aplicación falle completamente
            class MockResponse:
                def __init__(self):
                    self.text = json.dumps({
                        "estilo_aprendizaje": "No se pudo conectar con la IA. Asegúrate de que la API esté configurada correctamente.",
                        "temas_interes": ["No disponible - Error de conexión con API"],
                        "historias_recomendadas": [
                            {"titulo": "Historia 1", "introduccion": "No se pudieron generar historias debido a un error de conexión."},
                            {"titulo": "Historia 2", "introduccion": "Verifica tu conexión a internet y la configuración de la API."}
                        ],
                        "perfil_cognitivo": "No disponible debido a error de API",
                        "estrategias_enseñanza": ["No disponible"]
                    })
            return MockResponse()
    
    model = MockModel()
    print("Usando modelo simulado debido a errores de configuración")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'mp3'}

# Asegurarse de que exista la carpeta de subidas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_pdf_text(pdf_path):
    """Extraer texto de un archivo PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
        return text
    except Exception as e:
        print(f"Error al extraer texto del PDF: {e}")
        return "Error al procesar el PDF"

def transcribe_audio(audio_path):
    """Transcribir audio usando Gemini 2.5 Pro"""
    try:
        # Leer el archivo MP3 directamente en bytes
        print(f"Leyendo archivo de audio: {audio_path}")
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Convertir a base64 para enviar a la API
        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Crear un modelo multimodal de Gemini 2.5 Pro
        multimodal_model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Construir el prompt para la transcripción
        prompt = "Transcribe exactamente lo que se dice en este archivo de audio. Si está en español, mantén la transcripción en español. Si está en otro idioma, transcribe en ese idioma."
        
        # Procesar con Gemini 2.5 Pro como contenido multimodal
        print("Enviando audio a Gemini 2.5 Pro para transcripción...")
        response = multimodal_model.generate_content([
            prompt,
            {
                "mime_type": "audio/mp3",
                "data": encoded_audio
            }
        ])
        
        # Extraer la transcripción
        transcription = response.text.strip()
        print("Transcripción completada exitosamente")
        return transcription
        
    except Exception as e:
        print(f"Error al transcribir audio: {e}")
        return f"Error en la transcripción: {str(e)}"

def generate_ai_analysis(story_name, pdf_text, transcription=None):
    """Utilizar la API de Gemini para analizar los datos."""
    try:
        # Construir el prompt para Gemini
        prompt = f"""Eres un agente de inteligencia artificial de análisis lingüístico y cognitivo. 
        Necesito que analices la siguiente información y generes un perfil de estilo de aprendizaje 
        junto con recomendaciones de historias personalizadas.
        
        CONTEXTO INICIAL: {story_name}
        
        TRANSCRIPCIÓN DE AUDIO:
        {transcription if transcription else 'No disponible'}
        
        CONTENIDO DEL PDF (ENCUESTAS): 
        {pdf_text[:3000] if pdf_text else 'No disponible'}
        
        Basándote en esta información, realiza lo siguiente:
        
        1. Extrae y organiza las preguntas y respuestas de las encuestas si están presentes.
        2. Determina el posible estilo de aprendizaje (visual, auditivo, kinestésico o mixto).
        3. Identifica temas de interés y zonas de confort.
        4. Genera 5 introducciones breves para historias que podrían interesarle al estudiante.
        5. Crea una síntesis del perfil cognitivo y recomendaciones de enseñanza.
        
        Devuelve los resultados en formato JSON con estas claves:
        - estilo_aprendizaje: una descripción del estilo predominante
        - temas_interes: lista de temas que parecen interesarle
        - historias_recomendadas: array con 5 objetos que contengan título e introducción
        - perfil_cognitivo: descripción de tendencias de pensamiento
        - estrategias_enseñanza: recomendaciones prácticas
        """
        
        # Generar la respuesta con Gemini
        response = model.generate_content(prompt)
        
        # Extraer el JSON de la respuesta
        response_text = response.text
        
        # Intentar encontrar el contenido JSON en la respuesta
        try:
            # Buscar el contenido JSON entre bloques de código
            import re
            json_match = re.search(r'```json\n(.+?)\n```', response_text, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(1)
                result = json.loads(json_text)
            else:
                # Intentar parsear directamente toda la respuesta
                result = json.loads(response_text)
                
        except json.JSONDecodeError:
            # Si no se puede parsear como JSON, devolvemos un resultado genérico
            result = {
                "estilo_aprendizaje": "No se pudo determinar debido a datos insuficientes",
                "temas_interes": ["Tema 1", "Tema 2"],
                "historias_recomendadas": [
                    {"titulo": "Historia recomendada 1", "introduccion": response_text[:200]},
                    {"titulo": "Historia recomendada 2", "introduccion": "Introducción de muestra"},
                    {"titulo": "Historia recomendada 3", "introduccion": "Introducción de muestra"},
                    {"titulo": "Historia recomendada 4", "introduccion": "Introducción de muestra"},
                    {"titulo": "Historia recomendada 5", "introduccion": "Introducción de muestra"}
                ],
                "perfil_cognitivo": "Perfil basado en datos limitados",
                "estrategias_enseñanza": ["Estrategia 1", "Estrategia 2"]
            }
        
        return result
    
    except Exception as e:
        print(f"Error en el análisis con IA: {e}")
        return {
            "error": str(e),
            "estilo_aprendizaje": "Error al analizar con IA",
            "historias_recomendadas": []
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'audio_file' not in request.files or 'pdf_file' not in request.files:
        return jsonify({'error': 'Faltan archivos'}), 400
    
    audio_file = request.files['audio_file']
    pdf_file = request.files['pdf_file']
    
    if audio_file.filename == '' or pdf_file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if not (allowed_file(audio_file.filename) and allowed_file(pdf_file.filename)):
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
    
    try:
        # Guardar archivos temporalmente
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(pdf_file.filename))
        
        audio_file.save(audio_path)
        pdf_file.save(pdf_path)
        
        # Obtener contexto de la historia del nombre del archivo
        story_name = os.path.splitext(audio_file.filename)[0]
        
        # Extraer texto del PDF
        pdf_text = extract_pdf_text(pdf_path)
        
        # NUEVO: Transcribir el audio usando Gemini 2.5 Pro
        print("Iniciando transcripción de audio...")
        transcription = transcribe_audio(audio_path)
        print("Transcripción completa")
        
        # Usar Gemini para analizar los datos y generar recomendaciones
        # Ahora incluimos la transcripción en el análisis
        ai_analysis = generate_ai_analysis(story_name, pdf_text, transcription)
        
        # Generar resultados
        result = {
            'contexto_inicial': story_name,
            'transcripcion': transcription,
            'encuesta': pdf_text[:1000] + '...' if len(pdf_text) > 1000 else pdf_text,
            'estilo_aprendizaje': ai_analysis.get('estilo_aprendizaje', 'No determinado'),
            'temas_interes': ai_analysis.get('temas_interes', []),
            'perfil_cognitivo': ai_analysis.get('perfil_cognitivo', 'No determinado'),
            'estrategias_enseñanza': ai_analysis.get('estrategias_enseñanza', []),
            'historias_recomendadas': ai_analysis.get('historias_recomendadas', [])
        }
        
        # Guardar resultados en un archivo JSON
        result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resultados_analisis.json')
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error en la aplicación: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Only run in debug mode when running locally
    app.run(debug=True)
    
# PythonAnywhere will use the 'app' variable directly

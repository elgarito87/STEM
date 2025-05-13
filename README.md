# Análisis Lingüístico y Cognitivo

Aplicación web para analizar archivos de audio (MP3) y PDF, generando un perfil de estilo de aprendizaje y recomendaciones de historias personalizadas.

## Características

- Carga de archivos de audio (MP3) y PDF mediante arrastrar y soltar
- Transcripción automática de audio
- Extracción de texto de archivos PDF
- Análisis lingüístico del contenido
- Detección de estilo de aprendizaje
- Generación de historias personalizadas
- Interfaz intuitiva y responsiva

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- FFmpeg (para el procesamiento de audio)

## Instalación

1. Clona el repositorio o descarga los archivos
2. Crea un entorno virtual (recomendado):
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Instala FFmpeg:
   - En Windows: `choco install ffmpeg` o descárgalo de [aquí](https://ffmpeg.org/download.html)
   - En macOS: `brew install ffmpeg`
   - En Linux: `sudo apt install ffmpeg`

## Uso

1. Inicia la aplicación:
   ```
   python app.py
   ```
2. Abre tu navegador y ve a `http://localhost:5000`
3. Arrastra y suelta o haz clic para seleccionar un archivo de audio (MP3) y un archivo PDF
4. Haz clic en "Analizar Archivos"
5. Explora los resultados en las diferentes pestañas

## Estructura del Proyecto

- `app.py`: Aplicación principal de Flask
- `templates/`: Plantillas HTML
  - `index.html`: Interfaz de usuario principal
- `requirements.txt`: Dependencias de Python
- `uploads/`: Directorio para archivos cargados (se crea automáticamente)

## API

La aplicación expone los siguientes endpoints:

- `GET /`: Página principal
- `POST /upload`: Endpoint para cargar y procesar archivos

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Notas

- La aplicación está diseñada para funcionar en entornos locales
- El procesamiento de archivos grandes puede tardar varios segundos
- Se recomienda usar audios claros para una mejor transcripción

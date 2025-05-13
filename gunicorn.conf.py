# Configuración de Gunicorn para Render

bind = "0.0.0.0:10000"
workers = 2
timeout = 120  # Aumentamos el timeout para procesar archivos grandes
worker_class = "gevent"
threads = 4

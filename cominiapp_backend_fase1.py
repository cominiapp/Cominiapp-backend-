
import uuid
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS # <<<< LÍNEA CLAVE 1: Importar CORS
from google.cloud import firestore
# from firebase_admin import credentials, firestore, initialize_app # (Ya no es necesario, usamos google.cloud.firestore)

# --- 1. Configuración de la Aplicación Flask ---
# app = Flask(__name__)
# Habilita CORS para CodePen (CRUCIAL)
app = Flask(__name__)
CORS(app) # <<<< LÍNEA CLAVE 2: Inicializar CORS para la app

# --- 2. CONFIGURACIÓN DE FIRESTORE (NUEVA CONEXIÓN ESTABLE) ---
# Se autentica automáticamente con la clave GOOGLE_APPLICATION_CREDENTIALS
# que ya subiste a Render.
db = firestore.Client()
DRIVER_COLLECTION = 'DRIVERS'
REQUESTS_COLLECTION = 'REQUESTS'

# --- 3. Funciones de Acceso a Firestore (VÍA LIBRERÍA GOOGLE-CLOUD) ---

# [Endpoint GET /feed/community_id (MODIFICADO para usar db.collection().get())]
# [Endpoint GET /feed/community_id (MODIFICADO para usar db.collection().get())]
@app.route('/feed/community_id', methods=['GET'])
def get_firestore_posts():
    """Obtiene la colección de 'requests' (solicitudes) usando la librería de Firestore."""
    
    try:
        # Consulta todos los documentos en la colección REQUESTS
        docs = db.collection(REQUESTS_COLLECTION).stream()
        
        posts = []
        for doc in docs:
            # Convierte el documento de Firestore a un diccionario Python
            post = doc.to_dict()
            post['id'] = doc.id # Añade el ID único del documento
            posts.append(post)

        return jsonify(posts)
    
    except Exception as e:
        # Maneja la excepción al obtener datos de Firestore (ej: si falla la conexión)
        return jsonify({'success': False, 'message': f'Fallo al obtener datos: {e}'}), 500

# [Endpoint POST /driver/register (MODIFICADO para usar db.collection().set())]
@app.route('/driver/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400

    # 1. Generar ID único para el conductor (Driver ID)
    driver_id = str(uuid.uuid4())
    
    # 2. Preparar los datos del conductor
    driver_data = {
        'username': data.get('username'),
        'phone': data.get('phone'),
        'status': 'available',
        'location': 'TestingDefault', # Se actualizará con la ubicación real
        'community_id': 'Bahia Kino' # ID de la comunidad
    }

    try:
        # 3. Guardar en la colección 'DRIVERS' de Firestore (LÓGICA NUEVA ESTABLE)
        db.collection(DRIVER_COLLECTION).document(driver_id).set(driver_data)

        return jsonify({
            'success': True, 
            'message': 'Usuario registrado y listo para la fase 2.', 
            'user_id': driver_id
        })

    except Exception as e:
        # Manejo específico para Firestore/DB
        return jsonify({'success': False, 'message': f'Error al registrar conductor: {e}'}), 500


# --- 4. ENDPOINTS ADICIONALES (Lógica de la Aplicación) ---

# (Aquí se añadirían las funciones /taxi_request y /moto_request)

# --- 5. EJECUCIÓN SECUENCIAL (CRUCIAL) ---

if __name__ == '__main__':
    # Ejecuta el backend en el puerto 5000 (Render lo mapeará al puerto 80)
    app.run(host='0.0.0.0', port=5000, debug=True)

import uuid
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS # LINEA CLAVE 1: Importar CORS
from google.cloud import firestore

# --- 1. CONFIGURACIÓN DE LA APLICACIÓN FLASK ---
# app = Flask(__name__)
# Habilita CORS para CodePen (CRUCIAL)
app = Flask(__name__) # << ESTA linea debe ir sin espacios al inicio
CORS(app) # << ESTA linea debe ir sin espacios al inicio

# --- 2. CONFIGURACIÓN DE FIRESTORE (NUEVA CONEXIÓN ESTABLE) ---
# Se autentica automáticamente con la clave GOOGLE_APPLICATION_CREDENTIALS
# que ya subiste a Render.
db = firestore.Client()
DRIVER_COLLECTION = 'DRIVERS'
REQUESTS_COLLECTION = 'REQUESTS'

# --- 3. Funciones de Acceso a Firestore (VÍA LIBRERÍA GOOGLE-CLOUD) ---

# [Endpoint GET /feed/community_id (MODIFICADO para usar db.collection().get())]
@app.route('/feed/<community_id>', methods=['GET'])
def get_firestore_posts(community_id):
    """Consulta todos los documentos en la colección REQUESTS"""
    try:
        docs = db.collection(REQUESTS_COLLECTION).stream()
        posts = []
        
        for doc in docs:
            post = doc.to_dict()
            post['id'] = doc.id # Añade el ID único del documento
            posts.append(post)
            
        return jsonify(posts)

    except Exception as e:
        # Maneja la excepción al obtener datos de Firestore (ej: si falla la conexión)
        print(f"Error al obtener posts: {e}")
        return jsonify({'success': False, 'message': f'Fallo al obtener datos: {e}'}), 500


# [Endpoint POST /driver/register MODIFICADO para usar db.collection().set()]
@app.route('/driver/register', methods=['POST'])
def register_driver():
    # Lógica de lectura de JSON con manejo de errores (LA CORRECCIÓN)
    try:
        # Intenta leer el JSON de la solicitud
        data = request.get_json()
    except Exception as e:
        # Si falla la lectura de JSON (por ejemplo, el JSON está malformado)
        print(f"Error reading JSON: {e}")
        return jsonify({'success': False, 'message': 'Error al leer JSON: Formato incorrecto. Verifique el comando curl.'}), 400
        
    # A partir de aquí, el código original es válido:
    if not data:
        return jsonify({'success': False, 'message': 'Faltan datos requeridos (JSON vacío).'}), 400
        
    # 1. Generar ID único para el conductor (Driver ID)
    driver_id = str(uuid.uuid4())
    
    # 2. Preparar los datos del conductor
    driver_data = {
        'driver_id': driver_id,
        'username': data.get('username'),
        'phone': data.get('phone'),
        'status': 'available', # Disponible por defecto
        'location': firestore.GeoPoint(0, 0), # Ubicación de prueba, se actualizará
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
        print(f"Error al registrar conductor: {e}")
        return jsonify({'success': False, 'message': f'Error al registrar conductor: {e}'}), 500


# [Endpoint POST /taxi_request (LOGICA DE LA APLICACIÓN)]
# Endpoint para recibir las solicitudes de taxi/mototaxi
@app.route('/taxi_request', methods=['POST'])
def handle_taxi_request():
    try:
        data = request.get_json()
    except:
        return jsonify({'success': False, 'message': 'Error al leer JSON: Formato incorrecto.'}), 400

    if not data or not data.get('service_type') or not data.get('location'):
        return jsonify({'success': False, 'message': 'Faltan campos requeridos: service_type y location.'}), 400
    
    # 1. Crear documento de solicitud
    request_data = {
        'service_type': data.get('service_type'),
        'location': data.get('location'),
        'timestamp': datetime.datetime.now(),
        'status': 'pending',
        'community_id': 'Bahia Kino'
    }

    try:
        # 2. Guardar en la colección REQUESTS
        db.collection(REQUESTS_COLLECTION).add(request_data)

        return jsonify({
            'success': True,
            'message': 'Solicitud de transporte enviada con éxito.',
            'request_data': request_data
        })

    except Exception as e:
        print(f"Error al crear solicitud: {e}")
        return jsonify({'success': False, 'message': f'Error al crear solicitud: {e}'}), 500


# --- # --- 5. EJECUCIÓN SECUENCIAL (CRUCIAL) ---
if __name__ == '__main__':
    # Ejecuta el backend en el puerto 5000 (Render lo mapeará al puerto 80)
    # app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)
    pass # o simplemente dejarlo vacío
    

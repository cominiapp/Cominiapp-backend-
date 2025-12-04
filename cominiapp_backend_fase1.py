from flask import Flask, request, jsonify
from flask_cors import CORS
import requests # Módulo crucial para la API REST (Ya no es tan crucial, pero se mantiene)
import os
import uuid
from datetime import datetime
from google.cloud import firestore

# --- CONFIGURACIÓN DE FIRESTORE (NUEVA CONEXIÓN ESTABLE)
# El cliente de Firestore se autentica automáticamente con la clave GOOGLE_APPLICATION_CREDENTIALS
# que ya subiste a Render.

DRIVERS_COLLECTION = 'drivers'
REQUESTS_COLLECTION = 'requests'

# Inicializa el cliente de base de datos
db = firestore.Client()


# --- 1. Configuración de la Aplicación Flask ---
app = Flask(__name__)
# Habilita CORS para CodePen (CRUCIAL)
CORS(app)


# --- 2. Funciones de Acceso a Firestore (VÍA LIBRERÍA GOOGLE-CLOUD) ---

def get_firestore_posts():
    """Obtiene la colección de 'requests' (solicitudes) usando la librería de Firestore."""
    
    try:
        # Consulta todos los documentos en la colección REQUESTS
        docs = db.collection(REQUESTS_COLLECTION).stream()
        
        posts = []
        for doc in docs:
            # Convierte el documento de Firestore a un diccionario Python
            post = doc.to_dict()
            post['id'] = doc.id  # Añade el ID único del documento
            posts.append(post)
            
        return posts
    
    except Exception as e:
        print(f"Error al obtener datos de Firestore: {e}")
        return [] # Devuelve una lista vacía en caso de fallo

# --- 3. Endpoints Disponibles (Lógica de la Aplicación) ---

# Endpoint POST /driver/register (MODIFICADO para usar db.collection().set())
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
        'location': 'LatLongDefault',  # Se actualizará con la ubicación real
        'status': 'available',
        'community_id': 'Bahia Kino' # ID de la comunidad
    }
    
    try:
        # 3. Guardar en la colección 'drivers' de Firestore (LÓGICA NUEVA ESTABLE)
        db.collection(DRIVERS_COLLECTION).document(driver_id).set(driver_data)

        return jsonify({
            'success': True,
            'message': 'Usuario registrado y listo para la fase 2.',
            'user_id': driver_id,
            'community_id': 'Bahia Kino'
        })
    except Exception as e:
        # Manejo de error específico de Firestore/DB
        return jsonify({'success': False, 'message': f'Error al registrar conductor: {e}'}), 500


# Endpoint GET /feed/community_id (MODIFICADO para usar get_firestore_posts())
@app.route('/feed/<community_id>', methods=['GET'])
def get_feed(community_id):
    # La comunidad se puede usar para filtrar en Firestore en futuras fases
    
    try:
        # Llama a la nueva función de lectura estable de Firestore
        posts = get_firestore_posts()
        
        return jsonify({
            'success': True,
            'community_id': community_id,
            'posts': posts
        })
    except Exception as e:
        # Manejo de error general
        return jsonify({'success': False, 'message': f'Error interno del servidor al obtener feed: {e}'}), 500


# --- EJECUCIÓN SECUENCIAL (CRUCIAL) ---
if __name__ == '__main__':
    # Se ejecuta el backend en el puerto 5000
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)



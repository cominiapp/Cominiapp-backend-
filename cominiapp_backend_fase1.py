from flask import Flask, request, jsonify
from flask_cors import CORS
import requests # Módulo crucial para la API REST
import os
import uuid
from datetime import datetime

# --- CONFIGURACIÓN DE FIRESTORE REST API (TU PROYECTO) ---
from google.cloud import firestore

# Define los nombres de las colecciones que usaremos en Firestore
DRIVERS_COLLECTION = 'drivers'
REQUESTS_COLLECTION = 'requests'

# Inicializa el cliente. Se autentica automáticamente con la clave de Render.
db = firestore.Client()


from google.cloud import firestore

# Define los nombres de las colecciones que usaremos en Firestore
DRIVERS_COLLECTION = 'drivers'
REQUESTS_COLLECTION = 'requests'

# Inicializa el cliente. Se autentica automáticamente con la clave de Render.
db = firestore.Client()


# --- 1. Configuración de la Aplicación Flask ---
app = Flask(__name__)
CORS(app) # Habilita CORS para CodePen (CRUCIAL)

# --- 2. Funciones de Acceso a Firestore (VÍA REST) ---

def get_firestore_posts_rest():
    """Obtiene posts de la colección 'moto_data' usando la API REST."""
    # Ruta completa para leer la colección
    url = f"{BASE_API_URL}/moto_data"
    
    try:
        # Petición GET a Firebase
        response = requests.get(url)
        response.raise_for_status() # Lanza un error si el código HTTP no es 200
        
        data = response.json()
        posts = []
        
        if 'documents' in data:
            for doc in data['documents']:
                doc_id = doc['name'].split('/')[-1]
                fields = doc.get('fields', {})
                
                # Función auxiliar para extraer el valor (asumiendo que son StringValues)
                def get_field_value(field_name):
                    return fields.get(field_name, {}).get('stringValue', '')
                
                # Construimos el objeto del post
                post = {
                    'id': doc_id,
                    'author': get_field_value('author'), 
                    'community_tag': get_field_value('community_tag'), 
                    'content': get_field_value('content'), 
                    'timestamp': get_field_value('timestamp'),
                    'profile_pic': get_field_value('profile_pic') or 'https://picsum.photos/50/50?random=1'
                }
                posts.append(post)
        
        return posts
        
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con Firestore REST API: {e}")
        # Retorno de error en caso de fallo de conexión real
        return [
            {
                'id': 'error-rest',
                'author': 'Sistema - Falla de Firebase',
                'community_tag': 'CONEXIÓN FALLIDA',
                'content': f"No se pudo acceder a Firebase Project ID: {FIREBASE_PROJECT_ID}. Error: {e}",
                'timestamp': datetime.now().isoformat()
            }
        ]

# --- 3. Endpoints Disponibles ---

# Endpoint: POST /register
@app.route('/register', methods=['POST'])
def register():
    """Endpoint de registro (Simulado)."""
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400
    
    user_id = str(uuid.uuid4())
    
    return jsonify({
        'success': True,
        'message': 'Usuario registrado y listo para la Fase 2',
        'user_id': user_id,
        'community_id': 'Bahía Kino'
    })

# Endpoint: GET /feed/<community_id>
@app.route('/feed/<community_id>', methods=['GET'])
def get_feed(community_id):
    """Obtiene publicaciones del feed REAL de Firestore vía API REST."""
    try:
        posts = get_firestore_posts_rest()

        return jsonify({
            'success': True,
            'community_id': community_id,
            'posts': posts
        })
    except Exception as e:
        print(f"Error general al obtener feed: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor al obtener feed'}), 500

# --- 4. Ejecución del Servidor (CRUCIAL) ---
if __name__ == '__main__':
    print(f"\n--- CominiApp Backend Iniciado (FIREBASE REST MODE) ---")
    print(f"Conectando a Project ID: {FIREBASE_PROJECT_ID}")
    app.run(host='0.0.0.0', port=5000, debug=True)

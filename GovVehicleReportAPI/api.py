from flask import Flask, request, jsonify
import sqlite3
import random

app = Flask(__name__)

# inicializa la base de datos 
def init_db():
    conn = sqlite3.connect('fake_vehicles.db')  # Base de datos en archivo 
    cursor = conn.cursor()
    
 # tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            placa TEXT PRIMARY KEY,
            propietario_nombre TEXT,
            propietario_cedula TEXT,
            ubicacion_direccion TEXT,
            expediente TEXT
        )
    ''')
    
    # para denuncias 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT,
            denuncia TEXT,
            FOREIGN KEY (placa) REFERENCES vehicles (placa)
        )
    ''')
    
    # Datos falsos 
    fake_data = [
        {
            'placa': 'ABC123',
            'propietario': {'nombre': 'Juan Pérez', 'cedula': '0101234567'},
            'ubicacion': {'direccion': 'Av. Amazonas 123, Quito, Ecuador'},
            'expediente': 'EXP-001',
            'denuncias': ['Exceso de velocidad el 01/10/2025', 'Estacionamiento ilegal el 15/09/2025']
        },
        {
            'placa': 'DEF456',
            'propietario': {'nombre': 'María López', 'cedula': '0207654321'},
            'ubicacion': {'direccion': 'Calle 10 de Agosto 456, Guayaquil, Ecuador'},
            'expediente': 'EXP-002',
            'denuncias': ['Conducción imprudente el 05/10/2025']
        },
        {
            'placa': 'GHI789',
            'propietario': {'nombre': 'Carlos Ramírez', 'cedula': '0301122334'},
            'ubicacion': {'direccion': 'Vía a la Costa 789, Milagro, Ecuador'},
            'expediente': 'EXP-003',
            'denuncias': []  # sin denuncias
        },
        {
            'placa': 'JKL012',
            'propietario': {'nombre': 'Ana Gómez', 'cedula': '0409988776'},
            'ubicacion': {'direccion': 'Panamericana Norte Km 12, Cuenca, Ecuador'},
            'expediente': 'EXP-004',
            'denuncias': ['Falta de luces el 20/09/2025', 'No uso de cinturón el 10/10/2025']
        },
        {
            'placa': 'MNO345',
            'propietario': {'nombre': 'Pedro Sánchez', 'cedula': '0503344556'},
            'ubicacion': {'direccion': 'Av. de los Shyris 345, Ambato, Ecuador'},
            'expediente': 'EXP-005',
            'denuncias': ['Invasión de carril el 03/10/2025']
        }
    ] 
    # Insertar datos a una tabla vacía
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    if cursor.fetchone()[0] == 0:
        for data in fake_data:
            cursor.execute('''
                INSERT INTO vehicles (placa, propietario_nombre, propietario_cedula, ubicacion_direccion, expediente)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['placa'], data['propietario']['nombre'], data['propietario']['cedula'], data['ubicacion']['direccion'], data['expediente']))
            
            for denuncia in data['denuncias']:
                cursor.execute('''
                    INSERT INTO denuncias (placa, denuncia)
                    VALUES (?, ?)
                ''', (data['placa'], denuncia))
    
    conn.commit()
    conn.close()

init_db()

# Endpoint para consultar por placa
@app.route('/api/vehicle', methods=['GET'])
def get_vehicle():
    placa = request.args.get('placa')
    if not placa:
        return jsonify({'error': 'Parámetro "placa" requerido'}), 400
    
    conn = sqlite3.connect('fake_vehicles.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT propietario_nombre, propietario_cedula, ubicacion_direccion, expediente
        FROM vehicles WHERE placa = ?
    ''', (placa,))
    vehicle = cursor.fetchone()
    
    if not vehicle:
        conn.close()
        return jsonify({'found': False, 'message': 'Placa no encontrada'}), 404
    
    cursor.execute('''
        SELECT denuncia FROM denuncias WHERE placa = ?
    ''', (placa,))
    denuncias = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    response = {
        'placa': placa,
        'propietario': {
            'nombre': vehicle[0],
            'cedula': vehicle[1]
        },
        'ubicacion': {
            'direccion': vehicle[2]
        },
        'supuestas_denuncias': denuncias,
        'expediente': vehicle[3]
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
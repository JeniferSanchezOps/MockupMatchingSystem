import sqlite3
import threading
import time

class OrderMatchingSystem:
    def __init__(self, db_path="orders.db", interval=10):
        self.db_path = db_path
        self.interval = interval  # Intervalo en segundos para ejecutar el emparejamiento
        self.start_matcher()

    def connect_db(self):
        return sqlite3.connect(self.db_path)

    def ConsultarOrdenesdeVenta(self, identificador_activo):
        """Consulta órdenes de venta para un activo específico."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ordenes WHERE tipo='venta' AND activo_id=?", (identificador_activo,))
        ventas = cursor.fetchall()
        conn.close()
        return ventas

    def ConsultarOrdenesdeCompra(self, identificador_activo):
        """Consulta órdenes de compra para un activo específico."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ordenes WHERE tipo='compra' AND activo_id=?", (identificador_activo,))
        compras = cursor.fetchall()
        conn.close()
        return compras

    def Emparejamiento(self):
        """Proceso de emparejamiento entre órdenes de compra y venta."""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Obtener activos únicos con órdenes
        cursor.execute("SELECT DISTINCT activo_id FROM ordenes")
        activos = cursor.fetchall()

        for (activo_id,) in activos:
            ventas = self.ConsultarOrdenesdeVenta(activo_id)
            compras = self.ConsultarOrdenesdeCompra(activo_id)
            
            for compra in compras:
                for venta in ventas:
                    if self.evaluar_regla_de_activo(compra, venta):
                        self.registrar_match(compra, venta)

        conn.close()

    def evaluar_regla_de_activo(self, compra, venta):
        """Evalúa si una orden de compra y venta hacen match según las reglas del activo."""
        return compra[3] >= venta[3]  # Ejemplo: comparar precios (posición 3 en la tupla)

    def registrar_match(self, compra, venta):
        """Registra en la base de datos un emparejamiento exitoso."""
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO matches (compra_id, venta_id, activo_id) VALUES (?, ?, ?)", 
                       (compra[0], venta[0], compra[1]))
        conn.commit()
        conn.close()
        print(f"Match registrado: Compra {compra[0]} con Venta {venta[0]}")

    def start_matcher(self):
        """Inicia el temporizador para ejecutar el emparejamiento periódicamente."""
        def run():
            while True:
                print("Ejecutando emparejamiento...")
                self.Emparejamiento()
                time.sleep(self.interval)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

# Ejemplo de inicialización
if __name__ == "__main__":
    matching_system = OrderMatchingSystem(interval=30)

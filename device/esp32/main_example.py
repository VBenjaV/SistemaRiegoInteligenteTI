"""
Ejemplo de código para ESP32 con MicroPython

Este archivo contiene el código que debe ejecutarse en el microcontrolador ESP32
para leer sensores, publicar en MQTT y recibir comandos de control.

NOTA: Este es un ejemplo de referencia. El desarrollo completo del firmware
será realizado en la próxima fase del proyecto.
"""

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

CONFIG = {
    "WIFI_SSID": "nombre_red_wifi",
    "WIFI_PASSWORD": "contraseña_wifi",
    "MQTT_BROKER": "192.168.1.100",  # IP del servidor MQTT
    "MQTT_PORT": 1883,
    "MQTT_CLIENT_ID": "esp32_riego_1",
    "MQTT_USER": "",  # Opcional
    "MQTT_PASS": "",  # Opcional
    "TOPIC_PUBLISH_HUMEDAD": "jardin/sensor1/humedad",
    "TOPIC_PUBLISH_TEMP": "jardin/sensor1/temperatura",
    "TOPIC_SUBSCRIBE_COMMAND": "jardin/bomba/comando",
    "SENSOR_HUMEDAD_PIN": 32,  # GPIO 32 (ADC)
    "SENSOR_TEMP_PIN": 33,      # GPIO 33 (opcional)
    "RELAY_BOMBA_PIN": 25,      # GPIO 25 (salida digital)
    "LECTURA_INTERVALO_SEC": 300,  # 5 minutos
}


# ============================================================================
# IMPORTES Y SETUP
# ============================================================================

import json
import time
import machine
from machine import ADC, Pin
from micropython import const
try:
    import umqtt.simple as mqtt
except ImportError:
    # Si no está disponible, usar versión simple
    import mqtt

try:
    import network
except ImportError:
    pass


# ============================================================================
# CLASE SENSOR
# ============================================================================

class SensorHumedad:
    """Leer sensor de humedad del suelo"""
    
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  # Rango 0-3.3V
    
    def leer_raw(self):
        """Lectura raw del ADC"""
        return self.adc.read()
    
    def leer_humedad_porcentaje(self, calibracion_seco=4095, calibracion_mojado=1000):
        """
        Leer humedad como porcentaje
        
        Args:
            calibracion_seco: valor ADC cuando está seco (sin agua)
            calibracion_mojado: valor ADC cuando está mojado (en agua)
        
        Returns:
            Porcentaje de humedad (0-100%)
        """
        raw = self.leer_raw()
        
        # Invertir escala: cuando está seco, valor es alto, humedad baja
        # cuando está mojado, valor es bajo, humedad alta
        humedad = ((calibracion_seco - raw) / (calibracion_seco - calibracion_mojado)) * 100
        
        # Limitar entre 0 y 100
        humedad = max(0, min(100, humedad))
        
        return humedad


class Relé:
    """Controlar relé para bomba de agua"""
    
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT)
        self.pin.off()  # Apagado por defecto
    
    def encender(self):
        """Encender relé (activar riego)"""
        self.pin.on()
    
    def apagar(self):
        """Apagar relé (detener riego)"""
        self.pin.off()
    
    def esta_encendido(self):
        """Verificar estado del relé"""
        return self.pin.value() == 1


# ============================================================================
# CLASE WIFI
# ============================================================================

class WifiManager:
    """Gestionar conexión a Wi-Fi"""
    
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.conectado = False
    
    def conectar(self):
        """Conectar a Wi-Fi"""
        self.wlan.active(True)
        
        if not self.wlan.isconnected():
            print(f"[WiFi] Conectando a {self.ssid}...")
            self.wlan.connect(self.ssid, self.password)
            
            timeout = 20
            while not self.wlan.isconnected() and timeout > 0:
                time.sleep(0.5)
                timeout -= 1
        
        if self.wlan.isconnected():
            print(f"[WiFi] Conectado: {self.wlan.ifconfig()}")
            self.conectado = True
        else:
            print("[WiFi] Error de conexión")
            self.conectado = False
    
    def desconectar(self):
        """Desconectar de Wi-Fi"""
        self.wlan.disconnect()
        self.conectado = False


# ============================================================================
# CLASE MQTT
# ============================================================================

class MQTTClient:
    """Cliente MQTT para comunicación"""
    
    def __init__(self, broker, puerto, cliente_id, usuario=None, contraseña=None):
        self.broker = broker
        self.puerto = puerto
        self.cliente_id = cliente_id
        self.usuario = usuario
        self.contraseña = contraseña
        self.cliente = None
        self.conectado = False
    
    def conectar(self):
        """Conectar al broker MQTT"""
        try:
            self.cliente = mqtt.MQTTClient(
                self.cliente_id,
                self.broker,
                port=self.puerto
            )
            
            if self.usuario and self.contraseña:
                self.cliente.set_callback(self._callback)
            
            self.cliente.connect()
            print(f"[MQTT] Conectado a {self.broker}:{self.puerto}")
            self.conectado = True
            return True
        except Exception as e:
            print(f"[MQTT] Error de conexión: {e}")
            self.conectado = False
            return False
    
    def suscribir(self, tema):
        """Suscribirse a un tema"""
        try:
            self.cliente.subscribe(tema)
            print(f"[MQTT] Suscrito a: {tema}")
        except Exception as e:
            print(f"[MQTT] Error en suscripción: {e}")
    
    def publicar(self, tema, payload):
        """Publicar un mensaje"""
        try:
            self.cliente.publish(tema, payload)
            print(f"[MQTT] Publicado en {tema}: {payload}")
        except Exception as e:
            print(f"[MQTT] Error en publicación: {e}")
    
    def esperar_mensajes(self, timeout_ms=1000):
        """Esperar y procesar mensajes"""
        try:
            self.cliente.check_msg()
        except Exception as e:
            print(f"[MQTT] Error recibiendo mensajes: {e}")
    
    def desconectar(self):
        """Desconectar del broker"""
        try:
            self.cliente.disconnect()
            self.conectado = False
            print("[MQTT] Desconectado")
        except Exception as e:
            print(f"[MQTT] Error al desconectar: {e}")
    
    def _callback(self, topic, msg):
        """Callback para mensajes recibidos"""
        print(f"[MQTT] Mensaje recibido en {topic}: {msg}")


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class SistemaRiego:
    """Sistema completo de riego"""
    
    def __init__(self, config):
        self.config = config
        self.sensor = SensorHumedad(config["SENSOR_HUMEDAD_PIN"])
        self.rele = Relé(config["RELAY_BOMBA_PIN"])
        self.wifi = WifiManager(config["WIFI_SSID"], config["WIFI_PASSWORD"])
        self.mqtt = MQTTClient(
            config["MQTT_BROKER"],
            config["MQTT_PORT"],
            config["MQTT_CLIENT_ID"],
            config["MQTT_USER"],
            config["MQTT_PASS"]
        )
        self.riego_activo = False
        self.tiempo_fin_riego = 0
    
    def inicializar(self):
        """Inicializar el sistema"""
        print("[Sistema] Inicializando...")
        
        # Conectar Wi-Fi
        self.wifi.conectar()
        
        # Conectar MQTT
        if self.wifi.conectado:
            time.sleep(1)
            self.mqtt.conectar()
            
            if self.mqtt.conectado:
                self.mqtt.suscribir(self.config["TOPIC_SUBSCRIBE_COMMAND"])
    
    def leer_sensores(self):
        """Leer sensores"""
        humedad = self.sensor.leer_humedad_porcentaje()
        return humedad
    
    def enviar_datos(self, humedad):
        """Enviar datos a MQTT"""
        if not self.mqtt.conectado:
            return
        
        timestamp = self._get_timestamp()
        
        payload = json.dumps({
            "humedad": humedad,
            "timestamp": timestamp
        })
        
        self.mqtt.publicar(self.config["TOPIC_PUBLISH_HUMEDAD"], payload)
    
    def procesar_comando(self, tema, mensaje):
        """Procesar comando recibido"""
        if tema == self.config["TOPIC_SUBSCRIBE_COMMAND"]:
            try:
                comando = json.loads(mensaje)
                accion = comando.get("accion", "OFF")
                duracion = comando.get("duracion_segundos", 300)
                
                if accion == "ON":
                    self.encender_riego(duracion)
                elif accion == "OFF":
                    self.apagar_riego()
            except Exception as e:
                print(f"[Sistema] Error procesando comando: {e}")
    
    def encender_riego(self, duracion_segundos=300):
        """Encender riego"""
        self.rele.encender()
        self.riego_activo = True
        self.tiempo_fin_riego = time.time() + duracion_segundos
        print(f"[Riego] Encendido por {duracion_segundos} segundos")
    
    def apagar_riego(self):
        """Apagar riego"""
        self.rele.apagar()
        self.riego_activo = False
        print("[Riego] Apagado")
    
    def verificar_riego_activo(self):
        """Verificar si riego debe seguir activo"""
        if self.riego_activo and time.time() > self.tiempo_fin_riego:
            self.apagar_riego()
    
    def _get_timestamp(self):
        """Obtener timestamp en formato ISO"""
        # Nota: ESP32 necesita sincronización NTP
        import utime
        t = utime.localtime()
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
        )
    
    def loop(self):
        """Loop principal"""
        ultimo_envio = 0
        intervalo = self.config["LECTURA_INTERVALO_SEC"]
        
        while True:
            ahora = time.time()
            
            # Leer sensores cada X segundos
            if ahora - ultimo_envio >= intervalo:
                humedad = self.leer_sensores()
                print(f"[Sensor] Humedad: {humedad:.1f}%")
                
                self.enviar_datos(humedad)
                ultimo_envio = ahora
            
            # Verificar si riego debe apagarse
            self.verificar_riego_activo()
            
            # Procesar mensajes MQTT
            if self.mqtt.conectado:
                self.mqtt.esperar_mensajes(timeout_ms=100)
            
            time.sleep(0.1)


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    print("[Sistema] Iniciando Sistema de Riego Inteligente")
    
    sistema = SistemaRiego(CONFIG)
    sistema.inicializar()
    
    print("[Sistema] Entrando en loop principal...")
    try:
        sistema.loop()
    except KeyboardInterrupt:
        print("\n[Sistema] Interrumpido por usuario")
        sistema.mqtt.desconectar()
        sistema.rele.apagar()

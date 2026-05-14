# Documentación del Dispositivo ESP32

## Instalación del Firmware MicroPython

### 1. Descargar herramientas necesarias

```bash
# Instalar esptool
pip install esptool

# Descargar firmware MicroPython
# Ir a: https://micropython.org/download/esp32/
# Descargar la última versión (.bin)
```

### 2. Flashear firmware

```bash
# Borrar flash
esptool.py --port COM3 erase_flash

# Escribir firmware
esptool.py --port COM3 --baud 460800 write_flash -z 0x1000 esp32-YYYYMMDD-vX.X.X.bin
```

## Componentes Requeridos

- **Microcontrolador**: ESP32 (DevKit o similar)
- **Sensor de Humedad**: Capacitivo (ej. DFRobot SEN0193)
- **Relé**: Módulo de relé de 5V (para controlar electroválvula)
- **Electroválvula**: 12V DC o 24V (según disponibilidad)
- **Bomba de agua**: Submersible (opcional)
- **Power supply**: 5V para ESP32 y 12/24V para válvula

## Esquema de Conexión

```
ESP32
├─ GPIO 32 (ADC0) ──→ Sensor Humedad (salida analógica)
├─ GPIO 33 (ADC1) ──→ Sensor Temperatura (opcional)
├─ GPIO 25 (OUT)  ──→ Relé Módulo (IN pin)
├─ GND            ──→ GND común
└─ 3.3V           ──→ VCC sensor

Relé
├─ IN  ← GPIO 25
├─ GND ← ESP32 GND
├─ VCC ← 5V
├─ NO  → 12V Electroválvula
└─ GND → 12V GND
```

## Configuración WiFi y MQTT

Editar `CONFIG` en `main_example.py`:

```python
CONFIG = {
    "WIFI_SSID": "tu_red_wifi",
    "WIFI_PASSWORD": "tu_contraseña",
    "MQTT_BROKER": "192.168.1.100",  # IP del PC con Mosquitto
    "MQTT_PORT": 1883,
    ...
}
```

## Instalación de librerías

### Opción 1: Usando Thonny IDE

1. Abrir Thonny (https://thonny.org/)
2. Tools → Manage packages
3. Instalar: `micropython-umqtt.simple`

### Opción 2: Manualmente

```bash
# Conectar ESP32 por USB

# Subir librería MQTT
ampy -p COM3 put umqtt/simple.py umqtt/simple.py

# Subir main.py
ampy -p COM3 put device/esp32/main_example.py main.py
```

## Ejecutar el firmware

```bash
# Opción 1: Usar Thonny
# - Conectar ESP32
# - Abrir device/esp32/main_example.py
# - Run script

# Opción 2: Copiar a ESP32
ampy -p COM3 put device/esp32/main_example.py main.py
# Reiniciar ESP32 - ejecutará automáticamente main.py
```

## Testing Manual

### Verificar conexión WiFi

```python
import network
sta_if = network.WLAN(network.STA_IF)
print(sta_if.ifconfig())  # Debe mostrar IP
```

### Verificar conexión MQTT

```python
import umqtt.simple as mqtt
c = mqtt.MQTTClient("test", "192.168.1.100")
c.connect()
c.publish(b"test/topic", b"hello")
```

### Leer sensor

```python
from machine import ADC, Pin
adc = ADC(Pin(32))
adc.atten(ADC.ATTN_11DB)
print(adc.read())  # Valor entre 0-4095
```

## Troubleshooting

### ESP32 no se conecta al WiFi
- Verificar SSID y contraseña
- Revisar que el router esté a 2.4GHz (ESP32 no soporta 5GHz)
- Revisar logs en serial monitor

### MQTT no conecta
- Verificar IP del broker
- Ping al broker: `ping 192.168.1.100`
- Verificar puerto 1883 está abierto

### Sensor no lee correctamente
- Calibrar valores: `calibracion_seco` y `calibracion_mojado`
- Verificar conexión GPIO
- Probar con potencial en tierra

## Calib ración del Sensor

```python
# 1. Sensor al aire (seco)
sensor = SensorHumedad(32)
print(sensor.leer_raw())  # Anotar valor (ej: 4095)

# 2. Sensor en agua
print(sensor.leer_raw())  # Anotar valor (ej: 1000)

# 3. Usar estos valores en calibracion_seco y calibracion_mojado
```

## Monitoreo Serial

```bash
# Con screen (Linux/Mac)
screen /dev/ttyUSB0 115200

# Con PuTTY (Windows)
# - Seleccionar puerto (COM3, COM4, etc.)
# - Speed: 115200
# - Connection type: Serial
```

## Próximas Mejoras

- [ ] OTA (Over-The-Air) updates
- [ ] Almacenamiento en memoria Flash
- [ ] Sincronización NTP para hora exacta
- [ ] Bajo consumo de energía (deep sleep)
- [ ] Watchdog timer
- [ ] Recuperación de errores automática

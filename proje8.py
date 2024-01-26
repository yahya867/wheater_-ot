from machine import Pin, UART, ADC,I2C
import time
from time import sleep
import dht
from bmp280 import BMP280


WiFi_SSID = 'note10'
WiFi_password = '12341234'
TCP_ServerIP = "api.thingspeak.com"
Port = 80
API_KEY = 'your api key'
uart = UART(0, 115200)
sensor = dht.DHT11(Pin(3))
soil = ADC(Pin(27))
Raindrop_AO = ADC(4)
i2c = I2C(0, sda=Pin(16), scl=Pin(17))
bmp = BMP280(i2c)
def send_data(temperature, hum, pressure, moist, yagmur):
    data_thingspeak = "GET /update?key=" + API_KEY + "&field1=%s&field2=%s&field3=%s&field4=%s&field5=%s" % (
        temperature, hum, pressure, moist, yagmur) + "\r\n"

  

    sendAT("AT+CIPSTART=\"TCP\",\"" + TCP_ServerIP + "\"," + str(Port), "OK", 5000)
    sendAT("AT+CIPSEND=" + str(len(data_thingspeak)) + '\r\n', "OK")
    sleep(0.5)
    uart.write(data_thingspeak)
    print("Sending to ThingSpeak:", data_thingspeak)
    sendAT('AT+CIPCLOSE' + '\r\n', "OK")



def sendAT(cmd, ack, timeout=2000):
    uart.write(cmd + '\r\n')
    t = time.ticks_ms()
    while (time.ticks_ms() - t) < timeout:
        s = uart.read()
        if s is not None:
            time.sleep_us(10)
            s = s.decode("utf-8")
            print(s)
            if s.find(ack) >= 0:
                return True
def pressure_temperature():
    pressure = bmp.pressure / 100  
    temperature = bmp.temperature  
    return pressure, temperature

def humidity():
    sleep(2)
    sensor.measure()
    deneme = 0
    while sensor.humidity() is None:
        deneme += 1
        if deneme > 5:
            print("DHT11 ölçümünde hata oluştu.")
            return None, None
        sleep(3)  
        sensor.measure()
    
    hum = sensor.humidity()
    return hum

def nem_algilama():

    moisture = (soil.read_u16()) * 100 / 65535

    sleep(2)  
    return moisture

def rain_drop():

    adc_Raindrop = (Raindrop_AO.read_u16()) * 100 / 65535
    return adc_Raindrop

sleep(2)
sendAT("AT", "OK")
sendAT("AT+CWMODE=1", "OK")
sendAT("AT+CWJAP=\"" + WiFi_SSID + "\",\"" + WiFi_password + "\"", "OK", 20000)
sendAT("AT+CIPMUX=0", "OK")
sendAT("AT+CIPSTART=\"TCP\",\"" + TCP_ServerIP + "\"," + str(Port), "OK", 5000)

while True:
    hum = humidity()
    if hum is not None:
        moist = nem_algilama()
        sleep(3)
        pressure, temperature = pressure_temperature()  # Get BMP sensor data

        yagmur = rain_drop()
        send_data(temperature,hum,pressure,moist, yagmur)
    sleep(5)


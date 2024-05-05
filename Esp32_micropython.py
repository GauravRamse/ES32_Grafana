import network
import time
import urequests

import ujson
from machine import Pin, ADC
import time


def scale_value(x, x_min, x_max, y_min, y_max):
    # Normalize input value
    x_normalized = (x - x_min) / (x_max - x_min)
    
    # Invert the normalized value
    inverted_normalized = 1 - x_normalized
    
    # Scale inverted normalized value to target range
    y = y_min + inverted_normalized * (y_max - y_min)
    
    # Ensure y is within [0, 100] range
    if y < 0:
        y = 0
    elif y > 100:
        y = 100
    
    return y





# Function to connect to Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)  # Create a station interface object
    wlan.active(True)  # Activate the station interface
    
    # Connect to Wi-Fi network
    wlan.connect(ssid, password)
    
    # Wait for connection to be established
    while not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        time.sleep(1)
    
    # Print connection details
    print("Wi-Fi connected successfully")
    print("IP address:", wlan.ifconfig()[0])
    
    return True

## Wi-Fi credentials
# wifi_ssid = "HACKUPC2024B"
# wifi_password = "Biene2024!"

wifi_ssid = "wifi name"
wifi_password = "wifi password"


import dht
import machine


# Connect to Wi-Fi
if connect_to_wifi(wifi_ssid, wifi_password):
    
    # Define the URL you want to request
    # url = "http://192.168.202.182:8000/get_data/"
    
    url = "http://192.168.142.182:8000/post_data/"
    
    #url = "https://google.com"


    dht_pin_number = 10
    # Main loop
    for _ in range(50000):  # Read and print temperature 10 times

        d = dht.DHT11(machine.Pin(dht_pin_number))
        d.measure()
        temperature = d.temperature()
        humidity = d.humidity()
                  
               
        # Define the ADC pin number where your analog temperature sensor is connected
        adc_pin_num = 32  # Change this to the GPIO pin number your sensor is connected to

        # Create an ADC object
        ldr = Pin(adc_pin_num, mode=Pin.IN)
        ldr_value = ldr.value()
                  
  
  
          # Define the ADC pin number where your analog temperature sensor is connected
        photo_pin_num = 33  # Change this to the GPIO pin number your sensor is connected to

        # Create an ADC object
        photoresistor = ADC(Pin(photo_pin_num, mode=Pin.IN))
        photoresistor.atten(ADC.ATTN_11DB)

        photoresistor_value = photoresistor.read()
        # Data to be sent in the POST request
        data = {"temperature": temperature,
                "humidity": humidity,
                "ldr":"OFF" if ldr_value else "ON",
                "photoresistor": scale_value( photoresistor_value , 2200, 4200, 0, 100)}
        
        print(data)

        # Send the POST request with data
        response = urequests.post(url, json=data)

        # Close the response
        response.close()
        
        
          # Delay before next reading
        time.sleep(1)  # Adjust delay as needed


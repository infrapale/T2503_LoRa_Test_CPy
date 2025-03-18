# Example to send a packet periodically between addressed nodes
# Author: Jerry Needell
#
#  https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/advanced-circuitpython-library-usage-2
#

import time
import board
import busio
import digitalio
import adafruit_rfm9x
import neopixel


uart = busio.UART(board.TX, board.RX, baudrate=9600)
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.3

# Define radio parameters.
RADIO_FREQ_MHZ =868.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip.
CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D11)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# enable CRC checking
rfm9x.enable_crc = True
# set node addresses
rfm9x.node = 2
rfm9x.destination = 1
# initialize counter
counter = 0
# send a broadcast message from my_node with ID = counter
rfm9x.send(bytes("startup message from node {} ".format(rfm9x.node), "UTF-8"))

# Wait to receive packets.
print("Waiting for packets...")
# initialize flag and timer
time_now = time.monotonic()
pixel.fill((255, 0, 0))
while True:
    # Look for a new packet: only accept if addresses to my_node
    packet = rfm9x.receive(with_header=True)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        pixel.fill((0, 255, 0))
        # Received a packet!
        # Print out the raw bytes of the packet:
        str = "Received (raw header): " 
        uart.write(str)
        print(str)
        str = [hex(x) for x in packet[0:4]]
        uart.write("{}\n".format(str))
        print(str)
        str = "{0} {1} \n".format("Received (raw payload):", packet[4:])
        uart.write(str)
        print(str)
        str = "Received RSSI: {0} \n".format(rfm9x.last_rssi)
        uart.write(str)
        print(str)
        # send reading after any packet received
        counter = counter + 1
        # after 10 messages send a response to destination_node from my_node with ID = counter&0xff
        if counter % 10 == 0:
            pixel.fill((255, 128, 0))
            time.sleep(0.5)  # brief delay before responding
            rfm9x.identifier = counter & 0xFF
            rfm9x.send(
                bytes(
                    "message number {} from node {} ".format(counter, rfm9x.node),
                    "UTF-8",
                ),
                keep_listening=True,
            )
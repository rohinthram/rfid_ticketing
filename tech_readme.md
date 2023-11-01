# Technical Hints on the project

## Code on ESP32
- Interfacing RFID reader (RC522) using SPI protocol
- Interfacing LCD using I2C protocol (mainly because it makes interfacing easier and reduces the number of GPIO required)
- Use HTTP request to send and receive data (from autheticating user to getting fare etc.,)

## Python Code
- Uses Flask framework
- Uses gmail API to send forgot password mail
- Has all required API end points required by the mircocontrolller
- the files has some changes made to host in pythonanywhere, so some changes are required make it working elsewhere, even locally 
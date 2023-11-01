// By Rohinth Ram R V and Siva Chokkalingam S

// RFID Reader 
#include <SPI.h>
#include <MFRC522.h>
// Servo Motor
#include<ESP32Servo.h>
// LCD with I2C
#include<Wire.h>
#include<LiquidCrystal_I2C.h>
// Wifi
#include<WiFi.h>
#include<HTTPClient.h>
//for json payload
#include <ArduinoJson.h>

#define SS_PIN 25
#define RST_PIN 26

#define MISO_PIN  19 
#define MOSI_PIN  23 
#define SCK_PIN   18 

LiquidCrystal_I2C lcd(0x27, 16,2);

MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class
MFRC522::MIFARE_Key key; 

Servo Gate;

void setup() { 
  Serial.begin(9600);
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522
  rfid.PCD_DumpVersionToSerial();   // Show details of PCD - MFRC522 Card Reader details
  //Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
 
  lcd.init();   
  lcd.backlight(); 
  lcd.setCursor(0,0);

  Gate.attach(14);
  Gate.write(0);

  connectWiFi();
}

String domain = "http://ticketing.pythonanywhere.com";
const char* ssid = "ssid";
const char* password = "pswd";
  
void loop() {
  while(!(WiFi.status() == WL_CONNECTED))
  {
    connectWiFi();
  }
  
  lcd.setCursor(0,0);
  lcd.print("Show your ID");

  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if ( ! rfid.PICC_IsNewCardPresent())
    return ;

  // Verify if the NUID has been readed
  if ( ! rfid.PICC_ReadCardSerial())
    return;

  Serial.print("UID Tag : ");

  String tag= "";
  byte letter;
  for (byte i = 0; i < rfid.uid.size; i++){  
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : "");  
    Serial.print(rfid.uid.uidByte[i], HEX);  
    tag.concat(String(rfid.uid.uidByte[i] < 0x10 ? "0" : ""));  
    tag.concat(String(rfid.uid.uidByte[i], HEX));  
  }
  
  tag.toUpperCase(); 
  
  Serial.println(F("Card read successfully"));
  printHex(rfid.uid.uidByte, rfid.uid.size);
  Serial.println(F("Please Wait"));
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Please Wait ...");

  String ret = check(tag);
  if(ret == "-1"){
    lcd.clear();
    lcd.setCursor(0,0); 
    lcd.print("Invalid Access");
    delay(2000);
    lcd.clear();
    return;
  }
  else if(ret == "0"){
    lcd.clear();
    lcd.setCursor(0,0); 
    lcd.print("Invalid ID");
    lcd.setCursor(0,1);
    lcd.print(tag);
    delay(2000);
    lcd.clear();
    return;
  }
  else if(ret[0] == '1'){
    lcd.clear();
    lcd.setCursor(0,0); 
    lcd.print("Welcome (^^)");
    lcd.setCursor(0,1);
    lcd.print(ret.substring(1));
    Gate.write(90);
    delay(5000);
    lcd.clear();
    Gate.write(0);
  }
  else if(ret[0] == '2'){
    lcd.clear();
    lcd.setCursor(0,0); 
    lcd.print("Thank You!");
    lcd.setCursor(0,1);
    lcd.print(ret.substring(1));
    Gate.write(90);
    delay(3000);
    lcd.clear();
    Gate.write(0);
  }

  // Halt PICC
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
}

void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}

void connectWiFi()
{
  int i = 0;
  Serial.println("Connecting to WiFi...");
  lcd.clear();
  lcd.setCursor(0,0); 
  lcd.print("Connecting...");
  
  WiFi.begin(ssid, password);

  while(!(WiFi.status() == WL_CONNECTED))
  {
    Serial.println(" - ");
    i++;
    delay(300);
    if(i > 10)
      connectWiFi();

    Serial.println("\n... WiFi Connected");
    lcd.clear();
    lcd.setCursor(0,0); 
    lcd.print("Connected...");
    delay(1000);
    lcd.clear();
  }
}

String check(String tag_id){
  HTTPClient http;

  http.begin(domain+"/update");
  http.addHeader("Content-Type", "text/plain");
  
  int httpResponseCode = http.POST("{\"tag_id\":\"" + tag_id +"\",\"key\":\"123\", \"bus_id\":\"1\"}");
  Serial.println(httpResponseCode);
  if(httpResponseCode > 0){
    String response = http.getString();
    Serial.println(response);
    return response;
  }
  return "-1";
}

#include <Adafruit_GPS.h>

int analogPin = A7;
SoftwareSerial mySerial(6, 5);
//SoftwareSerial ss(6, 5);
Adafruit_GPS GPS(&mySerial);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  GPS.begin(38400);
  //These lines configure the GPS Module
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA); //Sets output to only RMC and GGA sentences
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); //Sets the output to 1/second. If you want you can go higher/lower
  GPS.sendCommand(PGCMD_ANTENNA); //Can report if antenna is connected or not
}

void loop() {
  // put your main code here, to run repeatedly:
  int val = analogRead(analogPin);
  float voltage = val * (5.0 / 1023.0);

  //Now we will start our GPS module, parse (break into parts) the Last NMEA sentence
  GPS.parse(GPS.lastNMEA()); //This is going to parse the last NMEA sentence the Arduino has received, breaking it down into its constituent parts.
  GPS.newNMEAreceived(); //This will return a boolean TRUE/FALSE depending on the case.
//  Serial.write(ss.read());
  if (voltage < 0.01) {
    //Print the current date/time/etc
    Serial.print("\nTime: ");
    Serial.print(GPS.hour, DEC); Serial.print(':');
    Serial.print(GPS.minute, DEC); Serial.print(':');
    Serial.print(GPS.seconds, DEC); Serial.print('.');
    Serial.println(GPS.milliseconds);
    Serial.print("Date: ");
    Serial.print(GPS.day, DEC); Serial.print('/');
    Serial.print(GPS.month, DEC); Serial.print("/20");
    Serial.println(GPS.year, DEC);
    Serial.print("Fix: "); Serial.print((int)GPS.fix);
    Serial.print(" quality: "); Serial.println((int)GPS.fixquality);

    Serial.println("Triggered");
    Serial.println(voltage);
  }
  delay(1);
}

//void loop() {
//    while (ss.available() > 0){
//    Serial.write(ss.read());
//  }
//}

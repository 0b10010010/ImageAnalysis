/*
author: Alex Kim
Base code from iforce2d UBX_GPS_NAV examples 

This script will read incoming GPS data and bridge information to onboard computer via Serial print
using FTDI USB to serial converter.
*/

#include <SoftwareSerial.h>

const long USB_BAUD_RATE = 115200;
const long GPS_BAUD_RATE = 115200;

const byte interruptPin = 3;

unsigned short imageIndex = 0;

// Connect the GPS RX/TX to arduino pins 3 and 5
SoftwareSerial serial = SoftwareSerial(10, 9);

const unsigned char UBX_HEADER[]         = { 0xB5, 0x62 };
const unsigned char NAV_DOP_HEADER[]     = { 0x01, 0x04 };
const unsigned char NAV_PVT_HEADER[]     = { 0x01, 0x07 };
const unsigned char NAV_TIMEGPS_HEADER[] = { 0x01, 0x20 };

enum _ubxMsgType {
  MT_NONE,
  MT_NAV_DOP,
  MT_NAV_PVT,
  MT_NAV_TIMEGPS
};

struct NAV_DOP {
  unsigned char cls;
  unsigned char id;
  unsigned short len;
  unsigned long iTOW;          // GPS time of week of the navigation epoch (ms)

  unsigned short gDOP;         // Geometric DOP
  unsigned short pDOP;         // Position DOP
  unsigned short tDOP;         // Time DOP
  unsigned short vDOP;         // Vertical DOP
  unsigned short hDOP;         // Horizontal DOP
  unsigned short nDOP;         // Northing DOP
  unsigned short eDOP;         // Easting DOP
};

struct NAV_PVT {
  unsigned char cls;
  unsigned char id;
  unsigned short len;
  unsigned long iTOW;          // GPS time of week of the navigation epoch (ms)

  unsigned short year;         // Year (UTC)
  unsigned char month;         // Month, range 1..12 (UTC)
  unsigned char day;           // Day of month, range 1..31 (UTC)
  unsigned char hour;          // Hour of day, range 0..23 (UTC)
  unsigned char minute;        // Minute of hour, range 0..59 (UTC)
  unsigned char second;        // Seconds of minute, range 0..60 (UTC)
  char valid;                  // Validity Flags (see graphic below)
  unsigned long tAcc;          // Time accuracy estimate (UTC) (ns)
  long nano;                   // Fraction of second, range -1e9 .. 1e9 (UTC) (ns)
  unsigned char fixType;       // GNSSfix Type, range 0..5
  char flags;                  // Fix Status Flags
  char flags2;                 // Additional Flags
  unsigned char numSV;         // Number of satellites used in Nav Solution

  long lon;                    // Longitude (deg)
  long lat;                    // Latitude (deg)
  long height;                 // Height above Ellipsoid (mm)
  long hMSL;                   // Height above mean sea level (mm)
  unsigned long hAcc;          // Horizontal Accuracy Estimate (mm)
  unsigned long vAcc;          // Vertical Accuracy Estimate (mm)

  long velN;                   // NED north velocity (mm/s)
  long velE;                   // NED east velocity (mm/s)
  long velD;                   // NED down velocity (mm/s)
  long gSpeed;                 // Ground Speed (2-D) (mm/s)
  long heading;                // Heading of motion 2-D (deg)
  unsigned long sAcc;          // Speed Accuracy Estimate
  unsigned long headingAcc;    // Heading Accuracy Estimate
  unsigned short pDOP;         // Position dilution of precision

  char reserved[6];           // Reserved
  long headVeh;                // Heading of Vehicle (2-D)
  short magDec;                // Magnetic Declination
  unsigned short magAcc;       // Magnetic Declination Accuracy
};

struct NAV_TIMEGPS {
  unsigned char cls;
  unsigned char id;
  unsigned short len;
  unsigned long iTOW;          // GPS time of week of the navigation epoch (ms)

  long fTOW;                   // Fractional part of iTOW (range: +/- 500000)
  short week;                  // GPS week number of the navigation epoch
  char leapS;                  // GPS leap seconds (GPS-UTC)
  char valid;                  // Validity Flags (see graphic below)
  unsigned long tAcc;          // Time Accuracy Estimate
};

union UBXMessage {
  NAV_DOP dop;
  NAV_PVT pvt;
  NAV_TIMEGPS t_gps;
};

UBXMessage ubxMessage;
UBXMessage tempUbxMessage;

// Compares the first two bytes of the ubxMessage struct with a specific message header.
// Returns true if the two bytes match.
boolean compareMsgHeader(const unsigned char* msgHeader) {
  unsigned char* ptr = (unsigned char*)(&tempUbxMessage);
  return ptr[0] == msgHeader[0] && ptr[1] == msgHeader[1];
}

// Reads in bytes from the GPS module and checks to see if a valid message has been constructed.
// Returns the type of the message found if successful, or MT_NONE if no message was found.
// After a successful return the contents of the ubxMessage union will be valid, for the
// message type that was found. Note that further calls to this function can invalidate the
// message content, so you must use the obtained values before calling this function again.
int readGPS() {
  static int fpos = 0;
  static unsigned char checksum[2];
  static byte currentMsgType = MT_NONE;
  static int payloadSize = sizeof(UBXMessage);

  while ( serial.available() ) {
    byte c = serial.read();

    if ( fpos < 2 ) {
      // For the first two bytes we are simply looking for a match with the UBX header bytes (0xB5,0x62)
      if ( c == UBX_HEADER[fpos] )
        fpos++;
      else
        fpos = 0; // Reset to beginning state.
    }
    else {
      // If we come here then fpos >= 2, which means we have found a match with the UBX_HEADER
      // and we are now reading in the bytes that make up the payload.

      // Place the incoming byte into the ubxMessage struct. The position is fpos-2 because
      // the struct does not include the initial two-byte header (UBX_HEADER).
      if ( (fpos - 2) < payloadSize )
        ((unsigned char*)(&tempUbxMessage))[fpos - 2] = c;

      fpos++;

      if ( fpos == 4 ) {
        // We have just received the second byte of the message type header,
        // so now we can check to see what kind of message it is.
        //        if ( compareMsgHeader(NAV_DOP_HEADER) ) {
        //          currentMsgType = MT_NAV_DOP;
        //          payloadSize = sizeof(NAV_DOP);
        //        }
        if ( compareMsgHeader(NAV_PVT_HEADER) ) {
          currentMsgType = MT_NAV_PVT;
          payloadSize = sizeof(NAV_PVT);
        }
        //        else if ( compareMsgHeader(NAV_TIMEGPS_HEADER) ) {
        //          currentMsgType = MT_NAV_TIMEGPS;
        //          payloadSize = sizeof(NAV_TIMEGPS);
        //        }
        else {
          // unknown message type, bail
          fpos = 0;
          continue;
        }
      }

      if ( fpos == (payloadSize + 2) ) {
        // All payload bytes have now been received, so we can calculate the
        // expected checksum value to compare with the next two incoming bytes.
        calcChecksum(checksum, payloadSize);
      }
      else if ( fpos == (payloadSize + 3) ) {
        // First byte after the payload, ie. first byte of the checksum.
        // Does it match the first byte of the checksum we calculated?
        if ( c != checksum[0] ) {
          // Checksum doesn't match, reset to beginning state and try again.
          fpos = 0;
        }
      }
      else if ( fpos == (payloadSize + 4) ) {
        // Second byte after the payload, ie. second byte of the checksum.
        // Does it match the second byte of the checksum we calculated?
        fpos = 0; // We will reset the state regardless of whether the checksum matches.
        if ( c == checksum[1] ) {
          // Checksum matches, we have a valid message.
		  memcpy(ubxMessage, tempUbxMessage, sizeof(tempUbxMessage));
          return currentMsgType;
        }
      }
      else if ( fpos > (payloadSize + 4) ) {
        // We have now read more bytes than both the expected payload and checksum
        // together, so something went wrong. Reset to beginning state and try again.
        fpos = 0;
      }
    }
  }
  return MT_NONE;
}

// The last two bytes of the message is a checksum value, used to confirm that the received payload is valid.
// The procedure used to calculate this is given as pseudo-code in the uBlox manual.
void calcChecksum(unsigned char* CK, int msgSize) {
  memset(CK, 0, 2);
  for (int i = 0; i < msgSize; i++) {
    CK[0] += ((unsigned char*)(&tempUbxMessage))[i];
    CK[1] += CK[0];
  }
  // ensure unsigned byte range
  CK[0] = CK[0] & 0xFF;
  CK[1] = CK[1] & 0xFF;
}

void setup() {
  Serial.begin(USB_BAUD_RATE);
  serial.begin(GPS_BAUD_RATE);
  pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), sendGPS, RISING);
}

void loop() {
  readGPS(); // loop through incoming serial data and parse GPS messages
}

void sendGPS() {
  imageIndex++;
  Serial.print("imageIndex: "); Serial.print(imageIndex);
//  Serial.print(" #SV: ");      Serial.print(ubxMessage.pvt.numSV);
//  Serial.print(" fixType: "); Serial.print(ubxMessage.pvt.fixType);
  Serial.print(" Date:");     Serial.print(ubxMessage.pvt.year); Serial.print("/"); Serial.print(ubxMessage.pvt.month); Serial.print("/"); Serial.print(ubxMessage.pvt.day); Serial.print(" "); Serial.print(ubxMessage.pvt.hour); Serial.print(":"); Serial.print(ubxMessage.pvt.minute); Serial.print(":"); Serial.print(ubxMessage.pvt.second); Serial.print(":"); Serial.print(ubxMessage.pvt.nano);
  Serial.print(" lat/lon: "); Serial.print(ubxMessage.pvt.lat / 10000000.0f,7); Serial.print(","); Serial.print(ubxMessage.pvt.lon / 10000000.0f,7);
//  Serial.print(" gSpeed: ");  Serial.print(ubxMessage.pvt.gSpeed / 1000.0f);
//  Serial.print(" heading: "); Serial.print(ubxMessage.pvt.heading / 100000.0f);
//  Serial.print(" hAcc: ");    Serial.print(ubxMessage.pvt.hAcc / 1000.0f);
  Serial.println();
}

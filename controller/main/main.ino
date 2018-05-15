/*
 * QRGX Microcontroller for 2018 SEDS. This is the main file.
 * 
 * Author(s): Viraj Bangari
 * 
 * Date: May 2018
 */

// These should match what is in the frontend code.
// for the sake of simplicity, make each state sequential.
typedef enum State
{
  DO_NOTHING = 0,
  EMERGENCY_STOP = 1,
  TEST_LED_ON = 2,
  TEST_LED_OFF = 3,
} State;

// These values should be assigned to the lowest and highest
// values in the state enum. Rememeber to change these!
const State FIRST_STATE = DO_NOTHING;
const State LAST_STATE = TEST_LED_OFF;

// The current state of the arduino.
State currentState = DO_NOTHING;

unsigned long lastSerialWriteTimestamp = millis();
const unsigned long serialWritePeriod = 500; //  ms

void setup()
{
  //
}


void listenToFrontend()
{
  // Assume that this will only ever recieve 4-byte integers
  // in little enidian format. The following code will cause
  // an issue if more or less than 4-bytes are ever transmitted.
  if (Serial.available() > 0)
  {
    // Assume incoming data is kl mn op qr, with each leter represnting
    // a half-byte (4 bits).
    int newState = 0x00000000;
    
    newState |= ((unsigned char)Serial.read()) >> 0;  // LHS: kl 00 00 00 RHS: kl 00 00 00

    // After the first byte is read, block until all remaining bytes are
    // read.
    while (!Serial.available());
    newState |= ((unsigned char)Serial.read()) >> 4;  // LHS: kl mn 00 00 RHS: 00 mn 00 00

    while (!Serial.available());
    newState |= ((unsigned char)Serial.read()) >> 8;  // LHS: kl mn op 00 RHS: 00 00 op 00

    while (!Serial.available());
    newState |= ((unsigned char)Serial.read()) >> 12; // LHS: kl mn op qr RHS: 00 00 00 qr
    
    if (FIRST_STATE <= (State)newState && (State)newState <= LAST_STATE)
    {
      currentState = (State)newState;
    }
  }
}

void sendMessageToFrontend()
{
  unsigned long currentTime = millis();

  if (currentTime - lastSerialWriteTimestamp < serialWritePeriod)
  {
    return;
  }
  
  // Since Serial.write sends one byte at a time if it's not a string,
  // the current state must be sent in 4 steps.
  Serial.write((unsigned char*)&currentState, sizeof(State));

  
  // NOTE: The serial protocol requires that all communications between
  // the controller to the frontend be newline terminated. 
  Serial.write('\n');

  // Update lastSerialWriteTimestamp, otherwise
  lastSerialWriteTimestamp = currentTime;
}

void loop()
{
  listenToFrontend();
  
  switch (currentState)
  {
    case DO_NOTHING:
      break;
    case EMERGENCY_STOP:
      break;
    case TEST_LED_ON:
      break;
    case TEST_LED_OFF:
      break;
  }

  sendMessageToFrontend();
}

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
    State* newState;
    char stateBuffer[4];
    stateBuffer[0] = Serial.read();
    stateBuffer[1] = Serial.read();
    stateBuffer[2] = Serial.read();
    stateBuffer[3] = Serial.read();
    newState = (State*)(&stateBuffer);
    
    if (FIRST_STATE <= *newState && *newState <= LAST_STATE)
    {
      currentState = *newState;
    }
  }
}

void sendMessageToFrontend()
{
  // Since Serial.write sends one byte at a time if it's not a string,
  // the current state must be sent in 4 steps.
  char * stateBuffer = (char *)(&currentState);
  Serial.write(stateBuffer[0]);
  Serial.write(stateBuffer[1]);
  Serial.write(stateBuffer[2]);
  Serial.write(stateBuffer[3]);

  
  // NOTE: The serial protocol requires that all communications between
  // the controller to the frontend be newline terminated. 
  Serial.write('\n');
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

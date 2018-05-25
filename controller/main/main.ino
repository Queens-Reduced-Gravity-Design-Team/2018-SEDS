/*
 * QRGX Microcontroller for 2018 SEDS. This is the main file.
 * 
 * Author(s): Viraj Bangari, Aaron Rosenstein
 * 
 * Date: May 2018
 */

//Digital Pin Declarations:
const int actuator_PWM[]={2,8};
const int actuator_2[]={3,7};
const int actuator_1[]={4,6};
const int actuator_STBY=5;

//Analog Pin Declarations:
const int potentiometer[]={0,1}; //Actuators
const int therm_1=2; //Heating Block Thermistors
const int therm_2=3;
const int therm_3=4;
const int therm_4=5; //Dry Block Heater Thermistor
const int amb_therm_1=6; //Ambient Temp Sensors
const int amb_therm_2=7; 

//Variable Declarations:
int minActuatorValue[2];
int maxActuatorValue[2];

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
  //Pin Initiations
  pinMode(actuator_1[0], OUTPUT);
  pinMode(actuator_1[1], OUTPUT);
  pinMode(actuator_2[0], OUTPUT);
  pinMode(actuator_2[1], OUTPUT);
  pinMode(actuator_PWM[0], OUTPUT);
  pinMode(actuator_PWM[1], OUTPUT);
  pinMode(actuator_STBY, OUTPUT);
  digitalWrite(actuator_STBY,HIGH);
  
  //Turn on the motor driver
  digitalWrite(actuator_STBY,HIGH);
  
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
    
    newState |= ((unsigned char)Serial.read()) << 0;  // LHS: kl 00 00 00 RHS: kl 00 00 00

    // After the first byte is read, block until all remaining bytes are
    // read.
    while (!Serial.available());
    newState |= ((unsigned char)Serial.read()) << 8;  // LHS: kl mn 00 00 RHS: 00 mn 00 00

    while (!Serial.available());
    newState |= ((unsigned char)Serial.read()) << 16;  // LHS: kl mn op 00 RHS: 00 00 op 00

    while (!Serial.available());
    newState |= ((unsigned char)Serial.read()) << 24; // LHS: kl mn op qr RHS: 00 00 00 qr
    
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

//Actuator Control Functions:

//gets the current actuator distance in mm:
int getActuatorDistance(int actuator)
{
  int scalingFactor=(maxActuatorValue[actuator-1]-minActuatorValue[actuator-1])/50;
  return (analogRead(potentiometer[actuator-1])-minActuatorValue[actuator-1])/scalingFactor;
}

//sets a designated actuator to a given distance value (mm) with a defined power value (1-255)
void setActuatorDistance(int actuator,int distance, int power)
{
  //determine the analog (0-1023) value required for the distance given.
  int scalingFactor=(maxActuatorValue[actuator-1]-minActuatorValue[actuator-1])/50;
  distance=scalingFactor*distance+minActuatorValue[actuator-1];
  
  //move actuators accordingly based on current location to the desired distance:
  while(distance<=analogRead(potentiometer[actuator-1]))
  {
    //Move piston inwards
    digitalWrite(actuator_1[actuator-1], LOW);
    digitalWrite(actuator_2[actuator-1], HIGH);
    analogWrite(actuator_PWM[actuator-1],power);
  }
  while(distance>=analogRead(potentiometer[actuator-1]))
  {
    //Move piston outwards
    digitalWrite(actuator_2[actuator-1], LOW);
    digitalWrite(actuator_1[actuator-1], HIGH);
    analogWrite(actuator_PWM[actuator-1],power);
  }
  //set all actuator control outputs to LOW:
    digitalWrite(actuator_2[actuator-1], LOW);
    digitalWrite(actuator_1[actuator-1], LOW);
    digitalWrite(actuator_PWM[actuator-1],LOW);
}

//Calibrate Actuators for Syringe Case inconsistencies:
void actuatorCalibrate()
{
  for(int i=0;i<=1;i++)
  {
    for(int j=0;j<=1;j++)
    {
      //When i=0, bring each actuator to its minimum while holding for 8 seconds to ensure that the point is reached
      //When i=1, do the same thing, but bringing the actuators to their maximum point.
      //record min/max for each actuator
      digitalWrite(actuator_1[j], i);
      digitalWrite(actuator_2[j], abs(i-1));
      analogWrite(actuator_PWM[j],255);
      delay(8000);
      switch(i)
      {
        case 0:
        minActuatorValue[j]=analogRead(potentiometer[j]);
        break;
        case 1:
        maxActuatorValue[j]=analogRead(potentiometer[j]);
        //disengage actuators
        digitalWrite(actuator_1[i], LOW);
        break;
      }
    }
  }
}

//Instruct actuators to take up a volume (in uL) of fluid, and whether to zero the actuator before taking up fluid.
void actuatorTakeUpVolume(int actuator, int volume,boolean zero)
{
  if(zero==true)
  {
    setActuatorDistance(actuator,0,255);
    delay(5000);
  }
  setActuatorDistance(actuator,0.6*volume,200); //0.6 corresponds to 0.6mm/uL --> 50uL = 30mm of travel.
}
void actuatorDispenseVolume(int actuator, int volume)
{
  int dist=getActuatorDistance(actuator);
  setActuatorDistance(actuator,dist-.6*volume,100);//dispense the volume instructed from the current plunger point.
}

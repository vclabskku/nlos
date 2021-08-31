#include "FastAccelStepper.h"

#define EN_PIN 5
#define DIR_PIN 6
#define STP_PIN 9
#define SENSOR 3

#define STEPS 5850
#define SET_SPEED 5000
#define SET_ACCEL 20000

char input; // for arduino - python serial communication 

FastAccelStepperEngine engine = FastAccelStepperEngine();
FastAccelStepper *stepper = NULL;

void setup() {
  Serial.begin(9600);
  pinMode(SENSOR, OUTPUT);
  
  engine.init();

  stepper = engine.stepperConnectToPin(STP_PIN);
  if(stepper) {
    stepper->setDirectionPin(DIR_PIN, true);
    stepper->setEnablePin(EN_PIN);
    stepper->setAutoEnable(true);
  }
  
  stepper_init();  
}

void loop() {
  while(Serial.available()) {
    input = Serial.read();
  }

  if(input == '1') {
    stepper_forward();
    input = '0';
  }
  else if(input == '2') {
    stepper_backward();
    input = '0';
  }
}

void stepper_init() {
  if(digitalRead(SENSOR) == 0) {
    stepper->setDirectionPin(DIR_PIN, false);
    stepper->setSpeedInHz(500);
    stepper->setAcceleration(1000);
    while(digitalRead(SENSOR) == 0) {
      stepper->move(1);
    }
    stepper->forceStopAndNewPosition(0);
  }
  else {
    stepper->setCurrentPosition(0);
  }
  Serial.println('3');
  delay(3000);
}

void stepper_forward() {
  stepper->setDirectionPin(DIR_PIN, true);
  stepper->setSpeedInHz(SET_SPEED);
  stepper->setAcceleration(SET_ACCEL);
  stepper->move(STEPS);
  
  while(stepper->isRunning()){}
  Serial.println('3');
}

void stepper_backward() {
  stepper->setDirectionPin(DIR_PIN, true);
  stepper->setSpeedInHz(SET_SPEED);
  stepper->setAcceleration(SET_ACCEL);
  stepper->moveTo(0);

  while(stepper->isRunning()){
    if(digitalRead(SENSOR) != 0) {
      stepper->forceStopAndNewPosition(0);
    }
  }
  Serial.println('3');
}

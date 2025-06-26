#include <TimerOne.h> // para la interrupción por tiempo

// 1) encoder
// Revisa cuantos pulsos PPR
int long encoder0PinA = 2; // pin 3 arduino uno
int long encoder0PinB = 3; // pin 4 arduino uno

float rps;

float e = 0.0, ref, A = 0.0, B = 0.0, C = 0.0, D = 0.0;
float uk1 = 0.0, yk1 = 0.0, yk2 = 0.0, ek1 = 0.0; // variables anteriores para el controlador
float ts; // tiempo de muestreo

float Kp = 4;
float Ki = 0.5;
float Td = 0.005;

long int pulsos;
long int pulsos2;
float pulsos_por_vuelta = 500.0;
float V_MAX = 12.00;

int estado = 0;

// 3) puente H
int pwm_pin = 5; // pin 5 arduino uno
byte pwm_motor = 0; // valor del pwm 8bits
float u = 0.0; // acción de control
float y = 0.0;
 
// --- Interrupción ---
void contador() {
  // Incrementa contador
  pulsos++;
}

void timerIsr() {
  rps = (float)((pulsos / pulsos_por_vuelta) / 0.05);
  pulsos2 = pulsos;
  pulsos = 0;
  if (estado == 0) {
    estado = 1;
  }
} 
 
////////////////////////////////////////////////////////// SETUP
void setup(void) {
  
  // encoder
  pinMode(encoder0PinA, INPUT);
  pinMode(encoder0PinB, INPUT);
  attachInterrupt(digitalPinToInterrupt(encoder0PinA), contador, RISING);
  attachInterrupt(digitalPinToInterrupt(encoder0PinB), contador, RISING);
  pulsos = 0;
  rps = 0.0;


  // puente
  pinMode(pwm_pin, OUTPUT);
  analogWrite(pwm_pin, 0);

  // interrupción
  Timer1.initialize(5000);
  Timer1.attachInterrupt(timerIsr);


  Serial.begin(500000); // Begin serial communication
  Serial.println("READY");

  ref = 1.15;
  ts = 0.005; // tiempo de muestreo en segundos (5ms)

  A = -Kp - Kp * Td / ts;
  B = Kp + 2 * Kp * Td / ts;
  C = -Kp * Td / ts;
  D = Kp * Ki * ts;

} 
 
//////////////////////////////////////////////////////// LOOP
void loop(void) {
  switch(estado) {
    case 0: // inicio
      break;

    case 1: // medir
      uk1 = u;
      yk2 = yk1;
      yk1 = y;
      ek1 = e;
      y = rps; // medición de salida
      e = ref - y; // error
      estado = 2; // llegá acá cada 10ms

      break;

    case 2: // calculo u
      // ACÁ AGREGAR MEDICIÓN, DEFINICIÓN DE ERROR Y CONTROLADOR, OBTENER u
      
      u = uk1 + A *y + B * yk1 + C * yk2 + D * ek1; // controlador PID modificado
      // Saturación del actuador
      if (u > 12){
          u = 12;
      }
      if (u < 0){
          u = 0;
      }
      //u = 8;

      pwm_motor = (byte)(u * 255.0 / V_MAX); // convierto a PWM

      analogWrite(pwm_pin, pwm_motor); // la mando por el pin de salida

      estado = 3;
      break;

    case 3: // comunico
      Serial.print(u);
      Serial.print(",");
      Serial.println(rps);
      estado = 0;
      break;
  }
}

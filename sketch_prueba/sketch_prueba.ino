const int VERDE = 13, AMARILLO = 12, ROJO = 11, BUZZER = 10;

void apagarTodo() {
  digitalWrite(VERDE, LOW);
  digitalWrite(AMARILLO, LOW);
  digitalWrite(ROJO, LOW);
  noTone(BUZZER);
}

void setup() {
  pinMode(VERDE, OUTPUT);
  pinMode(AMARILLO, OUTPUT);
  pinMode(ROJO, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  Serial.begin(115200);

  // prueba de arranque: cada LED enciende un momento
  int leds[] = {VERDE, AMARILLO, ROJO};
  for (int i = 0; i < 3; i++) {
    digitalWrite(leds[i], HIGH);
    delay(300);
    digitalWrite(leds[i], LOW);
  }
}

void loop() {
  if (Serial.available() > 0) {
    char c = toupper(Serial.read());
    if (c == 'G' || c == 'Y' || c == 'R') {
      apagarTodo();
      if (c == 'G') digitalWrite(VERDE, HIGH);
      if (c == 'Y') digitalWrite(AMARILLO, HIGH);
      if (c == 'R') {
        digitalWrite(ROJO, HIGH);
        tone(BUZZER, 1000, 600);   // pitido corto
      }
      Serial.print("OK:");
      Serial.println(c);
    }
  }
}
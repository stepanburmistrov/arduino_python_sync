// Определение пинов, к которым подключены светодиоды и кнопки
const int ledPins[] = { 5, 6, 7 };     // Пины светодиодов
const int buttonPins[] = { 2, 3, 4 };  // Пины кнопок
int ledStates = 0;                     // Состояния светодиодов хранятся в одном байте

// Настройка начальных параметров
void setup() {
  Serial.begin(9600);  // Инициализация порта
  // Настройка пинов светодиодов на вывод и пинов кнопок на ввод с подтяжкой к питанию
  for (int i = 0; i < 3; i++) {
    pinMode(ledPins[i], OUTPUT);
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

// Основной цикл выполнения
void loop() {
  // Проверка на наличие данных в порту
  if (Serial.available() > 0) {
    ledStates = Serial.read();  // Чтение полученных данных
    // Перебор светодиодов и обновление их состояния
    for (int i = 0; i < 3; i++) {
      digitalWrite(ledPins[i], (ledStates >> i) & 1);  // Установка состояния светодиода
    }
  }

  // Перебор кнопок для обработки их состояний
  for (int i = 0; i < 3; i++) {
    static unsigned long lastDebounceTime[3] = { 0, 0, 0 };  // Таймеры для антидребезга
    static bool lastButtonState[3] = { HIGH, HIGH, HIGH };   // Последние состояния кнопок

    bool currentButtonState = !digitalRead(buttonPins[i]);  // Чтение текущего состояния кнопки
    // Проверка на изменение состояния кнопки и антидребезг
    if (currentButtonState != lastButtonState[i] && (millis() - lastDebounceTime[i] > 50)) {
      lastDebounceTime[i] = millis();           // Обновление таймера антидребезга
      lastButtonState[i] = currentButtonState;  // Обновление состояния кнопки

      // Обработка нажатия кнопки
      if (currentButtonState == HIGH) {                  // Если кнопка отпущена
        ledStates ^= (1 << i);                           // Переключение бита состояния светодиода
        digitalWrite(ledPins[i], (ledStates >> i) & 1);  // Обновление состояния светодиода
        // Отправка обновленных состояний светодиодов через порт
        Serial.write(ledStates);
      }
    }
  }
}

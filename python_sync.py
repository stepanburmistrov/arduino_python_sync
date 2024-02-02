# Импортируем необходимые библиотеки
import serial
import serial.tools.list_ports
import cv2
import numpy as np
import time

# Функция для автоматического поиска и подключения к Arduino
def find_arduino_port():
    # Получаем список всех доступных COM-портов
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(port, end=" ")
        try:
            # Пытаемся открыть каждый порт
            ser = serial.Serial(port.device, 9600, timeout=1)
            print("opened")
            return ser  # Возвращаем объект порта, если успешно
        except serial.SerialException:
            # Продолжаем поиск, если порт не подходит
            continue

    # Выводим сообщение, если Arduino не найдена
    print("Arduino не найдена.")
    return None

# Ищем Arduino и подключаемся
ser = find_arduino_port()
if ser is None:
    exit()  # Завершаем программу, если подключение не удалось
time.sleep(2) #Ждем открытия порта

# Переменная для хранения состояний светодиодов
ledStates = 0

# Функция для отрисовки интерфейса управления светодиодами
def draw_interface():
    # Создаем черное изображение
    img = np.zeros((220, 310, 3), dtype=np.uint8)
    for i in range(3):
        # Определяем центральные точки светодиодов и кнопок
        center = (50 + i*100, 40)
        bottom_center = (50 + i*100, 60)

        # Выбираем цвет светодиода в зависимости от его состояния
        led_color = (0, 255, 0) if ledStates & (1 << i) else (0, 50, 0)

        # Рисуем полукруг и прямоугольник, имитируя форму светодиода
        cv2.ellipse(img, center, (20, 20), 0, 180, 360, led_color, -1)
        cv2.rectangle(img, (center[0] - 20, center[1]), (center[0] + 20, bottom_center[1]), led_color, -1)
        
        # Рисуем "ножки" светодиода
        cv2.line(img, (center[0] - 10, bottom_center[1]), (center[0] - 10, bottom_center[1] + 30), (200, 200, 200), 2)
        cv2.line(img, (center[0] + 10, bottom_center[1]), (center[0] + 10, bottom_center[1] + 40), (200, 200, 200), 2)

        # Рисуем кнопки
        button_center = (50 + i*100, 170)
        button_color = (200, 200, 200)
        cv2.rectangle(img, (30 + i*100, 150), (70 + i*100, 190), button_color, -1)
        cv2.circle(img, button_center, 10, (0, 0, 0), -1)
        
        # Добавляем подписи к светодиодам
        cv2.putText(img, f'LED {i+1}', (30 + i*100, 189), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

    # Отображаем созданное изображение
    cv2.imshow('LED Control', img)

# Функция для обработки событий мыши
def mouse_callback(event, x, y, flags, param):
    global ledStates
    # Проверяем нажатие левой кнопки мыши
    if event == cv2.EVENT_LBUTTONDOWN:
        # Перебираем координаты кнопок
        for i in range(3):
            if 30 + i*100 < x < 70 + i*100 and 150 < y < 190:
                # Изменяем состояние светодиода и отправляем новое состояние в Arduino
                ledStates ^= (1 << i)
                ser.write(bytearray([ledStates]))
                return

# Настройка окна OpenCV и привязка функции обработки событий мыши
cv2.namedWindow('LED Control')
cv2.setMouseCallback('LED Control', mouse_callback)

# Основной цикл программы
while True:
    # Чтение данных с Arduino
    if ser.in_waiting > 0:
        ledStates = ord(ser.read(1)) # Обновляем состояния светодиодов
    draw_interface() # Рисуем интерфейс
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Закрытие окна и освобождение ресурсов
cv2.destroyAllWindows()
ser.close()

import datetime
import json
import threading
import time
import configparser

import keyboard
import pyautogui
import pytesseract
import win32api
import win32con
from PIL import Image, ImageGrab
from Levenshtein import distance
from memory_profiler import profile

config = configparser.ConfigParser()
config.read('../resources/config.ini', encoding='utf-8')

INITIAL_SLEEP_TIME = config.getfloat("SLEEP", "INITIAL_SLEEP_TIME")
SHORT_SLEEP_TIME = config.getfloat("SLEEP", "SHORT_SLEEP_TIME")
MIDDLE_SLEEP_TIME = config.getfloat("SLEEP", "MIDDLE_SLEEP_TIME")
WALK_BACK_TIME = config.getfloat("SLEEP", "WALK_BACK_TIME")
WALK_SIDE_TIME = config.getfloat("SLEEP", "WALK_SIDE_TIME")
TURN_TIME = config.getfloat("SLEEP", "TURN_TIME")
WAIT_FOR_DOOR_TIME = config.getfloat("SLEEP", "WAIT_FOR_DOOR_TIME")

FOLDER = config.get("IMAGES", "FOLDER")
INITIALIZING_TEXT = FOLDER + config.get("IMAGES", "INITIALIZING_TEXT")
NEXT_BUTTON = FOLDER + config.get("IMAGES", "NEXT_BUTTON")
PANEL_BUTTON = FOLDER + config.get("IMAGES", "PANEL_BUTTON")

STOP_BUTTON = config.get("STOP", "STOP_BUTTON")

MOST_FREQUENT_GHOST = config.getboolean("GHOST", "MOST_FREQUENT")
GHOST_TYPE = config.get("GHOST", "SELECTED_GHOST_TYPE")

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SCREEN_COEFFICIENT = SCREEN_WIDTH / 1920
CONFIDENCE = 0.8
END_PROGRAM = False
GHOST_TYPES_CORDS = {
    "poltergeist": (int(1120 * SCREEN_COEFFICIENT), int(600 * SCREEN_COEFFICIENT)),
    "yurei": (int(1260 * SCREEN_COEFFICIENT), int(710 * SCREEN_COEFFICIENT)),
    'the twins': (int(1400 * SCREEN_COEFFICIENT), int(800 * SCREEN_COEFFICIENT)),
    'mara': (int(1120 * SCREEN_COEFFICIENT), int(650 * SCREEN_COEFFICIENT))
}

ENABLE_TESSERACT = config.getboolean("TESSERACT", "ENABLE")
if ENABLE_TESSERACT:
    pytesseract.pytesseract.tesseract_cmd = config.get("TESSERACT", "PATH")


def perform_mouse_click(x: int, y: int) -> None:
    """
    Функция перестановки курсора в определенную позицию и клика в данной позиции.
    :param x: Координаты установки курсора по ширине.
    :param y: Координаты установки курсора по высоте.
    :return:
    """
    win32api.SetCursorPos((int(x * SCREEN_COEFFICIENT), int(y * SCREEN_COEFFICIENT)))
    time.sleep(SHORT_SLEEP_TIME)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(SHORT_SLEEP_TIME)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def perform_keyboard_click(button: str) -> None:
    """
    Нажатие на клавиши на клавиатуре.
    :param button: Кнопка, которую нужно нажать.
    :return:
    """
    keyboard.press(button)
    time.sleep(SHORT_SLEEP_TIME)
    keyboard.release(button)


def select_map() -> None:
    """
    Функция выбора карты. Бот
        — из главного меню переходит на страницу выбора карты,
        — выбирает карту,
        — возвращается на главную страницу.
    :return:
    """
    perform_mouse_click(30, 540)
    time.sleep(MIDDLE_SLEEP_TIME)
    perform_mouse_click(450, 400)
    time.sleep(MIDDLE_SLEEP_TIME)
    perform_mouse_click(1900, 540)
    time.sleep(MIDDLE_SLEEP_TIME)


def start_game() -> None:
    """
    Функция запуска игры. Бот
        — нажимает кнопку готов,
        — нажимаю кнопку "играть"
    :return:
    """
    select_map()
    time.sleep(MIDDLE_SLEEP_TIME)
    perform_mouse_click(960, 950)
    time.sleep(MIDDLE_SLEEP_TIME)
    perform_mouse_click(1300, 950)


def is_image_on_screen(image_path: str, search_area: tuple = (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) -> (bool, tuple):
    """
    Нахождения заданного изображения на экране или в определенной области.
    :param image_path: Путь к заданному изображению.
    :param search_area: Область поиска (по умолчанию весь экран).
    :return:
    """
    image = Image.open(image_path)
    location = pyautogui.locateOnScreen(image, confidence=CONFIDENCE, region=search_area)
    image.close()

    if location:
        return True, location
    return False, location


def check_initializing_image() -> None:
    """
    Проверка загрузки карты.
    :return:
    """
    while True:
        if not is_image_on_screen(INITIALIZING_TEXT)[0]:
            time.sleep(0.5)
            if not is_image_on_screen(INITIALIZING_TEXT)[0]:
                break
        time.sleep(0.5)
    time.sleep(2)


def choose_ghost() -> None:
    """
    Определение призрака. Выбирается учитывая настройку из конфига (самый частый или заранее выбранный).
    :return:
    """
    if MOST_FREQUENT_GHOST:
        with open('../resources/ghost_type_frequency.json', 'r+') as json_file:
            ghosts = json.load(json_file)
            json_file.seek(0)
            most_frequent = max(ghosts, key=ghosts.get)
        perform_mouse_click(*GHOST_TYPES_CORDS[most_frequent])
        print(most_frequent)
    else:
        perform_mouse_click(*GHOST_TYPES_CORDS[GHOST_TYPE])


def select_ghost() -> None:
    """
    Выбор призрака (открытие журнала, выбор, закрытие журнала).
    :return:
    """
    perform_keyboard_click("j")
    time.sleep(MIDDLE_SLEEP_TIME)
    perform_mouse_click(1050, 80)
    time.sleep(MIDDLE_SLEEP_TIME)
    choose_ghost()
    time.sleep(MIDDLE_SLEEP_TIME)
    perform_keyboard_click("j")


def perform_actions_after_panel_flag() -> None:
    """
    Открытие дверей, выбор призрака и закрытие дверей.
    :return:
    """
    keyboard.release("d")
    time.sleep(SHORT_SLEEP_TIME)
    press_gate()

    time.sleep(SHORT_SLEEP_TIME)

    start = time.perf_counter()
    select_ghost()
    time.sleep(WAIT_FOR_DOOR_TIME - (time.perf_counter() - start))

    time.sleep(SHORT_SLEEP_TIME)

    press_gate()
    time.sleep(MIDDLE_SLEEP_TIME)
    perform_keyboard_click("p")


def complete_mission() -> None:
    """
    Выполнение миссии.
    :return:
    """
    perform_keyboard_click("o")
    time.sleep(SHORT_SLEEP_TIME)
    keyboard.press("d")

    start = time.perf_counter()
    while time.perf_counter() - start < 7:
        is_on_screen, location = is_image_on_screen(PANEL_BUTTON)
        if is_on_screen and 875 * SCREEN_COEFFICIENT <= location.left <= 930 * SCREEN_COEFFICIENT:
            break
        time.sleep(SHORT_SLEEP_TIME)

    perform_actions_after_panel_flag()


def press_gate() -> None:
    """
    Нажатие на панель управления дверью фургона.
    :return:
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(SHORT_SLEEP_TIME)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def check_end_game_image() -> None:
    """
    Проверка окончания загрузки (после завершения миссии).
    :return:
    """
    while True:
        if is_image_on_screen(NEXT_BUTTON)[0]:
            time.sleep(SHORT_SLEEP_TIME)
            if is_image_on_screen(NEXT_BUTTON)[0]:
                break
        time.sleep(1)


def end_game() -> None:
    """
    Действия после окончания миссии (принять награду, закрыть отчет игры).
    :return:
    """
    perform_mouse_click(429, 920)
    time.sleep(MIDDLE_SLEEP_TIME)
    perform_mouse_click(960, 720)
    time.sleep(MIDDLE_SLEEP_TIME)

    remember_ghost_type() if ENABLE_TESSERACT else write_logs()

    perform_mouse_click(1520, 920)


def write_logs(is_guessed: str = '', ghost_type: str = '') -> None:
    """
    Написание логов.
    :param is_guessed: Угадан ли призрак ('' или 'Guessed!').
    :param ghost_type: Тип призрака (указывается, если подключен tesseract)
    :return:
    """
    with open("../resources/logs.txt", "a") as f:
        f.write(f"{is_guessed}{ghost_type}finished: {str(datetime.datetime.now())}\n")


def find_closest_ghost_type(recognized_text: str, ghosts: list) -> str:
    """
    Нахождения наиболее похожего призрака на распознанный текст с изображения (иногда распознавание
    не дает точный результат)
    :param recognized_text: Распознанный текст.
    :param ghosts: Все призраки.
    :return: Тип призрака.
    """
    min_distance, closest_word = float('inf'), ""

    for json_word in ghosts:
        current_distance = distance(recognized_text, json_word)
        if current_distance < min_distance:
            min_distance = current_distance
            closest_word = json_word

    return closest_word


def remember_ghost_type() -> None:
    """
    Составление отчета о количество призраков, которые встречались.
    :return:
    """
    with open('../resources/ghost_type_frequency.json', 'r+') as json_file:
        ghosts = json.load(json_file)
        json_file.seek(0)

        screenshot = ImageGrab.grab(bbox=(int(1000 * SCREEN_COEFFICIENT), int(900 * SCREEN_COEFFICIENT),
                                          int(1310 * SCREEN_COEFFICIENT), int(970 * SCREEN_COEFFICIENT)))
        ghost_type = pytesseract.image_to_string(screenshot).strip().lower()
        ghost_type = find_closest_ghost_type(ghost_type, ghosts)
        screenshot.close()

        ghosts[ghost_type] += 1
        is_guessed = 'Guessed! ' if GHOST_TYPE == ghost_type else ''

        json.dump(ghosts, json_file, indent=4)
        json_file.truncate()

    write_logs(is_guessed, ghost_type + ' ')


@profile
def play() -> None:
    """
    Цикл игры (начало, выполнение миссии и окончание).
    :return:
    """
    start_game()
    check_initializing_image()

    complete_mission()

    check_end_game_image()
    end_game()


def infinite_play() -> None:
    """
    Повтор цикла игры, пока он не будет остановлен.
    :return:
    """
    while True:
        time.sleep(INITIAL_SLEEP_TIME)
        play()
        if END_PROGRAM:
            break


def finish() -> None:
    """
    Остановка цикла игры по нажатию клавиши.
    :return:
    """
    global END_PROGRAM
    while True:
        if keyboard.is_pressed(STOP_BUTTON):
            END_PROGRAM = True
            break
        time.sleep(SHORT_SLEEP_TIME)


def run() -> None:
    """
    Запуск в нескольких потоках игры и остановки игры для возможности обработки нажатия стоп
    кнопки во время выполнения цикла игры.
    :return:
    """
    play_thread = threading.Thread(target=infinite_play)
    finish_thread = threading.Thread(target=finish)

    play_thread.start()
    finish_thread.start()

    play_thread.join()
    finish_thread.join()

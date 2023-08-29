from bot import perform_keyboard_click, perform_actions_after_panel_flag, start_game, end_game
from bot import SHORT_SLEEP_TIME, SCREEN_COEFFICIENT
from PIL import ImageGrab
import keyboard
import time


def take_and_save_screenshot(area: tuple, path: str) -> None:
    """
    Функция создания скриншота определенного размера и его сохранения в файл.
    :param area: Область скриншота.
    :param path: Путь сохранения.
    :return:
    """
    screenshot = ImageGrab.grab(bbox=area)
    screenshot.save(path)
    screenshot.close()


def complete_mission() -> None:
    """
    Выполнение миссии (в отличие от основной, делает по ходу движения необходимые скриншоты
    для оптимизации работы бота)
    :return:
    """
    perform_keyboard_click("o")
    time.sleep(SHORT_SLEEP_TIME)
    keyboard.press("d")
    time.sleep(7)

    take_and_save_screenshot((int(1000 * SCREEN_COEFFICIENT), int(900 * SCREEN_COEFFICIENT),
                              int(1310 * SCREEN_COEFFICIENT), int(970 * SCREEN_COEFFICIENT)),
                             "../resources/images/panel.png")

    perform_actions_after_panel_flag()


def setup() -> None:
    """
    Настройка бота (включает в себя пробный запуск игры).
    :return:
    """
    start_game()
    take_and_save_screenshot((int(1000 * SCREEN_COEFFICIENT), int(900 * SCREEN_COEFFICIENT),
                              int(1310 * SCREEN_COEFFICIENT), int(970 * SCREEN_COEFFICIENT)),
                             "../resources/images/initializing.png")
    complete_mission()
    time.sleep(20)
    take_and_save_screenshot((int(1000 * SCREEN_COEFFICIENT), int(900 * SCREEN_COEFFICIENT),
                              int(1310 * SCREEN_COEFFICIENT), int(970 * SCREEN_COEFFICIENT)),
                             "../resources/images/next.png")
    end_game()


def main() -> None:
    """
    Запуск настройки бота
    :return:
    """
    setup()


if __name__ == "__main__":
    main()

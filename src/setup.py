from bot import complete_mission, start_game, end_game, check_initializing_image
from bot import FOLDER, SCREEN_COEFFICIENT
from PIL import ImageGrab
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


def setup() -> None:
    """
    Настройка бота (включает в себя пробный запуск игры).
    :return:
    """
    start_game()
    time.sleep(3)
    take_and_save_screenshot((int(750 * SCREEN_COEFFICIENT), int(900 * SCREEN_COEFFICIENT),
                              int(980 * SCREEN_COEFFICIENT), int(970 * SCREEN_COEFFICIENT)),
                             FOLDER + "initializing.png")
    check_initializing_image()
    complete_mission()
    time.sleep(20)
    take_and_save_screenshot((int(1400 * SCREEN_COEFFICIENT), int(900 * SCREEN_COEFFICIENT),
                              int(1550 * SCREEN_COEFFICIENT), int(970 * SCREEN_COEFFICIENT)),
                             FOLDER + "next.png")
    end_game()


def main() -> None:
    """
    Запуск настройки бота
    :return:
    """
    time.sleep(2)
    setup()


if __name__ == "__main__":
    main()

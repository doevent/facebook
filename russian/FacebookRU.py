# -*- coding: utf8 -*-

# patch chromedriver.exe:  Replacing cdc_ variable ($cdc_asdjflasutopfhvcZLmcfl_)

import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException, NoSuchElementException

import time
import random
import datetime
import configparser

import tempfile
import os
import time
import telebot
import requests # проверка версии

import tkinter as tk # окно
import argparse # командная строка


log_filename = f'fb_log\\facebook_select_ru-{datetime.datetime.now().strftime("%d-%m-%Y")}.log'
logging.basicConfig(filename=log_filename, level=logging.INFO, filemode='a', format=' %(asctime)s: %(name)s - %(levelname)s - %(message)s')
print(log_filename)
logging.info("==============================================================")
logging.info("Старт программы")


# Загрузка настроек из ini файла
try:
    config = configparser.ConfigParser()
    config.read('settings.ini')
    version = config.get("Settings", "version") # Текущая версия
    chrome_user = config.get("Settings", "chrome_user") # Имя пользователя в браузере Хром
    width_set = int(config.get("Settings", "width")) # Ширина окна браузера
    height_set = int(config.get("Settings", "height")) # Высота окна браузера сториес
    images_set = int(config.get("Settings", "images")) # включает и отключает картинки
    stories_set = int(config.get("Settings", "stories")) # количество циклов сториес
    birthday_set = int(config.get("Settings", "birthday")) # количество циклов поздравления
    feed_set = int(config.get("Settings", "feed")) # количество циклов в ленте друзей
    feed_select = int(config.get("Settings", "feed_select")) # # релевантные или новые сообщения в ленте
    API_TOKEN = str(config.get("Settings", "token")) # Токен телеграм бота
    BotID = str(config.get("Settings", "botid")) # ID телеграм бота


    stories_set_end = stories_set - 1 # отнимаем единицу, для условия завешения работы
except Exception as e:
    logging.exception("Ошибка загрузки INI")
    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка загрузки INI")

if API_TOKEN != '0' and BotID != '0' and len(API_TOKEN) > 15 and len(BotID) > 5:
    bot = telebot.TeleBot(API_TOKEN)

# Проверка версии
r_version = 0
upd_version = 0
try:
    r_version = requests.get('https://skobeev.design/fb/version.txt')
    r_version.encoding = 'utf-8' 
    upd_version = r_version.text
    # print(f"Текущая версия: {version}\nПоследняя версия: {r_version.text}")
    logging.info(f"Текущая версия: {version}")
    if upd_version == version:
        print(f"Последняя версия установлена: {version}")
    else:
        print(f"Последняя версия: {upd_version}")
except Exception as e:
    upd_version = "Недоступно"
    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка проверки версии.")
    logging.exception('Ошибка проверки версии')


driver = 0 # селениум
# переменные счетчиков сториес
count_like = 0
count_super = 0
count_together = 0
next_refrash = 0
print (f"\nТекущая версия: {version}\nПоследняя версия: {upd_version}")
print (f"\n{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ожидание...\n")


#Функция Создания окна браузера
def start_browser():
    global driver

    #настройки создания окна хрома
    options = webdriver.ChromeOptions() 
    options.add_argument("disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"user-data-dir={os.path.expanduser('~')}\\AppData\\Local\\Google\\Chrome\\User Data\\{chrome_user}")
    if images_set == 0: # отключает картинки
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    try:
        # создаем пустое окно браузера
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Создаем окно браузера...")
        driver = webdriver.Chrome(options=options)
    except WebDriverException:
        logging.exception("Ошибка в каталоге TEMP")
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка в каталоге TEMP\n{tempfile.gettempdir()}")
        try:
            if os.path.exists(tempfile.gettempdir()) == False:
                logging.warning("Каталог не найден. Создаем новый.\n{tempfile.gettempdir()}")
                os.mkdir(tempfile.gettempdir())
        except Exception as e:
            logging.exception("Ошибка создания каталога в TEMP")
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка создания каталога в TEMP\n{tempfile.gettempdir()}")
    except Exception as e:
        logging.exception('Ошибка создания окна браузера')

        
    # Маскировка браузера от фейсбука
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
        """
        })

    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})
    # Конец масикровки
    driver.set_window_rect(10,10, width_set, height_set)
    driver.get("https://facebook.com/")
    time.sleep(3)
    
    size = driver.get_window_size()
    position = driver.get_window_position()
    print(f"Window size: width = {size['width']}px, height = {size['height']}px, x = {position['x']}, y = {position['y']}")
    logging.info(f"Window size: width = {size['width']}px, height = {size['height']}px, x = {position['x']}, y = {position['y']}")
    print(driver.capabilities['browserVersion'])
    logging.info(driver.capabilities['browserVersion'])
    ActionChains(driver).send_keys(Keys.ESCAPE).perform() #жмем esc чтобы убрать всплывающие окна
    time.sleep(1)
    ActionChains(driver).send_keys(Keys.ESCAPE).perform() #жмем esc чтобы убрать всплывающие окна
    ActionChains(driver).reset_actions()
    if API_TOKEN != '0' and BotID != '0' and len(API_TOKEN) > 15 and len(BotID) > 5:
        bot.send_message(BotID, f"<b>Start FACEBOOK Bot</b>\nТекущая версия: <b>{version}</b>\nПоследняя версия: <b>{upd_version}</b>\nЛог: {log_filename}\n", parse_mode='Html')
        bot.send_message(BotID, f"<b>Создано новое окно браузера.</b>\n{driver.title}\nВерсия Chrome: {driver.capabilities['browserVersion']}\nWindow size: width = {size['width']}px, height = {size['height']}px,\nx = {position['x']}, y = {position['y']}", parse_mode='Html')
    logging.info("Создано окно браузера.")

    try:
        # Закрываем вкладки
        driver.implicitly_wait(7)
        count_close = driver.find_elements_by_css_selector('[aria-label="Закрыть чат"]')
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Найдено открытых вкладок: {len(count_close)}")
        for send_close in count_close:
            send_close.click()
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Закрыта вкладка")
            time.sleep(5)
            try:
                driver.find_element_by_css_selector('[aria-label="ОК"]').click()
                time.sleep(5)
            except Exception as e:
                logging.debug(e)
    except Exception as e:
        logging.debug(e)

#-----------------------------------------------------------
# Старт функции поздравлений
def start_birthday_fb():
    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Старт функции поздравлений...")

    start_browser()
    logging.info('Старт сценария поздравлений с днем рождения')
    if API_TOKEN != '0' and BotID != '0' and len(API_TOKEN) > 15 and len(BotID) > 5:
        bot.send_message(BotID, "<b>Старт</b> сценария поздравлений с днем рождения.", parse_mode='Html')

    
    try:
        driver.find_element_by_css_selector("[href='/events/birthdays/']").click()
        time.sleep(random.randrange(15,20))
    except Exception as e:
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Картинка с подарком не найдена.\n{e}")
        logging.warning(f"Картинка с подарком не найдена.\n{e}")
    else:
        try:
            birthday_message() # Если всё ОК, переходим в функцую отправки сообщений
        except Exception as e:
            driver.quit()
            logging.debug(e)

# Основная функция отправки поздравлений
def birthday_message():
    start_time = time.time()
    driver.implicitly_wait(40) # seconds
    time.sleep(random.randrange(18,27))

    try:
        with open("birthday.txt", "r", encoding="utf-8") as f:
            birthday = f.readlines()
            
            count_post = driver.find_elements_by_css_selector('[method="POST"]')
            len_count = len(count_post)-1
            print (f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Найдено полей для поздавлений: {len_count}")

            count_button = len(driver.find_elements_by_css_selector('[aria-label="Сообщение"]'))
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Найдено кнопок СООБЩЕНИЕ (в личку):  {count_button}")
                
            logging.info(f'Найдено полей для поздавлений: {len_count}')
            num_msg = 0 #счетчик отправленных хроник
            num_button = 0

            # # Переходим на страницу с поздравлениями
            # driver.get("https://www.facebook.com/events/birthdays/")
            # driver.implicitly_wait(10) # seconds
            # time.sleep(3)

            # ActionChains(driver).send_keys(Keys.ESCAPE).perform() #жмем esc чтобы убрать всплывающие окна
            # time.sleep(2)
            # ActionChains(driver).send_keys(Keys.ESCAPE).perform() #жмем esc чтобы убрать всплывающие окна
            # time.sleep(2)
            # ActionChains(driver).send_keys(Keys.HOME).perform() # листаем вверх
            # time.sleep(random.randrange(10,15))

    except Exception as e:
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка в блоке поздравлений\n{e}\n")
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Прерывание цикла")
        logging.exception("Ошибка в блоке поздравлений.")
        try:
            driver.quit()
        except Exception as e:
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка закрытия браузера...")


    for cv in range(0,200): #перебираем элементы и когда элемент окажется тектовым - отправляем поздравление
        ActionChains(driver).send_keys(Keys.TAB).perform()
        element = driver.switch_to.active_element
        # if element.find_elements_by_tag_name('span'):
        #     print(element.get_attribute("innerHTML"), "\n")
        driver.implicitly_wait(0)
        if len_count == num_msg or len_count == 0 or num_msg >= 19:
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Поздравления в хронике кончились: {num_msg}. Циклов всего: {cv}")
            break
        try:
            if element.find_element_by_tag_name('br').get_attribute('data-text') == 'true':
                try:
                    cmess = driver.find_elements_by_css_selector('[method="POST"]')
                    # cmess[0].location_once_scrolled_into_view
                    # time.sleep(random.randrange(2, 5))
                    txt = str(random.choice(birthday).replace("\n", ""))
                    ActionChains(driver).send_keys_to_element(element, txt, Keys.ENTER).perform()
                    num_msg += 1
                    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Поздравление в хронику №: {num_msg}")
                    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Текст: {txt}")
                    time.sleep(random.randrange(10, 15))
                    ActionChains(driver).reset_actions()

                except NoSuchElementException as e:
                    print(e)
                    logging.info(e)
                except Exception as e:
                    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка в цикле отправления поздравлений. Поздравление №: {num_msg}.\n{e}")
                    logging.exception(f"Ошибка в цикле отправления поздравлений. Поздравление №: {send_msg}.\n{e}")
                    break

        except Exception as e:
            logging.warning(f"Поздравления в хронику: {e}")



    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Начало поздравлений в личку")

    if count_button != 1 or count_button == 0: # если 0 и 1 то не перезагружаем страницу
        for t in range(0, 2):
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()  # жмем esc чтобы убрать всплывающие окна
            time.sleep(2)
        time.sleep(random.randrange(3, 6))

        driver.implicitly_wait(10)
        driver.get("https://www.facebook.com/events/birthdays/")
        time.sleep(random.randrange(10, 15))

    # Поиск кнопки
    try:
        for msgbut in driver.find_elements_by_css_selector('[aria-label="Сообщение"]'):
            if count_button == num_button or count_button == 0 or num_button >= 15:
                print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Поздравления в личку кончились: {num_button}.")
                break
            try:
                # Клик по кнопке
                try:
                    msgbut.click()
                except Exception as e:
                    print(msgbut.location)
                    print(f'Ошибка в клике по кнопке СООБЩЕНИЕ. Пробуем второй способ {e}')
                    ActionChains(driver).move_to_element(msgbut).click().perform()

                txt = str(random.choice(birthday).replace("\n", ""))
                time.sleep(random.randrange(40, 50))
                ActionChains(driver).send_keys(txt, Keys.ENTER).perform()
                num_button += 1
                time.sleep(random.randrange(5,10))
                print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Поздравление в личку: {num_button}")
                print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Текст: {txt}")
                ActionChains(driver).reset_actions()


                driver.implicitly_wait(20)
                #закрываем вкладки
                count_close = driver.find_elements_by_css_selector('[aria-label="Закрыть чат"]')

                for send_close in count_close:
                    send_close.click()
                    time.sleep(random.randrange(5,10))
                    try:
                        driver.find_element_by_css_selector('[aria-label="ОК"]').click()
                    except NoSuchElementException as e:
                        logging.debug(e)
                print(f'Закрыто вкладок: {len(count_close)}')
                time.sleep(random.randrange(10, 15))
            except Exception as e:
                print(f'Блок поздравлений в личку: {e}')
                logging.warning(f'Не может кликнуть на кнопку СООБЩЕНИЕ: {e}')
                break
    except Exception as e:
        print(e)
        logging.warning(f"Поздравления в личные сообщения: {e}")

                    
    logging.info(f'Отправлено поздравлений: {num_msg} из {len_count}')
    print (f"\n\nОправлено поздравлений в хронику: {num_msg} из {len_count}")
    print(f"Оправлено поздравлений в личку: {num_button} из {count_button}")
    print(f'Время выполнения: {round(time.time() - start_time, 1)} секунд')
    print (f"\n\n{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ожидание...\n")
    try:
        if API_TOKEN != '0' and BotID != '0' and len(API_TOKEN) > 15 and len(BotID) > 5:
            bot.send_message(BotID, f"<b>Конец</b> функции BIRTHDAY.\n\nОправлено поздравлений в хронику: <b>{num_msg}</b> из <b>{len_count}</b>\n"
                                    f"Оправлено поздравлений в личку: <b>{num_button}</b> из <b>{count_button}</b>"
                                    f"\nВремя выполнения: {round(time.time() - start_time, 1)} секунд", parse_mode='Html')
    except Exception as e:
        logging.debug(e)
    f.close()
    try:
        driver.quit()
    except Exception as e:
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка закрытия браузера...")





#-----------------------------------------------------------
# Начало функций сториес
def start_stories_fb():
    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Старт функции STORIES...")
    start_browser() # создаем окно
    logging.info('Старт сценария лайков сториес.')
    
    if API_TOKEN != '0' and BotID != '0' and len(API_TOKEN) > 15 and len(BotID) > 5:
        bot.send_message(BotID, "Старт сценария лайков сториес.")

    driver.get("https://www.facebook.com/")
    
    driver.implicitly_wait(60) # seconds
    time.sleep(10)
    wait = WebDriverWait(driver, 60)
    
    time.sleep(random.randrange(15,20))
    try:
        driver.find_element_by_css_selector("[aria-label='Все истории']").click()
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Кнопка ВСЕ ИСТОРИИ найдена.")
        logging.info("Кнопка ВСЕ ИСТОРИИ НАЙДЕНА.")
        time.sleep(15)

        stories_likes()


    except Exception as e:
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Не найдена кнопка Все истории \n{e}")
        logging.exception("Не найдена кнопка 'Все истории'.")
        stories_fb_alternative()  # Ищем на странице кнопку, если не найдена, то переходим на альтернатиынй вариант

#альтернативный сценарий входа в сториес
def stories_fb_alternative():
    logging.info("Включение функции альтернативного сценария сториес")
    

    driver.get("https://www.facebook.com/stories")
    driver.implicitly_wait(10) # seconds
    time.sleep(10)
  
    #перемещаемся по ссылкам на сториес человека
    ActionChains(driver).send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB).perform() # нужны три таба, но плюс один когда есть своя сториес.
    time.sleep(random.randrange(5,8))
    ActionChains(driver).send_keys(Keys.RETURN).perform()
    stories_likes() # переходим в функцию поиска кнопок и лайков

# кнопки лайк, супер и звук и тд...
def stories_button(button, stories=None):
    #переменные счетчиков
    global count_like
    global count_super
    global count_together
    global next_refrash
    
    wait = WebDriverWait(driver, 3)
    
    # Отключаем звук на компе
    if button == 'sound':
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Выключить звук"]'))).click()
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Звук выключен")
        except Exception as e:
            print (f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка кнопки вкл\выкл звука...\n{e}")
            logging.info("Ошибка кнопки вкл\выкл звука...\n{e}")
    
    elif button == 'like':
        try:
            buttonLIKE = driver.find_elements_by_css_selector('[aria-label="Нравится"]')
            for btn_like in buttonLIKE:
                driver.implicitly_wait(0)  # seconds
                try:
                    btn_like.click()
                    # print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Кнопка лайк - найдена...")
                    break
                except Exception as e:
                    logging.debug('Like button not found')
                    # print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Кнопка ЛАЙК не найдена. Ищем дальше...")
            count_like = count_like + 1
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> {stories} - ЛАЙК...")
        except Exception as e:
            logging.debug('Error find LIKEButton')
    elif button == 'love':
        try:
            # wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-reaction="2"]'))).click()
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Супер"]'))).click()
        except Exception as e:
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Кнопка SUPER не найдена.\n{e}")
            logging.info(f"Блок Сториес. Не найдена кнопка SUPER.\n{e}")
        else:
            count_super += 1
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> {stories} - СУПЕР...")
    
    elif button == 'cave':
        try:
            # wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-reaction="16"]'))).click()
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Мы вместе"]'))).click()
        except Exception as e:
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Кнопка МЫ ВМЕСТЕ не найдена.\n{e}")
            logging.info(f"Блок Сториес. Не найдена кнопка МЫ ВМЕСТЕ.\n{e}")
        else:
            count_together += 1 # счетчик мы вместе
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> {stories} - МЫ ВМЕСТЕ..")
    elif button == 'next':
        # NEXT
        try:
            wait = WebDriverWait(driver, 3)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '''[aria-label='Кнопка "Следующая подборка"']'''))).click()
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> {stories} Кнопка: Следующая подборка")
            time.sleep(random.randrange(1,2))
            next_refrash = 0 # clear count error
        except Exception as e:
            try:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '''[aria-label='Кнопка "Следующая открытка"']'''))).click()
                print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> {stories} Кнопка: Следующая открытка")
                time.sleep(random.randrange(1,2))
                next_refrash = 0 # clear count error
            except Exception as e:
                print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Не найдены обе кнопки NEXT. Обновление...")
                logging.debug("Блок Сториес. Не найдены кнопки NEXT. Обновление.")
                
                next_refrash += 1
                
                print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Обновление окна.")
                logging.info('Refresh browser. No button NEXT')
                driver.refresh()
                time.sleep(random.randrange(10,15))
                #перемещаемся по ссылкам на сториес человека
                ActionChains(driver).send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.RETURN).perform()
                time.sleep(random.randrange(4,8))
                try:
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Выключить звук"]'))).click()
                    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Звук выключен")
                except Exception as e:
                    print (f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка кнопки вкл\выкл звука...\n{e}")
                    logging.info("Ошибка кнопки вкл\выкл звука...\n{e}")

# основная функция лайков сториес
def stories_likes():
    count_next = 0
    count_skip = 0
    next_refrash = 0
    start_time = time.time()
    wait = WebDriverWait(driver, 30)
    driver.implicitly_wait(5) # seconds

    #перемещаемся по ссылкам на сториес человека
    ActionChains(driver).send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB).perform() # , Keys.RETURN
    time.sleep(random.randrange(4,8))
    
    try:
        # листаем фрейм со списком сториес, чтобы он прогрузился
        element = driver.switch_to.active_element # сохраняем активный элемент
        for tx in range(0, 8):
            ActionChains(driver).send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB).perform()
            time.sleep(random.randrange(4,7))
        # time.sleep(random.randrange(30,40))
        # возвращаемся к сохраненному элементу
        element.location_once_scrolled_into_view
        time.sleep(random.randrange(2,3))
        element.click()
    except Exception as e:
        logging.warning(f"Ошибка в блоке прогрузки фрейма сториес\n{e}")
        ActionChains(driver).send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.RETURN).perform()
        
    stories_button('sound')
    try:
        # Цикл лайков
        for stories in range(0, stories_set):
            wait = WebDriverWait(driver, 3)
            rnd_like = random.randrange(1,9)

            # генерация разных сценариев лайков
            if rnd_like == 1:
                # Одинарный лайк
                stories_button('like', stories)
 
            elif rnd_like == 2:
                #Одинарный супер
                stories_button('love', stories)
            
            elif rnd_like == 3:
                # Несколько лайков
                for mkmk in range(0,random.randrange(2,5)):
                    stories_button('like', stories)
            
            elif rnd_like == 4:
                # Несколько Супер
                for mkmk in range(0, random.randrange(2,5)):
                    stories_button('love', stories)
            
            elif rnd_like == 5:
                # Лайк + Супер
                stories_button('like', stories)
                time.sleep(random.randrange(1,4))
                stories_button('love', stories)
            
            elif rnd_like == 6:
                # Супер + Лайк
                stories_button('love', stories)
                time.sleep(random.randrange(1,4))
                stories_button('like', stories)
            
            elif rnd_like == 7:
                # Лайк, супер, мы вместе
                stories_button('like', stories)
                time.sleep(random.randrange(1,4))

                stories_button('love', stories)
                time.sleep(random.randrange(2,4))
                stories_button('cave', stories)
                
            elif rnd_like == 8:
                # Мы вместе
                stories_button('cave', stories)

            # NEXT
            stories_button('next', stories)
            if next_refrash == 3: # if repeat error no button NEXT - quit browser
                print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Кнопки не найдены. Закрываем браузер...")
                logging.warning("Не найдены кнопки NEXT. Закрываем браузер.")
                driver.quit()
                break
            
            count_next += 1
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> {stories} - Листаем...")
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Цикл № {stories} из {stories_set_end} ...")
            time.sleep(random.randrange(2,4))
            
            if stories_set_end == stories: #если цикл закончен, закрываем браузер
                print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> {stories} - Цикл лайков успешно завершен")
                logging.info(f"Кол-во: {stories} - Цикл лайков успешно завершен.")
                
                driver.quit()
                print (f"\n\nПоставлено лайков: {count_like}\nПоставленно сердечек: {count_super}\nПоставлено Мы вместе: "
                       f"{count_together}\nПролистано: {count_next}\nВсего циклов: {stories + 1}\nВремя выполнения: {round(time.time() - start_time, 1)} секунд")
                print (f"\n\n{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ожидание...\n")
                try:
                    if API_TOKEN != '0' and BotID != '0' and len(API_TOKEN) > 15 and len(BotID) > 5:
                        bot.send_message(BotID, f"Конец функции LIKE STORIES:\n\nПоставлено лайков: {count_like}\nПоставленно сердечек: {count_super}"
                                                f"\nПоставлено Мы вместе: {count_together}\nПролистано: {count_next}"
                                                f"\nВсего циклов: {stories + 1}\nВремя выполнения: <b>{round(time.time() - start_time, 1)} </b>секунд", parse_mode='Html')
                except Exception as e:
                    logging.debug(e)
                
    except Exception as e:
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ошибка в блоке цикла генерации вариантов лайков {e}")
        logging.exception("Функция лайков сториес. Ошибка в блоке цикла генерации вариантов лайков")
        driver.quit()


#-----------------------------------------------------------
# Функция начала лайков в ленте
def start_feed_likes():
    logging.info("Старт сценария лайков ленты новостей.")
    if API_TOKEN != '0' and BotID != '0' and len(API_TOKEN) > 15 and len(BotID) > 5:
        bot.send_message(BotID, "<b>Старт</b> сценария лайков ленты новостей.", parse_mode='Html')

    print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Старт функции LIKES FEED...")
    
    start_browser()

    if feed_select == 0:
        driver.get("https://www.facebook.com/")
    else:
        driver.get("https://www.facebook.com/?sk=h_chr")
        
    time.sleep(random.randrange(10,15))
    feed_likes()

# Основная функция лайков
def feed_likes():
    err_like = 0
    #переменные счетчиков
    count_like = 0
    count_super = 0
    count_together = 0
    count_select = 0
    start_time = time.time()

    # основной цикл
    for x_all in range(0, feed_set):
        ActionChains(driver).send_keys(Keys.ESCAPE).perform() #жмем esc чтобы убрать всплывающие окна
        time.sleep(random.randrange(1,3))
        
        ActionChains(driver).send_keys("j").perform()
        time.sleep(random.randrange(6,10))
        ActionChains(driver).send_keys("l").perform()
        ActionChains(driver).reset_actions()
        time.sleep(random.randrange(7,10))

        rnd_like_feed = random.randrange(1,4)
        if rnd_like_feed == 1:
            ActionChains(driver).send_keys(Keys.SPACE).perform() # жмем пробел
            count_like = count_like + 1
            print (f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Нравится: {count_like}")

        elif rnd_like_feed == 2:
            ActionChains(driver).send_keys(Keys.TAB).perform() # жмем лево
            time.sleep(random.randrange(2,4))
            ActionChains(driver).send_keys(Keys.SPACE).perform() # жмем пробел
            count_super = count_super + 1
            print (f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Супер: {count_super}")

            
        elif rnd_like_feed == 3:
            ActionChains(driver).send_keys(Keys.TAB + Keys.TAB).perform() # жмем лево
            time.sleep(random.randrange(2,4))
            ActionChains(driver).send_keys(Keys.SPACE).perform() # жмем пробел
            count_together = count_together + 1
            print (f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Мы вместе: {count_together}")
                    
        print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Сделано циклов {x_all} из {feed_set - 1}\n")
        ActionChains(driver).reset_actions()
            
        time.sleep(random.randrange(1,5))
        
        
        if x_all == feed_set - 1:
            print(f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Цикл лайков ленты закончен.")
            print(f"\nНравится: {count_like}\nСупер: {count_super}\nМы вместе: {count_together}\nВсего циклов: {feed_set - 1}"
                  f"\nСделано циклов: {x_all}\nВремя выполнения: {round(time.time() - start_time, 1)} секунд")
            print (f"\n\n{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} >> Ожидание...\n")
            logging.info("Цикл лайков ленты закончен")
            try:
                if API_TOKEN != '0' and BotID != '0' and len(API_TOKEN) > 15 and len(BotID) > 5:
                    bot.send_message(BotID, f"<b>Конец</b> функции <b>ЛАЙКИ ЛЕНТЫ НОВОСТЕЙ</b>:\nНравится: <b>{count_like}</b>"
                                            f"\nСупер: <b>{count_super}</b>\nМы вместе: <b>{count_together}</b>"
                                            f"\nСделано циклов: <b>{x_all}</b> из <b>{feed_set - 1}</b>"
                                            f"\nВремя выполнения: <b>{round(time.time() - start_time, 1)} секунд</b>", parse_mode='Html')
            except Exception as e:
                logging.debug(e)
            driver.quit()
        
        time.sleep(random.randrange(1,5))



# Отрыть ini файл
def open_file():
    with open('settings.ini', "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    window.title(f"Facebook autoclicker")

# Сохранить ini файл
def save_file():
    with open('settings.ini', "w") as output_file:
        text = txt_edit.get(1.0, tk.END)
        output_file.write(text)


window = tk.Tk()
window.title("facebook-auto-liker-bot")
window.rowconfigure(0, minsize=500, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

txt_edit = tk.Text(window)
fr_buttons = tk.Frame(window, relief=tk.RAISED)
btn_open = tk.Button(fr_buttons, text="Открыть", command=open_file)
btn_save = tk.Button(fr_buttons, text="Сохранить", command=save_file)

# Текущая версия: {version}\nПоследняя версия: {upd_version}

button1 = tk.Button(fr_buttons, text="Лайки сториес", bg="blue", fg="yellow", command=start_stories_fb)
button2 = tk.Button(fr_buttons, text="Лайки ленты", bg="orange", fg="blue", command=start_feed_likes)
button3 = tk.Button(fr_buttons, text="Поздравления с ДР", bg="purple", fg="white", command=start_birthday_fb)

label1 = tk.Label(fr_buttons,  text=f"Настройки бота\n")
label2 = tk.Label(fr_buttons,  text=f"\nФункции бота\n")
label3 = tk.Label(fr_buttons,  text=f"\n\nТекущая версия: {version}\nПоследняя версия: {upd_version}")
label4 = tk.Label(fr_buttons,  text=f"\n\nЭта программа написана для тестов\nбраузера на примере facebook.\nИспользуйте на свой страх и риск.\nАвтор не несет ответственности за\nущерб от данной программы.")

site_link = tk.Entry(fr_buttons)
label1.grid(row=0, column=0)
btn_open.grid(row=1, column=0, sticky="ew")
btn_save.grid(row=2, column=0, sticky="ew")

label2.grid(row=3, column=0)
fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky="nsew")

button1.grid(row=4, column=0)
button2.grid(row=5, column=0)
button3.grid(row=6, column=0)
label3.grid(row=7, column=0)
site_link.grid(row=8, column=0)
site_link.insert(0,'https://github.com/doevent/facebook-auto-liker')
label4.grid(row=9, column=0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument ('name', nargs='?')
    namespace = parser.parse_args()

    # запуск из командной строки
    if namespace.name == 'story':
        start_stories_fb()
    elif namespace.name == 'feed':
        start_feed_likes()
    elif namespace.name == 'birthday':
        start_birthday_fb()
    else:
        window.mainloop()

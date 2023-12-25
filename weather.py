import datetime
import requests
from config import token_weather


def get_forecast(token_weather):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        ans = ''
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?lat=57.1553&lon=65.5619&appid={token_weather}&units=metric"
        )
        data = r.json()

        # Получаем текущую дату
        current_date = datetime.datetime.now().date().strftime("%Y-%m-%d")

        # Функция для форматирования времени
        def get_time(item):
            return item['dt_txt']

        # Извлекаем прогноз на следующий день
        next_day_data = [item for item in data['list']]

        # Инициализируем переменную для отслеживания даты
        current_day = None

        # Создаем словарь для замены времени на "Утро", "День" и "Вечер"
        time_labels = {
            "12:00:00": "День"
        }

        for item in next_day_data:
            time = get_time(item).split()[-1]  # Получаем только время из даты
            main = item['weather'][0]['main']
            temp = round(item['main']['temp'])
            wind_speed = round(item['wind']['speed'])

            # Проверяем, если время в словаре временных меток, и используем его
            time_label = time_labels.get(time, "")

            # Проверяем, если день изменился, добавляем дату
            event_date = item['dt_txt'].split()[0]
            if event_date != current_day and time_label:
                current_day = event_date
                ans += f'{event_date}\n'


            # Выводим прогноз
            if time_label:

                ans += f"{time_label}: {code_to_smile.get(main, '')} {temp}°C ветер {wind_speed} м/с\n"

        return ans
    except Exception as e:
        print(f"Произошла ошибка: {e}")


# Вызываем функцию и передаем токен погоды
get_forecast(token_weather)

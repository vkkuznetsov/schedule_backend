import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

import psycopg
from datetime import datetime, timedelta


async def connect():
    connect_db = await psycopg.AsyncConnection.connect(
        "dbname=db1 user=postgres password=vik")
    return connect_db


async def insert_profile(profile_id, name, index=None):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                INSERT INTO profiles (profile_id, name, index) 
                VALUES (%s, %s, %s)
                ON CONFLICT (profile_id) 
                DO UPDATE SET name = EXCLUDED.name, index = EXCLUDED.index;
                '''
                await cursor.execute(sql, (profile_id, name, index))
    except Exception as e:
        print(e)


async def insert_names(name, index=None):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                INSERT INTO names (name, index) 
                VALUES (%s,%s);
                '''
                await cursor.execute(sql, (name, index))
    except Exception as e:
        print(e)


async def insert_many_table(name, event_id, index=None):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                INSERT INTO names_events(name, index, event_id)
                VALUES (%s,%s,%s)
                ON CONFLICT (name, index, event_id) DO NOTHING;
                '''
                await cursor.execute(sql, (name, index, event_id))
                await aconn.commit()
    except Exception as e:
        print(e)


async def insert_events(uid, start, end, name, location, instructions, event_type, subject_short):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                    INSERT INTO events(event_id, start_time, end_time, subject_name, location, instructors, event_type, subject_name_short)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO UPDATE
                    SET 
                        start_time = EXCLUDED.start_time,
                        end_time = EXCLUDED.end_time,
                        subject_name = EXCLUDED.subject_name,
                        location = EXCLUDED.location,
                        instructors = EXCLUDED.instructors,
                        event_type = EXCLUDED.event_type,
                        subject_name_short = EXCLUDED.subject_name_short;
                '''
                await cursor.execute(sql, (uid, start, end, name, location, instructions, event_type, subject_short))
                await aconn.commit()
    except Exception as e:
        print(e)


async def reset_database():
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                delete from names_events;
                delete from events;
                delete from profiles;
                delete from names;
                '''
                await cursor.execute(sql)
                await aconn.commit()
    except Exception as e:
        print(e)


async def reset_user_info(user_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                # Список запросов для удаления информации о пользователе
                sql = '''
                    DELETE FROM profiles
                    WHERE profile_id = %s;
                    '''

                await cursor.execute(sql, (user_id,))
                await aconn.commit()

    except Exception as e:
        print(e)


async def reset_user_info_all_events(user_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                # Список запросов для удаления информации о пользователе
                sql_queries = [
                    '''
                    DELETE FROM names_events
                    WHERE (name, index) IN (
                        SELECT name, index
                        FROM profiles
                        WHERE profile_id = %s
                    );
                    ''',
                    '''
                    DELETE FROM events
                    WHERE event_id IN (
                        SELECT event_id
                        FROM names_events
                        WHERE (name, index) IN (
                            SELECT name, index
                            FROM profiles
                            WHERE profile_id = %s
                        )
                    );
                    ''',
                    '''
                    UPDATE profiles
                    SET name = NULL, index = NULL
                    WHERE profile_id = %s;
                    '''
                ]

                for query in sql_queries:
                    await cursor.execute(query, (user_id,))

                await aconn.commit()

    except Exception as e:
        print(e)


async def reset_user_name_all_events(name, index):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                # Список запросов для удаления информации о пользователе
                sql_queries = [
                    '''
                    DELETE FROM names_events
                    WHERE name = %s AND index = %s;
                    ''',
                    '''
                    DELETE FROM events
                    WHERE event_id IN (
                        SELECT event_id
                        FROM names_events
                        WHERE name = %s AND index = %s
                    );
                    '''
                ]

                for query in sql_queries:
                    await cursor.execute(query, (name, index))

                await aconn.commit()

    except Exception as e:
        print(e)


async def reset_name_certain(FIO, index):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                # Запрос для удаления конкретной записи из таблицы names
                sql = '''
                    DELETE FROM names
                    WHERE name = %s AND index = %s;
                    '''

                await cursor.execute(sql, (FIO, index))

                await aconn.commit()

    except Exception as e:
        print(e)


async def show_profile(user_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = 'SELECT * FROM profiles WHERE profiles.profile_id = %s;'
                await cursor.execute(sql, (user_id,))
                result = await cursor.fetchone()
                if result is not None:
                    profile_id, name, index, second_name, second_index = result
                    return profile_id, name, index, second_name, second_index
                else:
                    return 'No id', 'no name', 'no index', 'no second name', 'no second index'
    except Exception as e:
        print(e)


async def show_friends(user_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = 'SELECT * FROM friends WHERE friends.profile_id = %s;'
                await cursor.execute(sql, (user_id,))
                results = await cursor.fetchall()
                count = len(results)
                return results, count

    except Exception as e:
        print(e)


async def show_friend_by_index(user_id, friend_index):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = 'SELECT name, index FROM friends WHERE profile_id = %s LIMIT 1 OFFSET %s;'
                await cursor.execute(sql, (user_id, friend_index))
                result = await cursor.fetchone()
                name, index = result
                return name, index

    except Exception as e:
        print(e)


async def insert_friend(profile_id, name, index=None):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                INSERT INTO friends(profile_id, name, index)
                VALUES (%s,%s,%s)
                ON CONFLICT (profile_id, name, index) DO NOTHING;
                '''
                await cursor.execute(sql, (profile_id, name, index))
                await aconn.commit()
    except Exception as e:
        print(e)


async def delete_all_friends(profile_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                DELETE FROM friends
                WHERE profile_id = %s;
                '''
                await cursor.execute(sql, (profile_id,))
                await aconn.commit()
    except Exception as e:
        print(e)


day_names = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среда',
    'Thursday': 'Четверг',
    'Friday': 'Пятница',
    'Saturday': 'Суббота',
    'Sunday': 'Воскресенье',
}
start_pair_smiles = {
    '08:30': '1️⃣',
    '10:15': '2️⃣',
    '12:00': '3️⃣',
    '14:00': '4️⃣',
    '15:45': '5️⃣',
    '17:30': '6️⃣',
    '19:10': '7️⃣',
    '20:50': '8️⃣',
}
end_pair_smiles = {
    '10:00': '1️⃣',
    '11:45': '2️⃣',
    '13:30': '3️⃣',
    '15:30': '4️⃣',
    '17:15': '5️⃣',
    '19:00': '6️⃣',
    '20:40': '7️⃣',
    '22:50': '8️⃣',
}


async def format_event(result):
    tab = '   ' * 2
    current_day = None
    formatted_result = ""
    for event in result:
        event_date = event[0].date()
        if event_date != current_day:
            day_of_week = event_date.strftime("%A")
            date = event_date.strftime("%d.%m")
            day_of_week_ru = day_names.get(day_of_week)
            formatted_result += f"\n\n{tab}<strong><u>{day_of_week_ru} {date}</u></strong>\n"
            current_day = event_date
        location = f'🏘 {event[3]}\n'
        start_time = event[0].strftime("%H:%M")
        end_time = event[1].strftime("%H:%M")

        emoji_order = start_pair_smiles[start_time]

        # Определяем, является ли пара "двойной" на основе разницы во времени
        start_minutes = int(event[0].strftime("%H")) * 60 + int(event[0].strftime("%M"))
        end_minutes = int(event[1].strftime("%H")) * 60 + int(event[1].strftime("%M"))
        time_difference = end_minutes - start_minutes

        if time_difference > 90:
            emoji_order += f'-{end_pair_smiles[end_time]}'

        time = f'⏰ {start_time} - {end_time}'
        instructor = f'\n🧑‍🔬 {event[5]}'
        event_type = event[4]
        type_emoji = (
            '🟢' if event_type == "Лекционное занятие" else
            '🔵' if event_type == "Практическое занятие" else
            '🟠' if event_type == "Лабораторное занятие" else
            '🔴'
        )
        name_description = f"\n{type_emoji} <b>{event[6]}</b>\n{emoji_order} <b>{event[2]}</b>\n"
        formatted_event = name_description + location + time + instructor + "\n"
        formatted_result += formatted_event
    return formatted_result


async def show_events_this_week(user_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                current_date = datetime.now()
                current_week = current_date.isocalendar()[1]
                sql = """
                    SELECT e.start_time, e.end_time, e.subject_name, e.location, e.event_type, e.instructors, e.subject_name_short
                    FROM events e
                    JOIN names_events ne ON e.event_id = ne.event_id
                    JOIN names n ON ne.name = n.name AND ne.index = n.index
                    JOIN profiles p ON n.name = p.name AND n.index = p.index
                    WHERE p.profile_id = %s
                    AND EXTRACT(WEEK FROM e.start_time::date) = %s  -- Преобразование start_time в тип date перед извлечением недели
                    ORDER BY e.start_time;
                """
                await cursor.execute(sql, (user_id, current_week))
                result = await cursor.fetchall()

                if not result:
                    return "Нет доступных событий."

                formatted_result = await format_event(result)
                ans = 'Расписание на эту неделю'
                ans += formatted_result
                return ans

    except Exception as e:
        print(e)


async def show_events_today(user_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                today = datetime.now().date()
                sql = """
                    SELECT e.start_time, e.end_time, e.subject_name, e.location, e.event_type, e.instructors, e.subject_name_short
                    FROM events e
                    JOIN names_events ne ON e.event_id = ne.event_id
                    JOIN names n ON ne.name = n.name AND ne.index = n.index
                    JOIN profiles p ON n.name = p.name AND n.index = p.index
                    WHERE p.profile_id = %s
                    AND DATE(e.start_time)::date = %s
                    ORDER BY e.start_time;
                """

                await cursor.execute(sql, (user_id, today))
                result = await cursor.fetchall()

                if not result:
                    return "На сегодня нет активных пар!"

                formatted_result = await format_event(result)
                ans = 'Расписание на сегодня'
                ans += formatted_result
                return ans

    except Exception as e:
        print(e)


async def show_events_tomorrow(user_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                tomorrow = datetime.now().date() + timedelta(days=1)

                sql = """
                    SELECT e.start_time, e.end_time, e.subject_name, e.location, e.event_type, e.instructors, e.subject_name_short
                    FROM events e
                    JOIN names_events ne ON e.event_id = ne.event_id
                    JOIN names n ON ne.name = n.name AND ne.index = n.index
                    JOIN profiles p ON n.name = p.name AND n.index = p.index
                    WHERE p.profile_id = %s
                    AND DATE(e.start_time)::date = %s
                    ORDER BY e.start_time;
                """

                await cursor.execute(sql, (user_id, tomorrow))
                result = await cursor.fetchall()

                if not result:
                    return "На завтра нет активных пар!"

                formatted_result = await format_event(result)
                ans = 'Расписание на завтра'
                ans += formatted_result
                return ans

    except Exception as e:
        print(e)


async def show_events_next_week(user_id):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                current_date = datetime.now()
                current_week = current_date.isocalendar()[1]

                # Получаем данные для следующей недели, добавив 1 к текущей неделе
                next_week = current_week + 1

                sql = """
                    SELECT e.start_time, e.end_time, e.subject_name, e.location, e.event_type, e.instructors, e.subject_name_short
                    FROM events e
                    JOIN names_events ne ON e.event_id = ne.event_id
                    JOIN names n ON ne.name = n.name AND ne.index = n.index
                    JOIN profiles p ON n.name = p.name AND n.index = p.index
                    WHERE p.profile_id = %s
                    AND EXTRACT(WEEK FROM e.start_time) = %s  
                    ORDER BY e.start_time;
                """
                await cursor.execute(sql, (user_id, next_week))
                result = await cursor.fetchall()

                if not result:
                    return "Нет доступных событий."

                formatted_result = await format_event(result)
                ans = 'Расписание на следующую неделю'
                ans += formatted_result
                return ans

    except Exception as e:
        print(e)


# Для запросов друзей
async def show_events_this_week_friend(name, index):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                current_date = datetime.now()
                current_week = current_date.isocalendar()[1]
                sql = """
                    SELECT e.start_time, e.end_time, e.subject_name, e.location, e.event_type, e.instructors, e.subject_name_short
                    FROM events e
                    JOIN names_events ne ON e.event_id = ne.event_id
                    JOIN names n ON ne.name = n.name AND ne.index = n.index
                    WHERE n.name = %s AND n.index = %s
                    AND EXTRACT(WEEK FROM e.start_time::date) = %s
                    ORDER BY e.start_time;
                """
                await cursor.execute(sql, (name, index, current_week))
                result = await cursor.fetchall()

                if not result:
                    return "Нет доступных событий."

                formatted_result = await format_event(result)
                ans = 'Расписание на эту неделю'
                ans += formatted_result
                return ans

    except Exception as e:
        print(e)


async def show_events_today_friend(name, index):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                today = datetime.now().date()
                sql = """
                    SELECT e.start_time, e.end_time, e.subject_name, e.location, e.event_type, e.instructors, e.subject_name_short
                    FROM events e
                    JOIN names_events ne ON e.event_id = ne.event_id
                    JOIN names n ON ne.name = n.name AND ne.index = n.index
                    WHERE n.name = %s AND n.index = %s
                    AND DATE(e.start_time)::date = %s
                    ORDER BY e.start_time;
                """

                await cursor.execute(sql, (name, index, today))
                result = await cursor.fetchall()

                if not result:
                    return "На сегодня нет активных пар!"

                formatted_result = await format_event(result)
                ans = 'Расписание на сегодня'
                ans += formatted_result
                return ans

    except Exception as e:
        print(e)


async def show_events_tomorrow_friend(name, index):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                tomorrow = datetime.now().date() + timedelta(days=1)

                sql = """
                    SELECT e.start_time, e.end_time, e.subject_name, e.location, e.event_type, e.instructors, e.subject_name_short
                    FROM events e
                    JOIN names_events ne ON e.event_id = ne.event_id
                    JOIN names n ON ne.name = n.name AND ne.index = n.index
                    WHERE n.name = %s AND n.index = %s
                    AND DATE(e.start_time)::date = %s
                    ORDER BY e.start_time;
                """

                await cursor.execute(sql, (name, index, tomorrow))
                result = await cursor.fetchall()

                if not result:
                    return "На завтра нет активных пар!"

                formatted_result = await format_event(result)
                ans = 'Расписание на завтра'
                ans += formatted_result
                return ans

    except Exception as e:
        print(e)


async def show_events_next_week_friend(name, index):
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                current_date = datetime.now()
                current_week = current_date.isocalendar()[1]

                # Получаем данные для следующей недели, добавив 1 к текущей неделе
                next_week = current_week + 1

                sql = """
                    SELECT e.start_time, e.end_time, e.subject_name, e.location, e.event_type, e.instructors, e.subject_name_short
                    FROM events e
                    JOIN names_events ne ON e.event_id = ne.event_id
                    JOIN names n ON ne.name = n.name AND ne.index = n.index
                    WHERE n.name = %s AND n.index = %s
                    AND EXTRACT(WEEK FROM e.start_time) = %s  -- Выбор событий для следующей недели
                    ORDER BY e.start_time;
                """
                await cursor.execute(sql, (name, index, next_week))
                result = await cursor.fetchall()

                if not result:
                    return "Нет доступных событий."

                formatted_result = await format_event(result)
                ans = 'Расписание на следующую неделю'
                ans += formatted_result
                return ans

    except Exception as e:
        print(e)



async def get_all_names():
    try:
        async with await connect() as aconn:
            async with aconn.cursor() as cursor:
                sql = '''
                SELECT * FROM names;
                '''
                await cursor.execute(sql)
                result = await cursor.fetchall()
                print(result)
    except Exception as e:
        print(e)
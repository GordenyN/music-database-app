import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Подключение к базе данных
conn = sqlite3.connect("MUSIC5.db")
cursor = conn.cursor()

# Получение данных для связанных таблиц с фильтрацией
def get_options(table, column="name", filter_condition=None):
    query = f"SELECT id, {column} FROM {table} ORDER BY {column}"
    if filter_condition:
        query = f"SELECT id, {column} FROM {table} WHERE {filter_condition} ORDER BY {column}"
    cursor.execute(query)
    return cursor.fetchall()

# Обновление значений в выпадающем списке
def update_combobox(combobox, table, column, filter_condition=None):
    values = get_options(table, column, filter_condition)
    combobox['values'] = [v[1] for v in values]

# Открытие формы для добавления нового значения
def open_add_form(input_window, table, column, combobox_to_update, extra_fields=None, column_description=None):
    add_window = tk.Toplevel(input_window)
    add_window.title(f"Добавить {table}")
    add_window.geometry("400x400")

    # Показываем описание для столбца, если оно передано
    if column_description:
        tk.Label(add_window, text=column_description).pack(pady=10)
    else:
        tk.Label(add_window, text=f"Введите {column}:").pack(pady=10)

    new_value_entry = tk.Entry(add_window)
    new_value_entry.pack(pady=5)

    extra_entries = {}
    if extra_fields:
        for field, label in extra_fields.items():
            tk.Label(add_window, text=label).pack(pady=5)
            entry = tk.Entry(add_window)
            entry.pack(pady=5)
            extra_entries[field] = entry

    def save_new_value():
        new_value = new_value_entry.get()
        extra_values = {field: entry.get() for field, entry in extra_entries.items()}
        
        if new_value:
            columns = [column] + list(extra_values.keys())
            values = [new_value] + list(extra_values.values())
            placeholders = ', '.join(['?' for _ in values])
            cursor.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", values)
            conn.commit()
            messagebox.showinfo("Успех", f"{table} добавлен успешно!")
            update_combobox(combobox_to_update, table, column)
            add_window.destroy()
        else:
            messagebox.showwarning("Ошибка", "Введите данные")

    save_button = tk.Button(add_window, text="Сохранить", command=save_new_value)
    save_button.pack(pady=10)

# Форма ввода данных
def open_input_form():
    input_window = tk.Toplevel(root)
    input_window.title("Ввод и редактирование данных в таблицу Sounds")
    input_window.geometry("600x800")

    fields_frame = tk.Frame(input_window)
    fields_frame.pack(pady=10)

    # Название произведения
    tk.Label(fields_frame, text="Название произведения:").pack(pady=5)
    title_entry = tk.Entry(fields_frame)
    title_entry.pack(pady=5)

    # Жанр
    tk.Label(fields_frame, text="Жанр:").pack(pady=5)
    genre_combobox = ttk.Combobox(fields_frame, values=[g[1] for g in get_options("Genres", "Name")])
    genre_combobox.pack(pady=5)
    tk.Button(fields_frame, text="Добавить жанр", command=lambda: open_add_form(input_window, "Genres", "Name", genre_combobox, {"Description": "Описание жанра"}, "Описание жанра (text) от 1 до 50 символов")).pack(pady=5)

    # Исполнитель
    tk.Label(fields_frame, text="Исполнитель:").pack(pady=5)
    artist_combobox = ttk.Combobox(fields_frame, values=[a[1] for a in get_options("Composers_Artists", "Name")])
    artist_combobox.pack(pady=5)

    

    # Добавление нового исполнителя с привязкой к стране
    tk.Button(fields_frame, text="Добавить исполнителя", command=lambda: open_add_form(input_window, "Composers_Artists", "Name", artist_combobox, {"birth_date": "Дата рождения", "country_id": "Страна"}, "Исполнитель (text). От 1 до 100 символов")).pack(pady=5)

    # Страна
    tk.Label(fields_frame, text="Страна:").pack(pady=5)
    country_combobox = ttk.Combobox(fields_frame, values=[])
    country_combobox.pack(pady=5)

    def update_country_options(event):
        artist_name = artist_combobox.get()
        if artist_name:
            filter_condition = f"id IN (SELECT country_id FROM Composers_Artists WHERE name='{artist_name}')"
            update_combobox(country_combobox, "Country", "Name", filter_condition)

    artist_combobox.bind("<<ComboboxSelected>>", update_country_options)

    # Год выпуска
    tk.Label(fields_frame, text="Год выпуска (YYYY):").pack(pady=5)
    year_entry = tk.Entry(fields_frame)
    year_entry.pack(pady=5)

    # Альбом
    tk.Label(fields_frame, text="Альбом:").pack(pady=5)
    album_combobox = ttk.Combobox(fields_frame, values=[a[1] for a in get_options("Albums", "title")])
    album_combobox.pack(pady=5)
    tk.Button(fields_frame, text="Добавить альбом", command=lambda: open_add_form(input_window, "Albums", "title", album_combobox, {"release_date": "Дата выхода"}, "Название альбома (text) от 1 до 50 символов")).pack(pady=5)

    # Концертный зал
    tk.Label(fields_frame, text="Концертный зал:").pack(pady=5)
    hall_combobox = ttk.Combobox(fields_frame, values=[h[1] for h in get_options("Concert_Halls", "Name")])
    hall_combobox.pack(pady=5)
    tk.Button(fields_frame, text="Добавить концертный зал", command=lambda: open_add_form(input_window, "Concert_Halls", "Name", hall_combobox, {"location": "Местоположение", "capacity": "Вместимость"}, "Концертный зал")).pack(pady=5)



# Функция для сохранения данных
    def save_data():
        title = title_entry.get()
        genre = genre_combobox.get()
        artist = artist_combobox.get()
        country = country_combobox.get()
        year = year_entry.get()
        album = album_combobox.get()
        hall = hall_combobox.get()

        if not title or not genre or not artist or not year or not album or not hall:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        try:
            cursor.execute(
                "INSERT INTO Songs (title, genre_id, composer_artist_id, country_id, release_date, albums_id, concert_halls_id) "
                "VALUES (?, (SELECT id FROM Genres WHERE Name=?), "
                "(SELECT id FROM Composers_Artists WHERE Name=?), "
                "(SELECT id FROM Country WHERE Name=?), ?, "
                "(SELECT id FROM Albums WHERE title=?), "
                "(SELECT id FROM Concert_Halls WHERE Name=?))",
                (title, genre, artist, country, year, album, hall)
            )
            conn.commit()
            messagebox.showinfo("Успех", "Данные успешно сохранены!")
            input_window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {e}")

    # Кнопка "Сохранить"
    save_button = tk.Button(input_window, text="Сохранить", command=save_data)
    save_button.pack(pady=10)



# Форма получения агрегированных данных
def open_stats_form():
    stats_window = tk.Toplevel(root)
    stats_window.title("Статистика")
    stats_window.geometry("300x200")

    cursor.execute("SELECT g.name, COUNT(*) FROM Songs s JOIN Genres g ON s.genre_id = g.id GROUP BY g.name")
    results = cursor.fetchall()

    stats_list = tk.Listbox(stats_window, width=50)
    stats_list.pack(pady=10)

    if results:
        for row in results:
            stats_list.insert(tk.END, f"{row[0]}: {row[1]} песен")
    else:
        stats_list.insert(tk.END, "Нет данных")

# Форма сведений о БД
def open_info_form():
    info_window = tk.Toplevel(root)
    info_window.title("Сведения о БД")
    info_window.geometry("300x150")

    tk.Label(info_window, text="Разработчик: Гордионок Наталья Игоревна").pack()
    tk.Label(info_window, text="База данных: MUSIC.db").pack()
    tk.Label(info_window, text="Описание: Хранение информации о песнях").pack()

# Выход из приложения
def exit_app():
    conn.close()
    root.destroy()


def open_search_form():
    search_window = tk.Toplevel(root)
    search_window.title("Поиск данных")
    search_window.geometry("300x200")
    
    tk.Label(search_window, text="Функция поиска еще не реализована").pack(pady=20)
    
# Создание главного окна
root = tk.Tk()
root.title("Музыкальная база данных")
root.geometry("400x350")

# Заголовок
label = tk.Label(root, text="Музыкальная база данных", font=("Arial", 12))
label.pack(pady=10)



# Кнопки
btn_input = tk.Button(root, text="Ввод и редактирование данных", command=open_input_form)
btn_input.pack(fill="x", padx=20, pady=5)

btn_stats = tk.Button(root, text="Получение агрегированных данных", command=open_stats_form)
btn_stats.pack(fill="x", padx=20, pady=5)

btn_info = tk.Button(root, text="Сведения о БД", command=open_info_form)
btn_info.pack(fill="x", padx=20, pady=5)

btn_exit = tk.Button(root, text="Выход", command=exit_app)
btn_exit.pack(fill="x", padx=20, pady=5)

# Запуск окна
root.mainloop()




















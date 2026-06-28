import sqlite3

# 1. Создаём базу в памяти и таблицы
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

# 2. Заполняем данными
cursor.executemany(
    "INSERT INTO users (id, name, email, created_at) VALUES (?, ?, ?, ?)",
    [
        (1, "Анна", "anna@mail.ru", "2026-06-01"),
        (2, "Борис", "boris@mail.ru", "2026-06-10"),
        (3, "Вика", "vika@mail.ru", "2026-06-15"),
        (4, "Глеб", "gleb@mail.ru", "2026-06-20"),
        (5, "Диана", "diana@mail.ru", "2026-06-25"),
    ],
)

cursor.executemany(
    "INSERT INTO orders (id, user_id, amount, status) VALUES (?, ?, ?, ?)",
    [
        (1, 1, 1500.00, "delivered"),
        (2, 1, 500.00, "cancelled"),
        (3, 2, 3000.00, "delivered"),
        (4, 3, 750.00, "pending"),
        (5, 2, 2000.00, "delivered"),
        (6, 5, 1200.00, "pending"),
    ],
)

print("=" * 50)
print("1. Все пользователи:")
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

print("\n" + "=" * 50)
print("2. Пользователи с суммой заказов (JOIN + GROUP BY):")
cursor.execute("""
SELECT u.name, SUM(o.amount) AS total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id
ORDER BY total_spent DESC
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} руб.")

print("\n" + "=" * 50)
print("3. Пользователи БЕЗ заказов (LEFT JOIN + WHERE IS NULL):")
cursor.execute("""
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL
""")
for row in cursor.fetchall():
    print(row[0])

print("\n" + "=" * 50)
print("4. Только delivered-заказы с суммой больше 1000:")
cursor.execute("""
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'delivered' AND o.amount > 1000
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} руб.")

print("\n" + "=" * 50)
print("5. Количество заказов по статусам:")
cursor.execute("""
SELECT status, COUNT(*) AS count
FROM orders
GROUP BY status
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

print("\n" + "=" * 50)
print("6. Дубликаты email (если есть):")
cursor.execute("""
SELECT email, COUNT(*)
FROM users
GROUP BY email
HAVING COUNT(*) > 1
""")
duplicates = cursor.fetchall()
if duplicates:
    for row in duplicates:
        print(f"Дубликат: {row[0]} ({row[1]} раз)")
else:
    print("Дубликатов нет")

conn.close()

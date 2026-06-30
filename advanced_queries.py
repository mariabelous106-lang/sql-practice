import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
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

cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", [
    (1, "Анна", "anna@mail.ru"),
    (2, "Борис", "boris@mail.ru"),
    (3, "Вика", "vika@mail.ru"),
])
cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", [
    (1, 1, 1000, "paid"),
    (2, 1, 500, "cancelled"),
    (3, 2, 2000, "paid"),
])

print("=" * 50)
print("1. Подзапрос: пользователи с суммой заказов > 1000")
cursor.execute("""
SELECT name
FROM users
WHERE id IN (
    SELECT user_id
    FROM orders
    GROUP BY user_id
    HAVING SUM(amount) > 1000
)
""")
for row in cursor.fetchall():
    print(row[0])

print("\n" + "=" * 50)
print("2. UNION: все имена пользователей + статусы заказов")
cursor.execute("""
SELECT name AS value FROM users
UNION
SELECT status AS value FROM orders
""")
for row in cursor.fetchall():
    print(row[0])

print("\n" + "=" * 50)
print("3. Транзакция с откатом (ROLLBACK)")
try:
    cursor.execute("BEGIN")
    cursor.execute("INSERT INTO users VALUES (4, 'Дима', 'dima@mail.ru')")
    cursor.execute("INSERT INTO orders VALUES (4, 4, 1500, 'new')")
    conn.commit()
    print("Транзакция успешна: Дима и его заказ добавлены")
except Exception as e:
    conn.rollback()
    print(f"Ошибка, откат: {e}")

print("\n" + "=" * 50)
print("4. Проверяем, что Дима в БД")
cursor.execute("SELECT * FROM users WHERE name = 'Дима'")
result = cursor.fetchone()
print("Дима в БД" if result else "Димы нет")

print("\n" + "=" * 50)
print("5. Пример ошибки и отката")
try:
    cursor.execute("BEGIN")
    cursor.execute("INSERT INTO users VALUES (5, 'Ева', 'eva@mail.ru')")
    cursor.execute("INSERT INTO orders VALUES (5, 999, 100, 'new')")
    conn.commit()
    print("Транзакция успешна")
except Exception as e:
    conn.rollback()
    print(f"Откат: {e}")

print("\n" + "=" * 50)
print("6. Проверяем: Евы быть не должно")
cursor.execute("SELECT * FROM users WHERE name = 'Ева'")
result = cursor.fetchone()
print("Ева в БД" if result else "Евы нет (откат сработал)")

conn.close()

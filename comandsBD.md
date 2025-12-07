-- ВСЕ КОМАНДЫ ДЛЯ БАЗЫ ДАННЫХ
-- Посмотреть все таблицы: \dt
-- Посмотреть структуру таблицы: \d users
-- Посмотреть все базы данных: \l
-- Посмотреть всех пользователей: \du
-- Выйти из psql: \q

-- ПОЛЬЗОВАТЕЛИ (таблица users)
SELECT * FROM users;
SELECT COUNT(*) FROM users;
SELECT * FROM users WHERE user_id = 123456789;
SELECT * FROM users ORDER BY created_at DESC;
DELETE FROM users WHERE user_id = 123456789;

-- СООБЩЕНИЯ (таблица messages)
SELECT * FROM messages;
SELECT COUNT(*) FROM messages;
SELECT * FROM messages WHERE user_id = 123456789;
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
DELETE FROM messages WHERE id = 1;

-- ЛЮДИ (таблица people)
SELECT * FROM people;
INSERT INTO people (name, description) VALUES ('Имя', 'Описание');
SELECT * FROM people WHERE id = 1;
UPDATE people SET name = 'Новое имя' WHERE id = 1;
DELETE FROM people WHERE id = 1;
SELECT COUNT(*) FROM people;

-- ДОБАВЛЕНИЕ ДАННЫХ
INSERT INTO users (user_id, username, first_name) VALUES (123456789, 'user', 'Имя');
INSERT INTO messages (user_id, message_text) VALUES (123456789, 'текст');
INSERT INTO people (name, description) VALUES ('Имя', 'Описание человека');

-- ОБНОВЛЕНИЕ ДАННЫХ
UPDATE users SET first_name = 'Новое имя' WHERE user_id = 123456789;
UPDATE people SET description = 'Новое описание' WHERE id = 1;

-- УДАЛЕНИЕ ДАННЫХ
DELETE FROM users WHERE user_id = 123456789;
DELETE FROM messages WHERE id = 1;
DELETE FROM people WHERE id = 1;

-- ПОИСК
SELECT * FROM users WHERE username LIKE '%test%';
SELECT * FROM messages WHERE message_text LIKE '%привет%';
SELECT * FROM people WHERE name LIKE '%Иван%';

-- СТАТИСТИКА
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_messages FROM messages;
SELECT COUNT(*) as total_people FROM people;
SELECT user_id, COUNT(*) FROM messages GROUP BY user_id ORDER BY count DESC;
SELECT DATE(created_at) as date, COUNT(*) FROM messages GROUP BY DATE(created_at);

-- ОЧИСТКА
DELETE FROM messages;
DELETE FROM users;
DELETE FROM people;
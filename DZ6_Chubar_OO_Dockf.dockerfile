# Використовуємо образ Python
FROM python:3.10-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо вміст поточної директорії у контейнер
COPY . /app

# Встановлюємо залежності
RUN pip install pymongo

# Відкриваємо порти
EXPOSE 3000
EXPOSE 5000

ENV NAME World

# Запускаємо Python-скрипт
CMD ["python", "DZ6_Chubar_OO_Pyth.py"]


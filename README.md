![example workflow](https://github.com/32aleksey32/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# foodgram-project-react - Дипломный проект в Яндекс.Практикум
## Спринт 17 - Продуктовый помощник Foodgram

### Ip сервера:
- 51.250.97.124

### Описание проекта:
«Продуктовый помощник»: приложение, в котором пользователи могут публиковать рецепты,
подписываться на публикации других авторов и добавлять понравившиеся рецепты в избранное.
Вкладка «список покупок» позволит пользователю создать список продуктов,
которые необходимо купить для приготовления выбранных блюд.

### Стек технологий использованный в проекте:
- Python 3.7
- Django 2.2.16
- Django Rest Framework
- Docker
- PostgreSQL

### Как установить проект:
- Клонируйте репозиторий с проектом на свой компьютер:
    ```
    git clone https://github.com/32Aleksey32/foodgram-project-react.git
    ```
- Локально отредактируйте файл infra/nginx.conf, обязательно в строке server_name вписать IP-адрес сервера

- Скопируйте файлы `docker-compose.yml`, `default.conf` и `.env` из директории infra на сервер:
  ```bash
  scp .\infra\docker-compose.yaml <username>@<host>:/home/<username>/docker-compose.yaml
  scp .\infra\nginx.conf <username>@<host>:/home/<username>/nginx.conf
  scp .\infra\.env <username>@<host>:/home/<username>/.env
  ```

- Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
  ```
  - DOCKER_USERNAME=<логин от аккаунта на Docker Hub>
  - DOCKER_PASSWORD=<пароль от аккаунта на Docker Hub>

  - HOST=<публичный адрес сервера для доступа по SSH>
  - USER=<username для подключения к серверу> 
  - SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>
  - PASSPHRASE=<пароль для сервера, если он установлен>

  - DB_ENGINE=<django.db.backends.postgresql>
  - DB_NAME=<имя базы данных postgres>
  - DB_POSTGRES_USER=<пользователь бд>
  - DB_POSTGRES_PASSWORD=<пароль>
  - DB_HOST=<db>
  - DB_PORT=<5432>

  - TELEGRAM_TOKEN=<токен вашего бота>. Получить этот токен можно у бота @BotFather
  - TELEGRAM_ID=<ID чата, в который придет сообщение>. Узнать свой ID можно у бота @userinfobot
  ```
  Workflow состоит из четырёх шагов:
    - `tests`: установка зависимостей, запуск flake8 и pytest
    - `build_and_push_to_docker_hub`: создание образов foodgram_backend и foodgram-frontend и загрузка их в свой репозиторий на DockerHub
    - `deploy`: развертывание проекта на удаленном сервере
    - `send_message`: отправка сообщения в чат Telegram при успешном выполнении workflow в GitHub Actions

#### Инструкции для развертывания и запуска приложения
- Зайдите на удаленный сервер
- Установите docker 
  ```bash
  sudo apt install docker.io
  ```
- Установите docker-compose на сервер:
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```
- Чтобы проверить, прошла ли установка успешно, выполните следующую команду:
  ```bash
  sudo docker-compose --version
  ```

- Соберите и запустите контейнеры на сервере:
  ```bash
  sudo docker-compose up -d --build
  ```

- После успешной сборки выполните следующие действия (только при первом деплое):
    * проведите миграции внутри контейнеров:
      ```bash
      sudo docker-compose exec backend python manage.py makemigrations
      sudo docker-compose exec backend python manage.py migrate
      ```
    * заполните базу данных ингредиентами:
      ```bash
      sudo docker-compose exec backend python manage.py load_ingredients
      ```  
    * соберите статику проекта:
      ```bash
      sudo docker-compose exec backend python manage.py collectstatic --no-input
      ```  
    * создайте суперпользователя Django:
      ```bash
      sudo docker-compose exec backend python manage.py createsuperuser
      ```

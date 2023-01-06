# universal_flash_cards_chatbotsource .v    

[piccolo-orm documentation](https://piccolo-orm.com/)

---

[docker documentation](https://docs.docker.com/engine/reference/commandline/volume_rm/)

---

### Робота з БД під час розробки

Додано ще один сервіс у компоуз-файлі з тулзою для зручної роботи з БД
Додавання цього сервісу (pgadmin) зроблено з окремим профілем dev - [почитати про це можна тут](https://docs.docker.com/compose/profiles/) - тому модель використання така:
- при локальному запуску у своєму середовищі dev всі команди docker-compose використовуються з профілем dev:
```CLI
docker-compose --profile dev rm -sf
docker-compose --profile dev create --build
docker-compose --profile dev up -d
. . .
```

Після цього на локальному браузері за адресою 127.0.0.1:5050 відкриється pgAdmin
щоб зайти - логін і пароль за замовченням в рядках 51 та 52 docker-compose.yaml
Підключення до БД (якщо ви не змінювали налаштувань для локального варіанта) - точно таке як і для БД на продакшені (але БД буде створена нова, створивши локально volumes)

---


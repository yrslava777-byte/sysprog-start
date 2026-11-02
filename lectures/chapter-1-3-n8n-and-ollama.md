# 1.3 n8n и Ollama: первая автоматизация

Глава справочника: [https://maximbytecamp.github.io/sysprog_makarov/temy/08-n8n-i-ollama/index.html](https://maximbytecamp.github.io/sysprog_makarov/temy/08-n8n-i-ollama/index.html)

## Разделы

1. Задача главы
2. Шаг 1. Установить Ollama и скачать модель
3. Шаг 2. Запустить n8n
4. Шаг 3. Принять сообщение: узел Webhook
5. Шаг 4. Отправить сообщение из brain.py
6. Шаг 5. Добавить пояснение модели
7. Шаг 6. Отправить письмо
8. Шаг 7. Опубликовать сценарий
9. Шаг 8. Сохранить работу в репозитории

## Шпаргалка

| Что | Как |
|---|---|
| Программы | `ollama pull qwen2.5:3b`; `npx n8n` → `localhost:5678`; Node.js 20.19–24.x |
| Сценарий | Webhook: POST, path `agent`; Basic LLM Chain + Ollama Chat Model; Send Email по SMTP |
| Отправка | `python3 brain.py адрес`; тест: `/webhook-test/agent`; боевой: `/webhook/agent` |
| Выражения | `{{ $json.body }}`; `{{ $('Webhook').item.json.body }}` |
| Проверка | вкладка Executions; ответ модели сверять с JSON |

## Итог главы

Сообщение агента доставляется по цепочке из трёх узлов n8n. `brain.py` отправляет JSON запросом POST на вебхук модулем `urllib.request`. Узел Webhook принимает его, Basic LLM Chain с моделью `qwen2.5:3b` в Ollama пишет пояснение, Send an Email отправляет письмо с пояснением и исходным сообщением. Пока сценарий собирается, используется тестовый адрес и кнопки в редакторе. После публикации работает боевой адрес, а каждый запуск записывается во вкладку Executions. Модель работает на своём компьютере, но ошибается в смысле чисел, поэтому её ответ отправляется вместе с данными агента.

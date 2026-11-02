# 1.2 C и Python вместе: библиотека и ctypes

Глава справочника: [https://maximbytecamp.github.io/sysprog_makarov/temy/07-c-i-python-vmeste/index.html](https://maximbytecamp.github.io/sysprog_makarov/temy/07-c-i-python-vmeste/index.html)

## Разделы

1. Задача главы
2. Шаг 1. Собрать библиотеку
3. Шаг 2. Проверить таблицу экспорта
4. Шаг 3. Загрузить библиотеку
5. Шаг 4. Описать структуру в Python
6. Шаг 5. Вызвать функцию ядра
7. Шаг 6. Поменять поля местами
8. Шаг 7. Передать пустой адрес
9. Шаг 8. Собрать brain.py
10. Запрос к помощнику ИИ

## Шпаргалка

| Что | Как |
|---|---|
| Библиотека | (Windows: `cl /LD core_info.c /Fe:sentry_core.dll`); (macOS: `clang -shared -fPIC -o libsentry_core.dylib core_info.c`); (Linux: `gcc -shared -fPIC -o libsentry_core.so core_info.c`); в Windows — `CORE_API` |
| Экспорт | (Windows: `dumpbin /exports sentry_core.dll`); (macOS: `nm -gU libsentry_core.dylib`); (Linux: `nm -D --defined-only libsentry_core.so`) |
| Загрузка | `core = ctypes.CDLL(str(путь))`; архитектура Python = архитектура библиотеки |
| Структура | `class CoreInfo(ctypes.Structure)`; `_fields_` в порядке `core.h`; `ctypes.sizeof` = 272 |
| Вызов | `argtypes = [ctypes.POINTER(CoreInfo)]`; `restype = ctypes.c_int`; `core.core_get_info(ctypes.byref(info))` |
| Ошибка | код ≠ 0 → `raise OSError(код, текст)`; `None` = `NULL` |

## Итог главы

Ядро агента собрано в динамическую библиотеку из того же `core_info.c`. В Windows функция отмечена `__declspec(dllexport)` через макрос `CORE_API`, в macOS и Linux она экспортируется без отметки, и таблица экспорта это показывает. Python загружает библиотеку модулем `ctypes` в свой процесс, поэтому архитектура библиотеки и Python должна совпадать. Структура описана классом с `_fields_`, типы параметров — в `argtypes` и `restype`, адрес передаётся через `byref`. Описание в Python ничем не сверяется с `core.h`: переставленные поля дали неверные числа без ошибки, поэтому размер и смещения проверяются запуском. Пустой адрес ядро отклоняет кодом ошибки, и `brain.py` превращает этот код в `OSError`. Итог — `brain.py`, который печатает сообщение `agent_started` в JSON.

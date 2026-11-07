# 2.1 Список процессов

Глава справочника: [https://maximbytecamp.github.io/sysprog_makarov/temy/14-spisok-processov/index.html](https://maximbytecamp.github.io/sysprog_makarov/temy/14-spisok-processov/index.html)

## Разделы

1. Задача главы
2. Шаг 1. Описать процесс в core.h
3. Шаг 2. Написать core_procs.c
4. Шаг 3. Проверить ядро программой на C
5. Шаг 4. Сверить с программой системы
6. Шаг 5. Дать ядру мало места
7. Шаг 6. Вызвать список из Python
8. Шаг 7. Отправить в репозиторий
9. Запрос к помощнику ИИ

## Шпаргалка

| Что | Как |
|---|---|
| Строка списка | `struct core_proc`: `pid`, `ppid`, `name[64]`; 80 байт |
| Договор | `core_list_procs(out, max, &count)`; не больше `max` строк, в `count` — сколько найдено |
| Мест мало | (Windows: 122 `ERROR_INSUFFICIENT_BUFFER`); (macOS и Linux: 34 `ERANGE`); повторить с `count` + запас |
| Источник | (Windows: `CreateToolhelp32Snapshot` + `Process32NextW`); (macOS: `proc_listallpids` + `proc_pidinfo`); (Linux: `/proc` + `/proc/N/stat`) |
| Сверка | (Windows: `tasklist`); (macOS и Linux: `ps -A`); близко, но не точно |
| Мозг | `list_procs()` — список словарей; `parents(procs, os.getpid())` — цепочка |

## Итог главы

Ядро агента получило функцию `core_list_procs`: она заполняет массив строками «номер, родитель, имя» по 80 байт и пишет в `count`, сколько процессов нашла. Windows отдаёт список снимком Tool Help, macOS — номерами из `proc_listallpids` и сведениями `proc_pidinfo`, Linux — папками `/proc` и файлами `stat`. Наружу функция на всех системах отдаёт одно и то же. Программа `list_procs.c` показала три вещи. Ядро находит само себя с верным родителем. Число процессов близко к числу системной программы. При 10 местах приходит код (Windows: 122) (macOS и Linux: 34) и число нужных мест. Мозг агента повторяет вызов с нужным местом и по номерам родителей строит цепочку от `brain.py` вверх до процесса, с которого начинается система.

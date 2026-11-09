# 2.2 Запуск процесса

Глава справочника: [https://maximbytecamp.github.io/sysprog_makarov/temy/16-zapusk-processa/index.html](https://maximbytecamp.github.io/sysprog_makarov/temy/16-zapusk-processa/index.html)

## Разделы

1. Задача главы
2. Шаг 1. Описать запущенный процесс в core.h
3. Шаг 2. Написать core_spawn.c
4. Шаг 3. Проверить ядро программой на C
5. Шаг 4. Время вышло и программы нет
6. Шаг 5. Запустить процесс из Python
7. Шаг 6. Отправить в репозиторий
8. Запрос к помощнику ИИ

## Шпаргалка

| Что | Как |
|---|---|
| Запущенный процесс | `struct core_child`: `pid`, `handle`; 16 байт |
| Запуск | `core_spawn(argv, &child)`; (Windows: `CreateProcessW`, поток закрыть сразу); (macOS и Linux: `posix_spawnp`) |
| Ожидание | `core_wait(&child, ms, &code)`; (Windows: `WaitForSingleObject` + `GetExitCodeProcess`); (macOS и Linux: `waitpid` с `WNOHANG`) |
| Коды | нет программы — 2; время вышло — (Windows: 258) (macOS: 60) (Linux: 110) |
| Мозг | `spawn([…])` — процесс; `wait(child, 5000)` — код |
| Утечка | запуск без ожидания; (Windows: открытые дескрипторы); (macOS и Linux: зомби) |

## Итог главы

Ядро агента получило две функции. `core_spawn` запускает программу по списку аргументов: в Windows — `CreateProcessW` по командной строке, склеенной из списка, в macOS и Linux — `posix_spawnp`. `core_wait` ждёт ребёнка с пределом времени и возвращает его код: в Windows через дескриптор процесса, в macOS и Linux через `waitpid`. Программа `run_child.c` показала три исхода: код 7, «время вышло» с кодом (Windows: 258) (macOS: 60) (Linux: 110) и «программы нет» с кодом 2. Мозг запустил второй Python, увидел его своим ребёнком в списке процессов и получил код 3. Программа `leak.c` показала, что запуск без ожидания оставляет в системе след: (Windows: 20 дескрипторов процессов, а без `CloseHandle(pi.hThread)` — ещё 20 дескрипторов потоков) (macOS и Linux: 20 зомби).

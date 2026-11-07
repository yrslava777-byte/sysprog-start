"""Проверки репозитория по дисциплине «Системное программирование».

Запускается в GitHub Actions на трёх системах (Windows, macOS, Linux) после каждой
отправки кода и локально командой: python checks/run_checks.py

Что проверяется:
1. Лабораторные работы, у которых есть код: программа собирается и печатает
   ожидаемую строку. Код для другой системы пропускается (hello.c с windows.h
   собирается только в Windows, с unistd.h — только в macOS и Linux).
   Снимки экрана лабораторных: заглушки в screenshots/ заменены своими снимками.
2. Проверки агента-сторожа. Каждая открывается на своей паре; до этого она
   отмечена как «ещё не открыта» и на результат не влияет.

Файл ведёт преподаватель: при обновлении материалов он заменяется новой версией.
"""
import os
import platform
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYSTEM = {"Windows": "win", "Darwin": "mac", "Linux": "linux"}[platform.system()]
SYSTEM_NAME = {"win": "Windows", "mac": "macOS", "linux": "Linux"}[SYSTEM]

# Проверки агента: номер, пара, на которой открывается, название.
AGENT_CHECKS = [
    (1, 4, "Список процессов совпадает с системным"),
    (2, 6, "Процесс загружает процессор больше 80%"),
    (3, 8, "Память процесса растёт без остановки"),
    (4, 10, "Изменён файл hosts"),
    (5, 11, "Новый файл в папке автозагрузки пользователя"),
    (6, 12, "Новая запись в системной автозагрузке"),
    (7, 13, "Пять неудачных входов подряд"),
    (8, 14, "Открыт новый порт"),
    (9, 15, "Модель ИИ занимает больше заданной памяти"),
    (10, 18, "В отправленных данных нет имени пользователя"),
    (11, 20, "Ядро работает в фоне и отвечает"),
    (12, 21, "Подключено новое устройство"),
    (13, 22, "Запущена программа без подписи или не из пакета"),
]
OPENED = 0  # сколько проверок агента уже открыто; растёт с каждой парой

PID_LINE = re.compile(r"agent v0(?: \(python\))?, pid= ?\d+")


def target_of_c(text):
    return "win" if "windows.h" in text else "posix"


def target_of_py(text):
    return "win" if "windll" in text else "posix"


def fits(target):
    return target == "win" if SYSTEM == "win" else target == "posix"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60, **kw)


def build_c(src, out_dir):
    exe = Path(out_dir) / ("hello.exe" if SYSTEM == "win" else "hello")
    if SYSTEM == "win":
        r = run(["cl", "/nologo", str(src), f"/Fe:{exe}", f"/Fo:{out_dir}\\"])
    else:
        cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
        r = run([cc, "-o", str(exe), str(src)])
    return exe, r


def check_lab01():
    rows = []
    lab = ROOT / "labs" / "01-process-inside"
    c, py = lab / "hello.c", lab / "hello.py"
    if not c.exists() and not py.exists():
        return [("ЛР 1", "hello.c, hello.py", "не сдано", "")], True
    ok = True
    if c.exists():
        text = c.read_text(encoding="utf-8", errors="replace")
        if not fits(target_of_c(text)):
            rows.append(("ЛР 1", "hello.c", "пропущено", f"код для другой системы, {SYSTEM_NAME} его не собирает"))
        else:
            with tempfile.TemporaryDirectory() as d:
                exe, r = build_c(c, d)
                if r.returncode != 0:
                    ok = False
                    rows.append(("ЛР 1", "hello.c", "ошибка", "не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150]))
                else:
                    out = run([str(exe)], input="\n").stdout
                    if PID_LINE.search(out):
                        rows.append(("ЛР 1", "hello.c", "пройдено", PID_LINE.search(out).group(0)))
                    else:
                        ok = False
                        rows.append(("ЛР 1", "hello.c", "ошибка", "нет строки «agent v0, pid=…» в выводе"))
    if py.exists():
        text = py.read_text(encoding="utf-8", errors="replace")
        if not fits(target_of_py(text)):
            rows.append(("ЛР 1", "hello.py", "пропущено", f"код для другой системы, в {SYSTEM_NAME} не запускается"))
        else:
            r = run([sys.executable, str(py)], input="\n")
            m = PID_LINE.search(r.stdout)
            if r.returncode == 0 and m:
                rows.append(("ЛР 1", "hello.py", "пройдено", m.group(0)))
            else:
                ok = False
                tail = (r.stderr.strip().splitlines() or ["нет строки «agent v0 (python), pid=…» в выводе"])[-1]
                rows.append(("ЛР 1", "hello.py", "ошибка", tail[:150]))
    return rows, ok


LAB02_LINE = "agent: total=6 area=12"


def check_lab02():
    """ЛР 2: debug.c собирается с отладочными сведениями и печатает ту же строку, что на кадрах."""
    src = ROOT / "labs" / "02-debugger" / "debug.c"
    if not src.exists():
        return [("ЛР 2", "debug.c", "не сдано", "")], True
    with tempfile.TemporaryDirectory() as d:
        exe = Path(d) / ("debug.exe" if SYSTEM == "win" else "debug")
        if SYSTEM == "win":
            r = run(["cl", "/nologo", "/Zi", "/Od", str(src), f"/Fe:{exe}", f"/Fo:{d}\\", f"/Fd:{d}\\"])
        else:
            cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
            r = run([cc, "-g", "-O0", "-o", str(exe), str(src)])
        if r.returncode != 0:
            return [("ЛР 2", "debug.c", "ошибка", "не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150])], False
        out = run([str(exe)]).stdout
    if LAB02_LINE in out:
        return [("ЛР 2", "debug.c", "пройдено", LAB02_LINE)], True
    return [("ЛР 2", "debug.c", "ошибка", f"нет строки «{LAB02_LINE}» в выводе")], False


LAB03_LINE = "sqrt(2) = 1.414214"


def check_lab03():
    """ЛР 3: libs.c собирается (в Linux — с -lm) и печатает корень из 2."""
    src = ROOT / "labs" / "03-libraries" / "libs.c"
    if not src.exists():
        return [("ЛР 3", "libs.c", "не сдано", "")], True
    with tempfile.TemporaryDirectory() as d:
        exe = Path(d) / ("libs.exe" if SYSTEM == "win" else "libs")
        if SYSTEM == "win":
            r = run(["cl", "/nologo", str(src), f"/Fe:{exe}", f"/Fo:{d}\\"])
        else:
            cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
            r = run([cc, "-o", str(exe), str(src), "-lm"])
        if r.returncode != 0:
            return [("ЛР 3", "libs.c", "ошибка", "не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150])], False
        out = run([str(exe)]).stdout
    if LAB03_LINE in out:
        return [("ЛР 3", "libs.c", "пройдено", LAB03_LINE)], True
    return [("ЛР 3", "libs.c", "ошибка", f"нет строки «{LAB03_LINE}» в выводе")], False


LABS = ("01-process-inside", "02-debugger", "03-libraries", "04-process-tree")
PLACEHOLDER = b"sysprog-placeholder"  # метка в заглушках шаблона, у снимка её нет
IMAGE_START = (b"\x89PNG", b"\xff\xd8\xff")


def check_screenshots():
    """Снимки лабораторных: каждый файл screenshots/*.png — картинка, и не заглушка из шаблона."""
    rows, ok = [], True
    for n, lab in enumerate(LABS, 1):
        files = sorted((ROOT / "labs" / lab / "screenshots").glob("*.png"))
        if not files:
            continue
        data = {f.name: f.read_bytes() for f in files}
        broken = [name for name, b in data.items() if not b.startswith(IMAGE_START)]
        left = [name[:2] for name, b in data.items() if PLACEHOLDER in b]
        if broken:
            ok = False
            rows.append((f"ЛР {n}", "screenshots/", "ошибка", "файл не картинка: " + ", ".join(broken)))
        elif len(left) == len(files):
            rows.append((f"ЛР {n}", "screenshots/", "не сдано", f"снимков 0 из {len(files)}"))
        elif left:
            rows.append((f"ЛР {n}", "screenshots/", "не сдано", f"снимков {len(files) - len(left)} из {len(files)}, остались заглушки " + ", ".join(left)))
        else:
            rows.append((f"ЛР {n}", "screenshots/", "пройдено", f"снимков {len(files)} из {len(files)}"))
    return rows, ok


def system_uptime():
    """Секунды с запуска системы — тем способом, которым их не считает агент студента."""
    if SYSTEM == "win":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.GetTickCount64.restype = ctypes.c_uint64
        return k32.GetTickCount64() // 1000
    if SYSTEM == "mac":
        import time
        boot = int(re.search(r"sec = (\d+)", run(["sysctl", "-n", "kern.boottime"]).stdout).group(1))
        return int(time.time()) - boot
    return int(float(Path("/proc/uptime").read_text().split()[0]))


def check_module1_agent():
    """Модуль 1, задание «Агент»: ядро собирается в библиотеку, brain.py печатает JSON с полем uptime_s."""
    core, brain = ROOT / "agent" / "core", ROOT / "agent" / "brain" / "brain.py"
    sources = [f for f in core.glob("*.c") if "core_get_info" in f.read_text(encoding="utf-8", errors="replace")
               and "int main" not in f.read_text(encoding="utf-8", errors="replace")]
    if not sources or not brain.exists():
        return [("Модуль 1", "agent", "не сдано", "нет agent/core/*.c с core_get_info или agent/brain/brain.py")], True
    mine = [f for f in sources if fits(target_of_c(f.read_text(encoding="utf-8", errors="replace")))]
    if not mine:
        return [("Модуль 1", "agent", "пропущено", f"ядро для другой системы, {SYSTEM_NAME} его не собирает")], True
    src = mine[0]
    if SYSTEM == "win":
        r = run(["cl", "/nologo", "/LD", str(src), "/Fe:sentry_core.dll", "/Fo:" + str(core) + "\\"], cwd=core)
    elif SYSTEM == "mac":
        r = run(["clang", "-shared", "-fPIC", "-o", "libsentry_core.dylib", str(src)], cwd=core)
    else:
        r = run(["gcc", "-shared", "-fPIC", "-o", "libsentry_core.so", str(src)], cwd=core)
    if r.returncode != 0:
        return [("Модуль 1", src.name, "ошибка", "ядро не собирается: " + (r.stdout + r.stderr).strip().splitlines()[-1][:150])], False
    r = run([sys.executable, str(brain)])
    try:
        msg = json.loads(r.stdout)
    except ValueError:
        tail = (r.stderr.strip().splitlines() or ["brain.py не напечатал JSON"])[-1]
        return [("Модуль 1", "brain.py", "ошибка", tail[:150])], False
    if "uptime_s" not in msg and "pid" in msg:
        return [("Модуль 1", "brain.py", "не сдано", "ядро из глав 1.1–1.2 работает, поля uptime_s ещё нет")], True
    missing = [k for k in ("event", "pid", "cpus", "page_size", "host", "uptime_s") if k not in msg]
    if missing:
        return [("Модуль 1", "brain.py", "ошибка", "в JSON нет полей: " + ", ".join(missing))], False
    real = system_uptime()
    if not isinstance(msg["uptime_s"], int) or abs(msg["uptime_s"] - real) > 60:
        return [("Модуль 1", "brain.py", "ошибка", f"uptime_s = {msg['uptime_s']}, система работает {real} с")], False
    return [("Модуль 1", "agent", "пройдено", f"uptime_s = {msg['uptime_s']}, система — {real} с")], True


def check_module1_ai():
    """Модуль 1, задание «ИИ»: сценарий n8n с вебхуком и моделью Ollama и журнал проверки ответов."""
    flow, log = ROOT / "agent" / "n8n" / "agent-uptime.json", ROOT / "agent" / "n8n" / "ai-log.md"
    if not flow.exists():
        return [("Модуль 1", "agent/n8n", "не сдано", "нет agent-uptime.json — выгрузки сценария из n8n")], True
    if not log.exists():
        return [("Модуль 1", "agent/n8n", "ошибка", "нет ai-log.md — журнала проверки ответов модели")], False
    try:
        nodes = [n.get("type", "") for n in json.loads(flow.read_text(encoding="utf-8")).get("nodes", [])]
    except ValueError:
        return [("Модуль 1", "agent-uptime.json", "ошибка", "файл не разбирается как JSON — экспорт из n8n")], False
    need = {"вебхук": "webhook", "модель Ollama": "ollama"}
    lost = [name for name, part in need.items() if not any(part in n.lower() for n in nodes)]
    if lost:
        return [("Модуль 1", "agent-uptime.json", "ошибка", "в сценарии нет узлов: " + ", ".join(lost))], False
    if log.read_text(encoding="utf-8").count("___"):
        return [("Модуль 1", "ai-log.md", "ошибка", "в журнале остались пропуски ___")], False
    return [("Модуль 1", "agent/n8n", "пройдено", f"узлов в сценарии: {len(nodes)}")], True


def main():
    # Консоль Windows по умолчанию в cp1252: русский текст выводится в UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    rows, ok = check_lab01()
    rows2, ok2 = check_lab02()
    rows3, ok3 = check_lab03()
    rows4, ok4 = check_module1_agent()
    rows5, ok5 = check_module1_ai()
    rows6, ok6 = check_screenshots()
    rows += rows2 + rows3 + rows6 + rows4 + rows5
    ok = ok and ok2 and ok3 and ok4 and ok5 and ok6
    passed = 0  # проверки агента появятся с пары 4
    lines = [f"## Проверки · {SYSTEM_NAME}", "",
             "| Работа | Файл | Результат | Подробности |", "|---|---|---|---|"]
    lines += [f"| {a} | `{b}` | {c} | {d} |" for a, b, c, d in rows]
    lines += ["", f"### Агент-сторож: проверок пройдено {passed} / {len(AGENT_CHECKS)}", "",
              "| № | Пара | Проверка | Результат |", "|---|---|---|---|"]
    for n, pair, name in AGENT_CHECKS:
        state = "ещё не открыта" if n > OPENED else "не пройдена"
        lines.append(f"| {n} | {pair} | {name} | {state} |")
    report = "\n".join(lines)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

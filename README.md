# PixelCraft 🎨

**PixelCraft** — легковесный процедурный Python-движок для создания 2D пиксель-арта, игровых спрайтов и покадровых анимаций.

Вместо ручного закрашивания каждого пикселя или использования нестабильных диффузионных нейросетей, PixelCraft делает упор на **процедурную геометрическую генерацию** с расчётом освещения, математической симметрией и строгими ретро-палитрами. 

Движок одинаково удобен как для разработчиков инди-игр и генеративного арта, так и для автоматизации и AI-ассистентов (Claude, Cursor, Codex, Antigravity, Gemini), для которых в репозиторий уже встроен готовый **Agent Skill**.

---

## ✨ Ключевые возможности

* 🔮 **Процедурные геометрические примитивы (Primary Method):**
  * `draw_shaded_sphere` — честный 3D-объём, направленный свет и плавные блики для голов, тел, сфер и драгоценных камней.
  * `draw_shaded_cylinder` — цилиндрические формы для лезвий, колонн, брони и конечностей.
  * `draw_polygon` — растеризованные полигоны произвольной формы для ушей, крыльев, щитов и плащей.
  * `draw_thick_line` — линии заданной толщины со сглаживанием пиксельных стыков.
* 📐 **Математическая симметрия (`mirror_horizontal`):**
  * Рисуйте только левую половину персонажа, оружия или щита — движок автоматически отзеркалит её на правую сторону со 100% точностью.
* 🌈 **Кураторские палитры и умные градиенты:**
  * Встроены классические палитры: PICO-8, DawnBringer (DB16, DB32), Endesga 32 (EDG32), Sweetie16, GameBoy.
  * `Palette.create_ramp()` — алгоритмическая генерация цветовых рамп с затемнением, высветлением и сдвигом цветового тона (`hue_shift`).
* 🪄 **Умные пост-фильтры и слои:**
  * `auto_outline(color)` — чёткий контур в 1px без артефактов.
  * `auto_shadow(dx, dy)` — процедурная падающая тень.
  * `palette_swap(mapping)` — мгновенный рескин спрайта (например, зелье здоровья в зелье маны).
  * `LayeredCanvas` — многослойная композиция (тело, одежда, глаза, экипировка).
* 🎞️ **Анимации и экспорт:**
  * Покадровый таймлайн `Animation`, дельта-кадры, процедурный отскок (`create_idle_bounce`) и дыхание.
  * Экспорт в `.png`, анимированные `.gif`, спрайтшиты с метаданными `.json` и ресурсы для Godot 4 (`.tres`).
* 🖼️ **Интерактивная HTML-галерея (`gallery.html`):**
  * Встроенная веб-витрина с зумом (до 12x), переключением фонов (шахматка, глубокий тёмный, светлый, хромакей), фильтрацией и определением разрешения.
* 🖥️ **TrueColor терминальный вывод:**
  * Мгновенный вывод спрайтов прямо в консоль символами полублоков `▀` (2 вертикальных пикселя на 1 текстовый символ = квадратное соотношение 1:1).
* 🔍 **Встроенный линтер (`lint_sprite`):**
  * Автоматическая проверка на висячие пиксели (jaggies / orphan pixels), симметрию и чистоту используемой палитры.

---

## 🚀 Установка

```bash
git clone https://github.com/flopercin/PixelCraft-Engine.git
cd PixelCraft-Engine
pip install -e .
```

*Требования: Python 3.8+ и Pillow.*

---

## 🛠 Быстрый старт

### 1. Процедурный спрайт персонажа (Рекомендуемый подход)

Процедурные примитивы обеспечивают честный объём, плавные световые рампы и компактный читаемый код:

```python
from pixelcraft import Canvas, Palette, print_ansi, save_png, export_gallery, lint_sprite

# 1. Загружаем палитру и генерируем рампы со сдвигом цветового тона
palette = Palette.load("edg32")
body_ramp = Palette.create_ramp("#d77643", steps=5, hue_shift_deg=10)
ear_dark = "#181425"

c = Canvas(24, 24, palette=palette)

# 2. Рисуем объёмную сферу головы и элементы левой половины
c.draw_shaded_sphere(cx=11, cy=13, radius=8, ramp=body_ramp, light_dir=(-0.6, -0.6))
c.draw_polygon([(7, 8), (4, 1), (3, 0), (6, 5), (10, 8)], fill_color=ear_dark, outline_color="#100c18")

# Глаз и мордочка
c.draw_rect(x=6, y=11, w=3, h=3, color="#63c74d")
c.draw_pixel(7, 12, "#181425")
c.draw_pixel(6, 11, "#ffffff")
c.draw_rect(x=8, y=14, w=4, h=4, color="#ead4aa")

# 3. Зеркалим левую половину на правую сторону
c.mirror_horizontal(from_side="left")

# 4. Центральные детали и ретро-обводка
c.draw_pixel(11, 14, "#f6757a")
c.draw_pixel(12, 14, "#f6757a")
c = c.auto_outline("#181425")

# 5. Вывод в консоль, сохранение и обновление веб-галереи
print_ansi(c, title="Procedural Character")
save_png(c, "output/character.png", scale=1, preview_scale=8)
export_gallery("output")

# Проверка качества
print(lint_sprite(c).summary())
```

---

### 2. Создание покадровой анимации и спрайтшита

```python
from pixelcraft import Canvas, Animation, save_gif, save_spritesheet

anim = Animation(name="slime_idle", default_duration_ms=160)

# Базовый кадр
anim.add_frame(slime_base, duration_ms=200)

# Кадр со сжатием вниз
frame_squish = Canvas(16, 16)
frame_squish.paste(slime_base, x=0, y=1)
anim.add_frame(frame_squish, duration_ms=180)

# Кадр с морганием
frame_blink = slime_base.clone()
frame_blink.draw_line(4, 5, 5, 5, "#140c1c")
frame_blink.draw_line(10, 5, 11, 5, "#140c1c")
anim.add_frame(frame_blink, duration_ms=120)

# Экспорт в GIF и Spritesheet (+ JSON метаданные)
save_gif(anim, "output/slime_idle.gif", preview_scale=8)
save_spritesheet(anim, "output/slime_sheet.png", layout="horizontal", save_meta_json=True)
```

---

### 3. Быстрые микро-иконки через ASCII-сетку

Для небольших значков 8×8 и 16×16 доступно построение через символьную сетку:

```python
from pixelcraft import Canvas, Palette, save_png

palette = Palette.load("pico8").with_aliases({
    ".": None,          # Прозрачный
    "C": "brown",       # Пробка
    "G": "light_gray",  # Стекло
    "W": "white",       # Блик
    "R": "red",         # Зелье
})

# Рисуем только левую половину флакона:
left_half = """
......CC
......CC
....GGGG
...GWWWW
..GWRRRR
.GWRRRRR
.GWRRRRR
..GBBBBB
"""

potion = Canvas.from_ascii_symmetric(left_half, palette, axis="x")
potion = potion.auto_outline("#000000")
save_png(potion, "output/potion.png")
```

---

## 🖼 Интерактивная HTML-галерея

PixelCraft умеет автоматически генерировать и обновлять локальный веб-просмотрщик для созданных спрайтов.

Запуск из консоли:
```bash
python -m pixelcraft gallery output
```

Или вызовом из скрипта:
```python
from pixelcraft import export_gallery

export_gallery("output")
```

Результат сохраняется в `output/gallery.html`. Файл можно открыть в любом браузере: он поддерживает масштабирование (1x, 2x, 4x, 6x, 8x, 12x), переключение прозрачного/тёмного/светлого фона, мгновенный поиск и отображение реального разрешения спрайтов.

---

## 🤖 Интеграция с AI-агентами (Agent Skill)

В репозиторий встроен специализированный навык для AI-агентов:
* **Файл навыка:** [`.agents/skills/pixelcraft/SKILL.md`](.agents/skills/pixelcraft/SKILL.md)
* **Правила репозитория:** [`AGENTS.md`](AGENTS.md)

Поддерживается в **Antigravity**, **Claude Code**, **Cursor**, **Codex**, **Windsurf** и других AI-инструментах.

Благодаря компактным процедурным шаблонам и строгим правилам симметрии, AI-ассистенты генерируют качественные спрайты за 1 шаг без пространственных искажений и лишних затрат токенов.

---

## 🖥 Консольный интерфейс (CLI)

```bash
# Список встроенных ретро-палитр
python -m pixelcraft palettes

# Просмотр изображения прямо в консоли с ANSI-цветами и линтером
python -m pixelcraft preview output/potion.png

# Генерация HTML-галереи спрайтов
python -m pixelcraft gallery output
```

---

## 📂 Структура проекта

```
PixelCraft-Engine/
├── pixelcraft/
│   ├── __init__.py       # Экспорт функций и классов
│   ├── palette.py        # Палитры, рампы, конвертация цветов
│   ├── canvas.py         # Canvas, LayeredCanvas, процедурные примитивы
│   ├── animation.py      # Timeline, кадры, дельта-анимации
│   ├── renderer.py       # ANSI-вывод, PNG/GIF, спрайтшиты, галерея
│   ├── linter.py         # Диагностика артефактов и симметрии
│   └── cli.py            # Консольные команды
├── examples/
│   ├── 01_magic_potion_ascii.py        # Иконка через ASCII-сетку
│   ├── 02_character_layered.py         # Слои: рыцарь и экипировка
│   ├── 03_animated_slime.py            # Анимация, GIF и спрайтшит
│   ├── 04_dungeon_sword_procedural.py  # Процедурное оружие с градиентами
│   ├── 05_edit_and_reskin.py           # Рескин через palette_swap
│   └── 06_procedural_32x32_boss.py     # 32x32 процедурный босс со сферами
├── .agents/skills/pixelcraft/          # Встроенный Agent Skill
├── AGENTS.md                           # Универсальные инструкции для ИИ
├── output/                             # Демонстрационные спрайты и gallery.html
└── pyproject.toml                      # Конфигурация пакета
```

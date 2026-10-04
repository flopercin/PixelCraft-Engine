# PixelCraft 🎨

**PixelCraft** — это программный движок и фреймворк для создания 2D спрайтов и анимаций в стиле **Pixel Art**, спроектированный специально для **AI-агентов и LLM**.

---

## 💡 Почему обычный код труден для ИИ и как PixelCraft это решает

Когда LLM генерирует пиксель-арт обычными библиотеками (например, `draw_pixel(x, y)` в PIL/Pygame):
1. **Пространственный дрифт (Spatial Drift):** Языковые модели не удерживают в уме точную 2D-сетку координат на больших фрагментах кода. Линии получаются кривыми, конечности смещаются, симметрия нарушается.
2. **Проблемы с палитрой:** Генерация случайных HEX-цветов разрушает гармонию ретро-арта.
3. **«Дрожание» анимации (Boiling):** При попытке нарисовать второй кадр с нуля модель меняет пропорции персонажа.
4. **Слепота процесса:** ИИ не видит промежуточный результат и не может скорректировать ошибки.

### Архитектурные решения PixelCraft для ИИ:
* **ASCII-матрицы символов (`from_ascii`):** Текстовая сетка сохраняет пространственную топологию прямо в токенах модели. Символы привязаны к цветам палитры (`.` — прозрачный, `#` — контур, `G` — золото).
* **Симметричный режим (`from_ascii_symmetric`):** ИИ рисует только **половину** спрайта (левую часть), а движок зеркалит её со 100% математической точностью. Это исключает асимметрию лиц, щитов, мечей, зелий и монстров.
* **Кураторские палитры:** Встроены палитры PICO-8, DawnBringer (DB16, DB32), Endesga 32, GameBoy, Sweetie16 + генератор градиентных рамп со сдвигом цветового тона (`hue_shift`).
* **Умные пост-фильтры:** `auto_outline(color)` создаёт чёткую обводку в 1px, `auto_shadow()` создаёт падающую тень.
* **Слои (`LayeredCanvas`):** Независимое рисование тела, одежды, глаз и оружия.
* **Анимации и дельта-патчи:** Клонирование базового кадра, процедурный отскок (`create_idle_bounce`), дыхание, парение (`create_floating`), мигание глаз и хит-флеш.
* **Мгновенный визуальный фидбек для ИИ:**
  * **ANSI TrueColor 24-bit (`print_ansi`):** Рисует спрайт прямо в stdout консоли символами полублоков `▀` (2 вертикальных пикселя на 1 текстовый символ = идеальное соотношение 1:1).
  * **Текстовая сетка (`to_ascii`):** Читаемая матрица символов в текстовом выводе.
  * **Увеличенный превью (`_preview.png` / `preview_scale=8`):** Создаёт увеличенный файл без размытия, который мультимодальный агент может сразу изучить через `view_file`.
  * **Линтер качества (`lint_sprite`):** Диагностирует висячие пиксели-мусор (orphan pixels / jaggies), проверяет палитру, симметрию и размер видимой области.

---

## 🚀 Установка

```bash
cd FloprSprites
pip install -e .
```

Требуется только Python 3.8+ и Pillow.

---

## 🛠 Быстрый старт

### 1. Спрайт через симметричную ASCII-сетку

```python
from pixelcraft import Canvas, Palette, print_ansi, save_png, lint_sprite

# Назначаем символы на цвета палитры
palette = Palette.load("pico8").with_aliases({
    ".": None,          # Прозрачный
    "C": "brown",       # Пробка
    "G": "light_gray",  # Стекло
    "W": "white",       # Блик
    "P": "dark_purple", # Зелье
    "M": "pink",        # Свечение
    "B": "dark_blue",   # Дно
})

# Рисуем только левые 8 колонок!
left_half = """
......CC
......CC
....GGGG
...GWWWW
..GWPPMM
.GWPPPMM
.GWPPPMM
.GWWPPMM
.GPPMMMM
.GPPMMMM
.GPPMMMM
..GBBBBB
"""

# Движок создаёт симметричный 16x12 спрайт
potion = Canvas.from_ascii_symmetric(left_half, palette, axis="x")
potion = potion.auto_outline("#000000")

# Вывод в консоль и сохранение
print_ansi(potion, title="Potion")
save_png(potion, "output/potion.png", scale=1, preview_scale=8)

# Диагностика
report = lint_sprite(potion)
print(report.summary())
```

---

### 2. Создание анимации и спрайтшита

```python
from pixelcraft import Canvas, Palette, Animation, save_gif, save_spritesheet

anim = Animation(name="slime_idle", default_duration_ms=160)

# Кадр 0: базовый
anim.add_frame(slime_base, duration_ms=200)

# Кадр 1: сжатие вниз на 1px
frame_squish = Canvas(16, 16)
frame_squish.paste(slime_base, x=0, y=1)
anim.add_frame(frame_squish, duration_ms=180)

# Кадр 2: моргание (дельта-патч глаз)
frame_blink = slime_base.clone()
frame_blink.draw_line(4, 5, 5, 5, "black")
frame_blink.draw_line(10, 5, 11, 5, "black")
anim.add_frame(frame_blink, duration_ms=120)

# Экспорт в GIF и Spritesheet (с JSON для Godot / Unity)
save_gif(anim, "output/slime.gif", preview_scale=8)
save_spritesheet(anim, "output/slime_sheet.png", layout="horizontal", save_meta_json=True)
```

---

## 🖥 Консольный интерфейс (CLI)

```bash
# Список доступных палитр
python -m pixelcraft palettes

# Превью любого PNG прямо в терминале с линтером
python -m pixelcraft preview output/potion.png
```

---

## 📂 Структура проекта

```
FloprSprites/
├── pixelcraft/
│   ├── __init__.py       # Публичный API
│   ├── palette.py        # Палитры, рампы, конвертация цветов
│   ├── canvas.py         # Canvas, LayeredCanvas, примитивы, ASCII-парсинг
│   ├── animation.py      # Timeline, процедурный баунс, флоат, сжатие
│   ├── renderer.py       # ANSI-вывод, Pillow PNG/GIF, Spritesheets, HTML viewer
│   ├── linter.py         # Проверка артефактов, jaggies, симметрии
│   └── cli.py            # CLI команды
├── examples/
│   ├── 01_magic_potion_ascii.py        # Симметрия + ASCII сетка
│   ├── 02_character_layered.py         # Многослойный рыцарь
│   ├── 03_animated_slime.py            # Анимация, GIF, Spritesheet + JSON
│   └── 04_dungeon_sword_procedural.py  # Процедурное рисование + рампы
├── output/                             # Сгенерированные спрайты и превью
└── pyproject.toml                      # Конфигурация пакета
```

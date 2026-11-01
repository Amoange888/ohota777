import tkinter as tk
from tkinter import ttk
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
COLS = 30
ROWS = 15
CELL_SIZE = 35
RABBIT_COUNT = 65
WOLF_MALE_COUNT = 20
WOLF_FEMALE_COUNT = 20
MAX_LIFE = 10
rabbits = []
wolves = []
occupied = set()
day = 0
history_days = []
rabbits_history = []
wolves_history = []

def random_empty_cell():
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)

        if (x, y) not in occupied:
            occupied.add((x, y))
            return x, y

def get_neighbors(x, y):
    neighbors = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = x + dx
            ny = y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                neighbors.append((nx, ny))
    return neighbors

for i in range(RABBIT_COUNT):
    x, y = random_empty_cell()

    rabbit = {
        "x": x,
        "y": y
    }

    rabbits.append(rabbit)
for i in range(WOLF_MALE_COUNT):
    x, y = random_empty_cell()

    wolf = {
        "x": x,
        "y": y,
        "life": MAX_LIFE,
        "sex": "male"
    }

    wolves.append(wolf)
for i in range(WOLF_FEMALE_COUNT):
    x, y = random_empty_cell()

    wolf = {
        "x": x,
        "y": y,
        "life": MAX_LIFE,
        "sex": "female"
    }

    wolves.append(wolf)

def get_occupied_cells():
    occupied_cells = set()
    for rabbit in rabbits:
        occupied_cells.add((rabbit["x"], rabbit["y"]))
    for wolf in wolves:
        occupied_cells.add((wolf["x"], wolf["y"]))
    return occupied_cells

def check_uniq_position():
    positions = []
    for rabbit in rabbits:
        positions.append((rabbit["x"], rabbit["y"]))
    for wolf in wolves:
        positions.append((wolf["x"], wolf["y"]))
    if len(positions) != len(set(positions)):
        print("Несколько животных находятся на одной клетке!")
        return False
    return True

def get_free_neighbors(x, y, occupied_cells):
    free_cells = []

    for cell in get_neighbors(x, y):
        if cell not in occupied_cells:
            free_cells.append(cell)
    return free_cells

def choose_random_move(x, y, occupied_cells):
    free_cells = get_free_neighbors(x, y, occupied_cells)
    possible_moves = free_cells + [(x, y)]
    return random.choice(possible_moves)

def resolve_moves(moves):
    random.shuffle(moves)
    occupied_targets = set()
    accepted_moves =  []
    for animal, new_position in moves:
        if new_position not in occupied_targets:
            occupied_targets.add(new_position)
            accepted_moves.append((animal, new_position))
    return accepted_moves

def plan_moves(animals, occupied_cells):
    moves = []
    for animal in animals:
        x = animal["x"]
        y = animal["y"]
        new_position = choose_random_move(x, y, occupied_cells)
        moves.append((animal, new_position))
    return moves

def apply_moves(moves):
    for animal, new_position in moves:
        animal["x"] = new_position[0]
        animal["y"] = new_position[1]

root = tk.Tk()
root.title("Симуляция экосистемы")

canvas = tk.Canvas(
    root,
    width=COLS * CELL_SIZE,
    height=ROWS * CELL_SIZE
)
canvas.pack(padx = 10, pady = 10)
stats_label = tk.Label(root, text = "")
stats_label.pack()
data_frame = tk.Frame(root)
data_frame.pack(pady=5)

history_frame = tk.Frame(data_frame)
history_frame.pack(side="left", padx=10)
history_table = ttk.Treeview(
    history_frame,
    columns=("day", "wolves", "rabbits"),
    show="headings",
    height=18
)
history_table.heading("day", text="День")
history_table.heading("wolves", text="Волки")
history_table.heading("rabbits", text="Кролики")
style = ttk.Style()
style.configure("Treeview", rowheight=28, font=("Arial", 11))
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
history_table.column("day", width=85, anchor="center", stretch=False)
history_table.column("wolves", width=100, anchor="center", stretch=False)
history_table.column("rabbits", width=100, anchor="center", stretch=False)
history_table.pack()
fig = Figure(figsize=(7, 4), dpi=120)
ax = fig.add_subplot(111)
graph_canvas = FigureCanvasTkAgg(fig, master=data_frame)
graph_canvas.get_tk_widget().pack(side="left", padx=10)
controls_frame = tk.Frame(root)
controls_frame.pack(pady = 5)
tk.Label(controls_frame, text = "Кролики").grid(row = 0, column = 0)
rabbit_entry = tk.Entry(controls_frame, width = 6)
rabbit_entry.grid(row = 0, column = 1)
rabbit_entry.insert(0, str(RABBIT_COUNT))
tk.Label(controls_frame, text="Самцы:").grid(row=0, column=2)
male_entry = tk.Entry(controls_frame, width=6)
male_entry.grid(row=0, column=3)
male_entry.insert(0, str(WOLF_MALE_COUNT))
tk.Label(controls_frame, text="Самки:").grid(row=0, column=4)
female_entry = tk.Entry(controls_frame, width=6)
female_entry.grid(row=0, column=5)
female_entry.insert(0, str(WOLF_FEMALE_COUNT))
for row in range(ROWS):
    for col in range(COLS):
        x1 = col * CELL_SIZE
        y1 = row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        canvas.create_rectangle(
            x1, y1, x2, y2,
            outline = 'BLACK'

        )
def move_animals(animals):
    for animal in animals:
        animal["x"] += random.randint(-1, 1)
        animal["y"] += random.randint(-1, 1)
        animal["x"] = max(0, min(COLS -1, animal["x"]))
        animal["y"] = max(0, min(ROWS - 1, animal["y"]))

def plan_wolf_actions(occupied_cells):
    moves = []
    hunted_rabbits = []
    fed_wolves = []

    shuffled_wolves = wolves[:]
    random.shuffle(shuffled_wolves)

    for wolf in shuffled_wolves:
        if wolf["life"] <= 5:
            neighbors = get_neighbors(wolf["x"], wolf["y"])

            available_rabbits = [
                rabbit for rabbit in rabbits
                if (rabbit["x"], rabbit["y"]) in neighbors
                and rabbit not in hunted_rabbits
            ]

            if available_rabbits:
                prey = random.choice(available_rabbits)
                hunted_rabbits.append(prey)
                fed_wolves.append(wolf)
                continue

        new_position = choose_random_move(
            wolf["x"],
            wolf["y"],
            occupied_cells
        )
        moves.append((wolf, new_position))

    return moves, hunted_rabbits, fed_wolves

def reproduce_rabbits():
    occupied_cells = get_occupied_cells()
    newborns = []
    for rabbit in rabbits:
        free_cells = get_free_neighbors(
            rabbit["x"],
            rabbit["y"],
            occupied_cells
        )
        if free_cells and random.random() < 0.2:
            new_position = random.choice(free_cells)
            new_rabbit = {
                "x": new_position[0],
                "y": new_position[1],
            }
            newborns.append(new_rabbit)
            occupied_cells.add(new_position)
    rabbits.extend(newborns)
    return len(newborns)

def reproduce_wolves():
    occupied_cells = get_occupied_cells()
    newborns = []
    paired_wolves = set()

    for i, wolf in enumerate(wolves):
        if i in paired_wolves:
            continue

        if wolf["life"] <= 7.5:
            continue

        neighbors = get_neighbors(wolf["x"], wolf["y"])

        for j, partner in enumerate(wolves):
            if i == j or j in paired_wolves:
                continue

            if partner["life"] <= 7.5:
                continue

            if partner["sex"] == wolf["sex"]:
                continue

            partner_position = (partner["x"], partner["y"])

            if partner_position not in neighbors:
                continue

            free_cells = get_free_neighbors(
                wolf["x"],
                wolf["y"],
                occupied_cells
            )

            if free_cells and random.random() < 0.5:
                new_position = random.choice(free_cells)

                new_wolf = {
                    "x": new_position[0],
                    "y": new_position[1],
                    "life": MAX_LIFE,
                    "sex": random.choice(["male", "female"])
                }

                newborns.append(new_wolf)
                occupied_cells.add(new_position)

            paired_wolves.add(i)
            paired_wolves.add(j)
            break

    wolves.extend(newborns)
    return len(newborns)

def age_wolves():
    dead_wolves = 0
    for wolf in wolves[:]:
        wolf["life"] -=1
        if wolf["life"] <= 0:
            wolves.remove(wolf)
            dead_wolves += 1
    return dead_wolves

def check_ecosystem():
    if len(rabbits) == 0 or len(wolves) == 0:
        print("Экосистема погибла.")
        return False

    if len(rabbits) < 20:
        print("ВНИМАНИЕ: кролики на грани исчезновения!")

    if len(wolves) < 5:
        print("ВНИМАНИЕ: волки на грани исчезновения!")

    return True

def update_stats():
    stats_label.config(
        text = f"День: {day}| Кролики: {len(rabbits)}| Волки: {len(wolves)}"
    )

running = False

def update_history():
    history_table.insert(
        "",
        "end",
        values=(day, len(wolves), len(rabbits))
    )
    rows = history_table.get_children()
    if len(rows) > 18:
        history_table.delete(rows[0])
    history_days.append(day)
    rabbits_history.append(len(rabbits))
    wolves_history.append(len(wolves))
    ax.clear()
    ax.plot(history_days, rabbits_history, color="green", label="Кролики")
    ax.plot(history_days, wolves_history, color="red", label="Волки")
    ax.set_xlabel("Дни")
    ax.set_ylabel("Количество животных")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax.relim()
    ax.autoscale_view()
    fig.tight_layout()
    graph_canvas.draw()

def auto_run():
    global running

    if not running:
        return
    next_turn()
    if rabbits and wolves and running:
        root.after(500, auto_run)
    else:
        running = False


def start_simulation():
    global running
    if not running and rabbits and wolves:
        running = True
        auto_run()

def next_turn():
    global day
    day += 1
    dead_wolves = age_wolves()

    occupied_cells = get_occupied_cells()

    rabbit_moves = plan_moves(rabbits, occupied_cells)

    wolf_moves, hunted_rabbits, fed_wolves = plan_wolf_actions(
        occupied_cells
    )

    all_moves = rabbit_moves + wolf_moves
    accepted_moves = resolve_moves(all_moves)

    apply_moves(accepted_moves)

    for rabbit in hunted_rabbits:
        rabbits.remove(rabbit)

    for wolf in fed_wolves:
        wolf["life"] = MAX_LIFE

    print("Успешные охоты:", len(hunted_rabbits))
    print("Волков умерло от голода:", dead_wolves)
    reproduce_rabbits()
    reproduce_wolves()
    update_history()
    print("Кроликов", len(rabbits))
    if not check_uniq_position():
        return
    print("Волков", len(wolves))
    if not check_ecosystem():
        canvas.delete("all")
        canvas.create_text(
            COLS * CELL_SIZE / 2,
            ROWS * CELL_SIZE / 2,
            text="Экосистема погибла",
            font=("Arial", 20, "bold"),
            fill="red"
        )
        update_stats()
        button.config(state="disabled")
        return
    canvas.delete("all")
    for row in range(ROWS):
        for col in range(COLS):
            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE

            canvas.create_rectangle(
                x1, y1,
                x1 + CELL_SIZE, y1 + CELL_SIZE,
                outline="black"
            )

    draw_animals()
    update_stats()

def draw_animals():
    # Рисуем кроликов
    for rabbit in rabbits:
        x = rabbit["x"] * CELL_SIZE
        y = rabbit["y"] * CELL_SIZE

        # Уши
        canvas.create_oval(
            x + 9, y + 2,
            x + 15, y + 17,
            fill="gray", outline="black"
        )
        canvas.create_oval(
            x + 17, y + 2,
            x + 23, y + 17,
            fill="gray", outline="black"
        )

        # Тело
        canvas.create_oval(
            x + 5, y + 12,
            x + 30, y + 31,
            fill="gray", outline="black"
        )

        # Глаз
        canvas.create_oval(
            x + 23, y + 17,
            x + 26, y + 20,
            fill="black"
        )

        # Нос
        canvas.create_oval(
            x + 29, y + 22,
            x + 32, y + 25,
            fill="pink", outline="black"
        )

    # Рисуем волков
    for wolf in wolves:
        x = wolf["x"] * CELL_SIZE
        y = wolf["y"] * CELL_SIZE

        # Хвост
        canvas.create_line(
            x + 5, y + 19,
            x + 1, y + 13,
            x + 3, y + 25,
            fill="gray", width=3
        )

        # Тело
        canvas.create_oval(
            x + 5, y + 12,
            x + 27, y + 30,
            fill="gray", outline="black"
        )

        # Уши
        canvas.create_polygon(
            x + 12, y + 14,
            x + 12, y + 4,
            x + 19, y + 13,
            fill="gray", outline="black"
        )

        # Морда
        canvas.create_polygon(
            x + 22, y + 15,
            x + 34, y + 20,
            x + 22, y + 26,
            fill="gray", outline="black"
        )

        # Красный глаз
        canvas.create_oval(
            x + 24, y + 17,
            x + 27, y + 20,
            fill="red"
        )

        # Запас жизни
        life_color = "green" if wolf["life"] > 5 else "red"

        canvas.create_text(
            x + CELL_SIZE - 5,
            y + CELL_SIZE - 4,
            text=str(wolf["life"]),
            fill=life_color,
            font=("Arial", 9, "bold"),
            anchor="se"
        )

def reset_simulation():
    global rabbits, wolves, occupied, day, running
    running = False
    try:
        rabbit_count = int(rabbit_entry.get())
        male_count = int(male_entry.get())
        female_count = int(female_entry.get())

        if min(rabbit_count, male_count, female_count) < 0:
            raise ValueError

    except ValueError:
        print("Введите целые неотрицательные числа!")
        return
    if rabbit_count + male_count + female_count > COLS * ROWS:
        print("Слишком много животных! Максимум — 450.")
        return

    rabbits = []
    wolves = []
    occupied = set()
    day = 0
    history_days.clear()
    rabbits_history.clear()
    wolves_history.clear()
    for row in history_table.get_children():
        history_table.delete(row)
    for i in range(rabbit_count):
        x, y = random_empty_cell()
        rabbits.append({"x": x, "y": y})

    for i in range(male_count):
        x, y = random_empty_cell()
        wolves.append({
            "x": x,
            "y": y,
            "life": MAX_LIFE,
            "sex": "male"
        })

    for i in range(female_count):
        x, y = random_empty_cell()
        wolves.append({
            "x": x,
            "y": y,
            "life": MAX_LIFE,
            "sex": "female"
        })

    canvas.delete("all")
    for row in range(ROWS):
        for col in range(COLS):
            x1 = col * CELL_SIZE
            y1 = row * CELL_SIZE
            canvas.create_rectangle(
                x1, y1,
                x1 + CELL_SIZE, y1 + CELL_SIZE,
                outline="black"
            )

    draw_animals()
    update_stats()
    update_history()
    button.config(state="normal")
update_stats()
draw_animals()
button = tk.Button(root, text = "Отправить Ракеты на Киев", command = next_turn)
button.pack()
reset_button = tk.Button(
    root,
    text="Обновление",
    command=reset_simulation
)
reset_button.pack()
start_button = tk.Button(
    root,
    text="Запустить",
    command=lambda: start_simulation()
)
start_button.pack()
root.mainloop()

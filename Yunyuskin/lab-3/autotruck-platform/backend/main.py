import random
import networkx as nx  # networkx
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Папка для хранения профилей игроков
SAVE_DIR = "players"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

MODES = {
    "truck": {"speed": 90, "capacity": 10, "emoji": "🚛"},
    "drone": {"speed": 60, "capacity": 3, "emoji": "🚁"},
    "boat": {"speed": 30, "capacity": 15, "emoji": "🛥️"}
}

NODES = {}
EDGES_DATA = []


class AuditData(BaseModel):
    load: float
    segments: List[dict]


def get_player_save(player_id: str):
    path = f"{SAVE_DIR}/{player_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"balance": 1000}


def save_player_data(player_id: str, data: dict):
    with open(f"{SAVE_DIR}/{player_id}.json", "w") as f:
        json.dump(data, f)


def generate_grid_world():
    global NODES, EDGES_DATA
    NODES, EDGES_DATA = {}, []
    ids = ["A", "B", "C", "D", "E", "F", "G", "H"]
    labels = ["Склад", "Хаб", "Порт", "База", "Завод", "Центр", "Пункт", "Терминал"]
    for i, node_id in enumerate(ids):
        col, row = i % 4, i // 4
        NODES[node_id] = {"x": 180 + col * 220, "y": 180 + row * 260, "label": f"{labels[i]} {node_id}"}
    for i in range(len(ids) - 1):
        EDGES_DATA.append({"from": ids[i], "to": ids[i + 1], "dist": 200, "mode": random.choice(list(MODES.keys()))})
    extra_links = [("A", "E"), ("B", "F"), ("C", "G"), ("D", "H"), ("B", "G")]
    for u, v in extra_links:
        if random.random() > 0.4:
            EDGES_DATA.append({"from": u, "to": v, "dist": 350, "mode": random.choice(list(MODES.keys()))})


generate_grid_world()


@app.get("/init_data")
def get_data():
    return {"nodes": NODES, "edges": EDGES_DATA, "modes": MODES}


@app.get("/get_balance/{player_id}")
def get_balance(player_id: str):
    return get_player_save(player_id)


@app.get("/calculate_route")
def calculate_route(load: float):
    G = nx.DiGraph()
    for e in EDGES_DATA:
        weight = (e['dist'] / MODES[e['mode']]["speed"]) * (100 if load > MODES[e['mode']]["capacity"] else 1)
        G.add_edge(e['from'], e['to'], weight=weight, mode=e['mode'])
    try:
        path = nx.shortest_path(G, "A", "H", weight='weight')
        segments = [{"u": path[i], "v": path[i + 1], "mode": G[path[i]][path[i + 1]]['mode']} for i in
                    range(len(path) - 1)]
        return {"path": path, "segments": segments}
    except:
        return {"error": "Путь заблокирован"}


@app.post("/audit/{player_id}")
def audit_logic(player_id: str, data: AuditData):
    overloads = [s for s in data.segments if data.load > MODES[s['mode']]['capacity']]
    integrity_score = max(0, 100 - (len(overloads) * 45))
    efficiency = max(0, 100 - (len(overloads) * 40))

    cost = len(data.segments) * 40
    payout = int(data.load * 95 * (integrity_score / 100))

    # Обновление баланса на сервере
    player = get_player_save(player_id)
    player["balance"] = player["balance"] - cost + payout
    save_player_data(player_id, player)

    return {
        "efficiency": efficiency,
        "integrity_score": integrity_score,
        "payout": payout,
        "cost": cost,
        "new_balance": player["balance"],
        "bottlenecks": [f"{o['u']}→{o['v']}" for o in overloads]
    }


@app.get("/regen")
def regen():
    generate_grid_world()
    return {"status": "ok"}
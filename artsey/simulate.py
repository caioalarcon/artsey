import argparse
import yaml
from collections import defaultdict
from pynput import keyboard


def load_layout(path, orientation):
    with open(path) as f:
        data = yaml.safe_load(f)
    layout = defaultdict(dict)
    for entry in data["keymap"]:
        layer = entry["layer"]["layer"]
        keys = []
        for key in entry["combo"][orientation]:
            keys.append((key["x"], key["y"]))
        layout[layer][frozenset(keys)] = entry["description"]
    return layout, data


def build_position_map(keys):
    if len(keys) != 8:
        raise ValueError("Eight keys required")
    pos = {}
    idx = 0
    for y in range(2):
        for x in range(4):
            pos[(x, y)] = keys[idx]
            idx += 1
    return pos


def build_combo_map(layout, position_map):
    combo_map = defaultdict(dict)
    for layer, combos in layout.items():
        for coords, desc in combos.items():
            physical = frozenset(position_map[c] for c in coords)
            combo_map[layer][physical] = desc
    return combo_map


class Simulator:
    def __init__(self, combo_map):
        self.combo_map = combo_map
        self.current_layer = "Base"
        self.pressed = set()
        self.combo = set()

    def resolve_combo(self, keys):
        # check global layer first
        if keys in self.combo_map.get("Global", {}):
            return self.combo_map["Global"][keys]
        return self.combo_map.get(self.current_layer, {}).get(keys)

    def on_press(self, key):
        try:
            ch = key.char
        except AttributeError:
            return
        self.pressed.add(ch)
        self.combo.add(ch)

    def on_release(self, key):
        try:
            ch = key.char
        except AttributeError:
            if key == keyboard.Key.esc:
                return False
            return
        if ch in self.pressed:
            self.pressed.remove(ch)
        if not self.pressed:
            result = self.resolve_combo(frozenset(self.combo))
            if result:
                if result.startswith("Layer - "):
                    layer = result.split("Layer - ")[-1].strip()
                    if self.current_layer == layer:
                        self.current_layer = "Base"
                    else:
                        self.current_layer = layer
                    print(f"\n[Switched to {self.current_layer} layer]")
                else:
                    print(result, end="", flush=True)
            self.combo.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARTSEY layout simulator")
    parser.add_argument("--hand", choices=["left", "right"], default="right",
                        help="Use left or right handed combos")
    parser.add_argument("keys", nargs=8,
                        help="Eight keys: top row left->right then bottom row left->right")
    parser.add_argument("--yaml", default="artsey.yaml",
                        help="Path to artsey YAML file")
    args = parser.parse_args()

    position_map = build_position_map(args.keys)
    layout, _ = load_layout(args.yaml, args.hand)
    combo_map = build_combo_map(layout, position_map)

    sim = Simulator(combo_map)
    print("Press ESC to exit.")
    with keyboard.Listener(on_press=sim.on_press, on_release=sim.on_release) as listener:
        listener.join()


"""Project-wide constants.

The model contract is a 24-class single-stage classifier:
12 produce types × {fresh, rotten}. The Kaggle dataset's `Bellpepper`
and `Capciscum` folders are the same vegetable (user-verified) and are
merged into one canonical `bellpepper` class. Folder-name typos
`bittergroud` and `okara` are normalized to `bitter_gourd` and `okra`.
"""

from __future__ import annotations

PRODUCE_TYPES: tuple[str, ...] = (
    "apple",
    "banana",
    "bellpepper",
    "bitter_gourd",
    "carrot",
    "cucumber",
    "mango",
    "okra",
    "orange",
    "potato",
    "strawberry",
    "tomato",
)

FRESHNESS_LEVELS: tuple[str, ...] = ("fresh", "rotten")

UNKNOWN_TYPE = "unknown"
FRESHNESS_NA = "n_a"

TYPE_LABELS = PRODUCE_TYPES
FRESHNESS_LABELS = FRESHNESS_LEVELS
OUTPUT_TYPE_LABELS = TYPE_LABELS + (UNKNOWN_TYPE,)
OUTPUT_FRESHNESS_LABELS = FRESHNESS_LABELS + (FRESHNESS_NA,)

COMBINED_CLASSES: tuple[str, ...] = tuple(
    f"{produce}_{freshness}"
    for produce in PRODUCE_TYPES
    for freshness in FRESHNESS_LEVELS
)
COMBINED_UNKNOWN = f"{UNKNOWN_TYPE}_{FRESHNESS_NA}"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

TYPE_DISPLAY_NAMES = {
    "apple": "Apple",
    "banana": "Banana",
    "bellpepper": "Bell Pepper",
    "bitter_gourd": "Bitter Gourd",
    "carrot": "Carrot",
    "cucumber": "Cucumber",
    "mango": "Mango",
    "okra": "Okra",
    "orange": "Orange",
    "potato": "Potato",
    "strawberry": "Strawberry",
    "tomato": "Tomato",
    "unknown": "Unknown / Unsupported",
}

FRESHNESS_DISPLAY_NAMES = {
    "fresh": "Fresh",
    "rotten": "Rotten",
    "n_a": "N/A",
}

PRODUCE_LATIN: dict[str, str] = {
    "apple": "Malus domestica",
    "banana": "Musa acuminata",
    "bellpepper": "Capsicum annuum",
    "bitter_gourd": "Momordica charantia",
    "carrot": "Daucus carota",
    "cucumber": "Cucumis sativus",
    "mango": "Mangifera indica",
    "okra": "Abelmoschus esculentus",
    "orange": "Citrus × sinensis",
    "potato": "Solanum tuberosum",
    "strawberry": "Fragaria × ananassa",
    "tomato": "Solanum lycopersicum",
    "unknown": "Specimen incognitus",
}

PRODUCE_BASE_SHELF_LIFE: dict[str, tuple[int, int]] = {
    "apple": (14, 30),
    "banana": (3, 7),
    "bellpepper": (7, 14),
    "bitter_gourd": (4, 7),
    "carrot": (14, 28),
    "cucumber": (5, 9),
    "mango": (4, 8),
    "okra": (3, 5),
    "orange": (10, 21),
    "potato": (21, 60),
    "strawberry": (2, 5),
    "tomato": (5, 10),
    "unknown": (0, 0),
}

PRESERVATION_TIPS: dict[str, str] = {
    "apple": "Store in the refrigerator crisp drawer (4°C). Keep separate from ethylene-sensitive produce.",
    "banana": "Store at room temperature away from direct sunlight. Wrap stems in foil to slow ripening.",
    "bellpepper": "Refrigerate unwashed in a loose plastic bag. Keep dry to prevent moisture rot.",
    "bitter_gourd": "Wrap in paper towel and refrigerate at 7–10°C. Consume within 4-5 days.",
    "carrot": "Cut off green tops before storing. Keep in a plastic bag in the fridge crisper.",
    "cucumber": "Store in warmer part of fridge (around 10°C). Avoid storing near ethylene producers.",
    "mango": "Keep at room temp until soft and sweet, then refrigerate for up to 5 days.",
    "okra": "Refrigerate in a perforated paper bag. Keep dry; moisture causes rapid decay.",
    "orange": "Store at room temp for up to a week, or refrigerate in a mesh bag for up to 3 weeks.",
    "potato": "Store in a cool, dark, well-ventilated place. Never refrigerate or store near onions.",
    "strawberry": "Refrigerate in a single layer on paper towels. Wash only right before eating.",
    "tomato": "Keep stem-side down at room temperature away from sunlight. Avoid refrigerating unripened tomatoes.",
    "unknown": "Inspect carefully before consumption. Store in cool, dry environment.",
}


#attribute_inference.py
from typing import Dict, Optional

from constants import (
    CATEGORY_OPTIONS,
    COLOR_ALIASES,
    COLOR_OPTIONS,
    PATTERN_OPTIONS,
    ACCESSORY_TYPE_OPTIONS,
)


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def infer_color_from_name(name: str) -> Optional[str]:
    from constants import COLOR_ALIASES, COLOR_OPTIONS

    text = normalize_text(name)

    # Buscar primero cualquier coincidencia de texto y normalizar con la función estándar
    for alias in sorted(COLOR_ALIASES.keys(), key=len, reverse=True):
        if alias in text:
            normalized = COLOR_ALIASES.get(alias)
            if normalized in COLOR_OPTIONS:
                return normalized

    # Luego colores oficiales (también priorizando largos)
    for color in sorted(COLOR_OPTIONS, key=len, reverse=True):
        if color in text:
            return color

    return None


def infer_pattern_from_name(name: str) -> Optional[str]:
    text = normalize_text(name)

    pattern_keywords = {
        "animal_print": [
            "animal print", "animal", "leopardo", "leopard", "zebra", "cebra",
            "snake", "serpiente", "piton", "pitón"
        ],
        "floral": [
            "floral", "floreada", "flores", "flower"
        ],
        "rayas": [
            "rayas", "rayada", "rayado", "striped", "stripe"
        ],
        "cuadros": [
            "cuadros", "cuadrillé", "cuadriculado", "tartan", "plaid"
        ],
        "grafico": [
            "grafico", "gráfico", "print", "estampado grafico", "estampado gráfico"
        ],
        "estampado": [
            "estampado", "estampada"
        ],
        "liso": [
            "liso", "lisa", "basica", "básica", "basico", "básico"
        ],
    }

    for pattern, keywords in pattern_keywords.items():
        if pattern not in PATTERN_OPTIONS:
            continue
        for keyword in keywords:
            if keyword in text:
                return pattern

    return None


def infer_category_from_name(name: str) -> Optional[str]:
    text = normalize_text(name)

    category_keywords = {
        "one_piece": [
            "vestido", "enterito", "mono", "jumpsuit", "overall"
        ],
        "top": [
            "polera", "camiseta", "remera", "top", "blusa", "camisa",
            "body", "crop top", "camiseta", "beatle", "tank", "musculosa"
        ],
        "midlayer": [
            "blazer", "cardigan", "cárdigan", "chaleco", "sweater", "sueter",
            "suéter", "tejido"
        ],
        "outerwear": [
            "chaqueta", "abrigo", "parka", "impermeable", "trench",
            "cortaviento", "anorak", "polar"
        ],
        "bottom": [
            "jeans", "pantalon", "pantalón", "falda", "short", "shorts",
            "calza", "leggings", "buzo", "palazzo", "mini", "minifalda"
        ],
        "shoes": [
            "zapatillas", "zapatilla", "zapatos", "zapato", "botines",
            "botin", "botín", "botas", "bota", "sandalias", "sandalia",
            "mocasines", "mocasín", "mocasin", "tacos", "taco"
        ],
        "accessory": [
            "reloj", "collar", "pulsera", "anillo", "aros", "cinturon",
            "cinturón", "bolso", "cartera", "bufanda", "pañuelo",
            "gorro", "guantes", "lentes"
        ],
    }

    for category, keywords in category_keywords.items():
        if category not in CATEGORY_OPTIONS:
            continue
        for keyword in keywords:
            if keyword in text:
                return category

    return None


def infer_accessory_type_from_name(name: str) -> Optional[str]:
    text = normalize_text(name)

    mapping = {
        "reloj": ["reloj"],
        "collar": ["collar"],
        "pulsera": ["pulsera", "brazalete"],
        "anillo": ["anillo"],
        "aros": ["aros", "aretes"],
        "cinturón": ["cinturon", "cinturón"],
        "bolso": ["bolso", "cartera"],
        "bufanda": ["bufanda"],
        "pañuelo": ["pañuelo", "panuelo"],
        "gorro": ["gorro", "beanie"],
        "guantes": ["guantes", "guante"],
    }

    for accessory_type, keywords in mapping.items():
        if accessory_type not in ACCESSORY_TYPE_OPTIONS:
            continue
        for keyword in keywords:
            if keyword in text:
                return accessory_type

    return None


def infer_waterproof_from_name(name: str) -> Optional[bool]:
    text = normalize_text(name)

    waterproof_keywords = [
        "impermeable", "waterproof", "rain", "lluvia", "cortaviento"
    ]

    for keyword in waterproof_keywords:
        if keyword in text:
            return True

    return None


def infer_warmth_from_name(name: str) -> Optional[str]:
    text = normalize_text(name)

    cold_keywords = [
        "abrigo", "parka", "polar", "bufanda", "guantes", "gorro",
        "sweater grueso", "chaleco grueso"
    ]
    hot_keywords = [
        "polera", "top", "crop top", "musculosa", "tank", "short", "shorts"
    ]

    for keyword in cold_keywords:
        if keyword in text:
            return "frio"

    for keyword in hot_keywords:
        if keyword in text:
            return "caluroso"

    return None


def infer_attributes_from_name(name: str) -> Dict[str, Optional[object]]:
    inferred_category = infer_category_from_name(name)
    inferred_accessory_type = infer_accessory_type_from_name(name)

    # Si se detecta tipo de accesorio, reforzar categoría
    if inferred_accessory_type:
        inferred_category = "accessory"

    return {
        "category": inferred_category,
        "pattern": infer_pattern_from_name(name),
        "color": infer_color_from_name(name),
        "waterproof": infer_waterproof_from_name(name),
        "warmth": infer_warmth_from_name(name),
        "accessory_type": inferred_accessory_type,
    }

import os
import re


def suggest_name_from_filename(filename: str) -> str:
    if not filename:
        return ""

    name = filename.lower()

    # quitar extensión
    name = os.path.splitext(name)[0]

    # reemplazar separadores por espacio
    name = re.sub(r"[_\-]+", " ", name)

    # limpiar patrones típicos tipo IMG_1234
    name = re.sub(r"\bimg\s*\d+\b", "", name)
    name = re.sub(r"\b\d{3,}\b", "", name)

    name = name.strip()

    # fallback
    if len(name) < 3:
        return ""

    return name
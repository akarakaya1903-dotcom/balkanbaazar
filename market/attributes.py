# -*- coding: utf-8 -*-
"""Kategoriye ozel ilan alanlari (arac: marka/model/yil/km, emlak: oda/m2 vb.), formlar ve filtreler icin."""

# alan: (anahtar, tur, secenekler)  tur: text | number | select
SCHEMA = {
    "vasita": [],  # attributes_vehicle.py ile doldurulur
    "emlak": [("deal", "select", ["sale", "rent"]), ("rooms", "select", ["1+0", "1+1", "2+1", "3+1", "4+1", "5+"]),
              ("m2", "number", None), ("floor", "number", None)],
    "elektronik": [("brand", "text", None), ("model", "text", None)],
    "giyim": [("brand", "text", None), ("size", "text", None)],
    "moda": [("brand", "text", None), ("size", "text", None)],
    "is-ilanlari": [("job_type", "select", ["fulltime", "parttime", "remote"])],
    "oto-yapi": [("brand", "text", None)],
}

LANGS = ["tr", "en", "mk", "sq", "sr", "bg", "el", "bs"]
_L = lambda *v: dict(zip(LANGS, v))
LABELS = {
    "brand": _L("Marka", "Brand", "Марка", "Marka", "Марка", "Марка", "Μάρκα", "Marka"),
    "model": _L("Model", "Model", "Модел", "Modeli", "Модел", "Модел", "Μοντέλο", "Model"),
    "year": _L("Yıl", "Year", "Година", "Viti", "Година", "Година", "Έτος", "Godina"),
    "km": _L("Kilometre", "Mileage (km)", "Километри", "Kilometra", "Километара", "Километри", "Χιλιόμετρα", "Kilometraža"),
    "fuel": _L("Yakıt", "Fuel", "Гориво", "Karburanti", "Гориво", "Гориво", "Καύσιμο", "Gorivo"),
    "gearbox": _L("Vites", "Gearbox", "Менувач", "Marshi", "Мењач", "Скоростна кутия", "Κιβώτιο", "Mjenjač"),
    "deal": _L("İlan türü", "Type", "Тип", "Lloji", "Врста", "Вид", "Τύπος", "Vrsta"),
    "rooms": _L("Oda sayısı", "Rooms", "Соби", "Dhoma", "Собе", "Стаи", "Δωμάτια", "Sobe"),
    "m2": _L("Metrekare (m²)", "Area (m²)", "Квадратура (m²)", "Sipërfaqja (m²)", "Квадратура (m²)", "Квадратура (m²)", "Εμβαδόν (m²)", "Kvadratura (m²)"),
    "floor": _L("Kat", "Floor", "Кат", "Kati", "Спрат", "Етаж", "Όροφος", "Sprat"),
    "size": _L("Beden", "Size", "Големина", "Madhësia", "Величина", "Размер", "Μέγεθος", "Veličina"),
    "job_type": _L("Çalışma şekli", "Job type", "Вид работа", "Lloji i punës", "Врста посла", "Вид работа", "Τύπος εργασίας", "Vrsta posla"),
    "attrs_title": _L("Özellikler", "Details", "Карактеристики", "Detajet", "Карактеристике", "Характеристики", "Χαρακτηριστικά", "Karakteristike"),
    "any": _L("Hepsi", "Any", "Сите", "Të gjitha", "Све", "Всички", "Όλα", "Sve"),
}
CHOICES = {
    "petrol": _L("Benzin", "Petrol", "Бензин", "Benzinë", "Бензин", "Бензин", "Βενζίνη", "Benzin"),
    "diesel": _L("Dizel", "Diesel", "Дизел", "Naftë", "Дизел", "Дизел", "Πετρέλαιο", "Dizel"),
    "lpg": _L("LPG", "LPG", "ТНГ", "LPG", "ТНГ", "Газ", "LPG", "LPG"),
    "hybrid": _L("Hibrit", "Hybrid", "Хибрид", "Hibrid", "Хибрид", "Хибрид", "Υβριδικό", "Hibrid"),
    "electric": _L("Elektrik", "Electric", "Електричен", "Elektrik", "Електрични", "Електрически", "Ηλεκτρικό", "Električni"),
    "manual": _L("Manuel", "Manual", "Мануелен", "Manual", "Мануелни", "Ръчна", "Χειροκίνητο", "Manuelni"),
    "automatic": _L("Otomatik", "Automatic", "Автоматски", "Automatik", "Аутоматски", "Автоматична", "Αυτόματο", "Automatski"),
    "sale": _L("Satılık", "For sale", "Продажба", "Në shitje", "Продаја", "Продава се", "Πώληση", "Prodaja"),
    "rent": _L("Kiralık", "For rent", "Изнајмување", "Me qira", "Изнајмљивање", "Под наем", "Ενοικίαση", "Iznajmljivanje"),
    "fulltime": _L("Tam zamanlı", "Full-time", "Полно работно време", "Kohë e plotë", "Пуно радно време", "Пълно работно време", "Πλήρης απασχόληση", "Puno radno vrijeme"),
    "parttime": _L("Yarı zamanlı", "Part-time", "Скратено работно време", "Kohë e pjesshme", "Скраћено радно време", "Непълно работно време", "Μερική απασχόληση", "Skraćeno radno vrijeme"),
    "remote": _L("Uzaktan", "Remote", "Од далечина", "Në distancë", "Рад на даљину", "Дистанционно", "Εξ αποστάσεως", "Rad na daljinu"),
}
_FALL = {"hr": "bs", "cnr": "bs"}

from . import attributes_vehicle as _V  # noqa: E402
SCHEMA["vasita"] = _V.SCHEMA_VASITA
LABELS.update({k: v for k, v in _V.LABELS.items() if k not in LABELS})
CHOICES.update({k: v for k, v in _V.CHOICES.items() if k not in CHOICES})
GROUPS = {"vasita": _V.GROUPS}
FILTER_OFF = {k for g, keys, ok in _V.GROUPS if not ok for k in keys}  # filtre cubugunda gosterilmeyenler


def _pick(table, key, lang):
    d = table.get(key, {})
    return d.get(lang) or d.get(_FALL.get(lang, "en")) or d.get("en") or key


def label(key, lang):
    return _pick(LABELS, key, lang)


def choice_label(code, lang):
    return _pick(CHOICES, code, lang) if code in CHOICES else code


def root_slug(category):
    if not category:
        return ""
    return (category.parent.slug if category.parent_id else category.slug)


def fields_for(root):
    return SCHEMA.get(root, [])


def all_keys():
    """Tum kategorilerde gecen alanlar: anahtar -> (tur, secenekler, [kategori slug'lari])."""
    out = {}
    for slug, fields in SCHEMA.items():
        for key, kind, choices in fields:
            kind0, ch0, cats = out.get(key, (kind, choices, []))
            out[key] = (kind0, ch0, cats + [slug])
    return out


def clean_attrs(root, data):
    """Form verisinden yalnizca o kategoriye ait ve dolu alanlari alir."""
    attrs = {}
    for key, kind, choices in fields_for(root):
        value = data.get("attr_" + key)
        if kind == "multi":
            vals = [v for v in (value or []) if v in (choices or [])]
            if vals:
                attrs[key] = vals
            continue
        if value in (None, ""):
            continue
        attrs[key] = int(value) if kind == "number" else str(value).strip()
    return attrs


def display_rows(item, lang):
    """Ilan sayfasi icin [(etiket, deger)]."""
    root = root_slug(item.category)
    rows = []
    for key, kind, choices in fields_for(root):
        value = (item.attrs or {}).get(key)
        if value in (None, "") or kind == "multi":
            continue
        rows.append((label(key, lang), choice_label(str(value), lang) if kind == "select" else value))
    return rows


def display_sections(item, lang):
    """Ilan sayfasi icin bolumler: [(baslik, "table"|"tags", [(etiket, deger)] | [etiket])]."""
    root = root_slug(item.category)
    attrs = item.attrs or {}
    fields = {k: (kind, ch) for k, kind, ch in fields_for(root)}
    groups = GROUPS.get(root) or [("attrs_title", [k for k in fields], True)]
    tables, tags_out = [], []
    for title_key, keys, _ok in groups:
        rows = []
        for key in keys:
            kind, ch = fields[key]
            value = attrs.get(key)
            if value in (None, "", []):
                continue
            if kind == "multi":
                tags = [choice_label(str(v), lang) for v in value if v in (ch or [])]
                if tags:
                    tags_out.append((label(key, lang), "tags", tags))
            else:
                rows.append((label(key, lang), choice_label(str(value), lang) if kind == "select" else value))
        if rows:
            tables.append((label(title_key, lang), "table", rows))
    return tables + tags_out


def filter_specs(root, params, lang):
    """Kenar cubuk filtreleri icin alan tanimlari ve mevcut degerler."""
    specs = []
    for key, kind, choices in fields_for(root):
        if kind == "multi" or key in FILTER_OFF:
            continue
        spec = {"key": key, "kind": kind, "label": label(key, lang)}
        if kind == "select":
            spec["choices"] = [(c, choice_label(c, lang)) for c in choices]
            spec["value"] = params.get("a_" + key, "")
        elif kind == "number":
            spec["min"] = params.get("a_%s_min" % key, "")
            spec["max"] = params.get("a_%s_max" % key, "")
        else:
            spec["value"] = params.get("a_" + key, "")
        specs.append(spec)
    return specs


def apply_filters(qs, root, params):
    """a_<anahtar>, a_<anahtar>_min / _max parametrelerini sorguya uygular."""
    for key, kind, choices in fields_for(root):
        if kind == "multi" or key in FILTER_OFF:
            continue
        if kind == "number":
            for suffix, op in (("min", "gte"), ("max", "lte")):
                raw = params.get("a_%s_%s" % (key, suffix), "")
                if raw:
                    try:
                        qs = qs.filter(**{"attrs__%s__%s" % (key, op): int(raw)})
                    except ValueError:
                        pass
        else:
            raw = params.get("a_" + key, "").strip()
            if raw:
                qs = qs.filter(**{"attrs__%s__iexact" % key: raw})
    return qs


def param_pairs(root, params):
    """Siralama formunda filtrelerin korunmasi icin gizli alanlar."""
    pairs = []
    for key, kind, choices in fields_for(root):
        if kind == "multi" or key in FILTER_OFF:
            continue
        names = ["a_%s_min" % key, "a_%s_max" % key] if kind == "number" else ["a_" + key]
        for n in names:
            if params.get(n):
                pairs.append((n, params.get(n)))
    return pairs

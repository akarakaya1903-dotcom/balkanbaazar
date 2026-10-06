# -*- coding: utf-8 -*-
"""Kategori simgeleri: duz cizgili SVG'ler + pastel renk tonlari (emoji yerine, daha profesyonel gorunum)."""

ICONS = {
    "auto": '<path d="M5 19l2.5-7a2 2 0 0 1 1.9-1.4h13.2a2 2 0 0 1 1.9 1.4L27 19v6H5zM5 19h22"/><circle cx="10" cy="22" r="1.5"/><circle cx="22" cy="22" r="1.5"/>',
    "realestate": '<rect x="8" y="5" width="16" height="22"/><path d="M12 10h2M18 10h2M12 15h2M18 15h2M12 20h2M18 20h2M14 27v-4h4v4"/>',
    "electronics": '<rect x="5" y="8" width="22" height="14" rx="2"/><path d="M2 26h28"/>',
    "home": '<path d="M4 15 16 5l12 10M7 13v14h18V13M13 27v-8h6v8"/>',
    "fashion": '<path d="M11 5 4 9l3 5 3-1.5V27h12V12.5L25 14l3-5-7-4c-.5 2-2.5 3.5-5 3.5S11.5 7 11 5z"/>',
    "baby": '<rect x="11" y="12" width="10" height="16" rx="3"/><rect x="13" y="7" width="6" height="5" rx="1"/><path d="M16 3v4M11 19h10"/>',
    "sport": '<circle cx="16" cy="16" r="11"/><path d="M5 16h22M16 5c4 3 4 19 0 22M16 5c-4 3-4 19 0 22"/>',
    "services": '<path d="M21 5a6 6 0 0 0-6 8L5 23a2.8 2.8 0 0 0 4 4l10-10a6 6 0 0 0 8-6l-4 4-4-1-1-4 4-4z"/>',
    "briefcase": '<rect x="4" y="10" width="24" height="16" rx="3"/><path d="M12 10V8a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M4 18h24"/>',
    "pets": '<circle cx="9" cy="13" r="2.5"/><circle cx="14" cy="8" r="2.5"/><circle cx="20" cy="8" r="2.5"/><circle cx="25" cy="13" r="2.5"/><path d="M16 15c-5 0-8 4-8 7 0 3 3 4 5 3.5 2-.5 4-.5 6 0 2 .5 5-.5 5-3.5 0-3-3-7-8-7z"/>',
    "beauty": '<rect x="12" y="17" width="8" height="10" rx="1.5"/><rect x="13" y="12" width="6" height="5"/><path d="M13 12l6-7v7"/>',
    "grocery": '<path d="M4 12h24l-3 14H7zM11 12l4-7M21 12l-4-7"/>',
    "book": '<path d="M6 6h14a4 4 0 0 1 4 4v16H10a4 4 0 0 1-4-4V6zM6 22a4 4 0 0 1 4-4h14"/>',
    "compass": '<circle cx="16" cy="16" r="11"/><path d="M21 11l-3 8-8 3 3-8z"/>',
    "tag": '<path d="M4 16V5h11l13 13-11 11zM10 10h.01"/>',
}

# (arka plan, simge rengi)
TONES = {
    "auto": ("#DBEAFE", "#1D4ED8"), "realestate": ("#D1FAE5", "#047857"), "electronics": ("#E0F2FE", "#0369A1"),
    "home": ("#FEF3C7", "#B45309"), "fashion": ("#FCE7F3", "#DB2777"), "baby": ("#EDE9FE", "#6D28D9"),
    "sport": ("#FFEDD5", "#C2410C"), "services": ("#E2E8F0", "#475569"), "briefcase": ("#E0E7FF", "#4338CA"),
    "pets": ("#FFE8CC", "#9A3412"), "beauty": ("#FFE4E6", "#BE123C"), "grocery": ("#ECFCCB", "#4D7C0F"),
    "book": ("#FDE68A", "#92400E"), "compass": ("#CFFAFE", "#0E7490"), "tag": ("#E5E7EB", "#374151"),
}

SLUG_ICON = {
    # ikinci el
    "vasita": "auto", "emlak": "realestate", "elektronik": "electronics", "ev-yasam": "home", "giyim": "fashion",
    "anne-bebek": "baby", "hobi-spor": "sport", "is-sanayi": "services", "is-ilanlari": "briefcase", "hayvanlar": "pets",
    # magaza
    "moda": "fashion", "ev-mobilya": "home", "kozmetik": "beauty", "market": "grocery", "spor": "sport",
    "oto-yapi": "auto", "kitap-hobi": "book", "evcil-hayvan": "pets", "turizm": "compass", "arac-kiralama": "auto",
}

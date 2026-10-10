# -*- coding: utf-8 -*-
"""Vasita disindaki tum kategoriler icin detayli ilan alanlari. Diller: tr|en|mk|sq|sr|bg|el|bs"""
from .attributes_vehicle import _table

LABELS = _table("""
storage_gb=Depolama (GB)|Storage (GB)|Меморија (GB)|Memoria (GB)|Меморија (GB)|Памет (GB)|Αποθήκευση (GB)|Memorija (GB)
ram_gb=RAM (GB)
screen_in=Ekran boyutu (inç)|Screen size (in)|Големина на екран (инчи)|Madhësia e ekranit (inç)|Величина екрана (инчи)|Размер на екрана (инча)|Μέγεθος οθόνης (ίντσες)|Veličina ekrana (inča)
processor=İşlemci|Processor|Процесор|Procesori|Процесор|Процесор|Επεξεργαστής|Procesor
camera_mp=Kamera (MP)|Camera (MP)|Камера (MP)|Kamera (MP)|Камера (MP)|Камера (MP)|Κάμερα (MP)|Kamera (MP)
front_cam_mp=Ön kamera (MP)|Front camera (MP)|Предна камера (MP)|Kamera e përparme (MP)|Предња камера (MP)|Предна камера (MP)|Μπροστινή κάμερα (MP)|Prednja kamera (MP)
os=İşletim sistemi|Operating system|Оперативен систем|Sistemi operativ|Оперативни систем|Операционна система|Λειτουργικό σύστημα|Operativni sistem
origin=Alındığı yer|Purchased from|Купено од|Blerë nga|Купљено од|Купено от|Αγορά από|Kupljeno od
warranty_type=Garanti|Warranty|Гаранција|Garancia|Гаранција|Гаранция|Εγγύηση|Garancija
material=Malzeme|Material|Материјал|Materiali|Материјал|Материал|Υλικό|Materijal
dimensions=Ölçüler|Dimensions|Димензии|Përmasat|Димензије|Размери|Διαστάσεις|Dimenzije
gender=Cinsiyet|Gender|Пол|Gjinia|Пол|Пол|Φύλο|Spol
age_group=Yaş grubu|Age group|Возрасна група|Grupmosha|Узрасна група|Възрастова група|Ηλικιακή ομάδα|Dobna skupina
author=Yazar|Author|Автор|Autori|Аутор|Автор|Συγγραφέας|Autor
publisher=Yayınevi|Publisher|Издавач|Botuesi|Издавач|Издател|Εκδότης|Izdavač
language=Dil|Language|Јазик|Gjuha|Језик|Език|Γλώσσα|Jezik
position=Pozisyon|Position|Позиција|Pozicioni|Позиција|Позиция|Θέση|Pozicija
experience=Deneyim|Experience|Искуство|Përvoja|Искуство|Опит|Εμπειρία|Iskustvo
education=Eğitim|Education|Образование|Arsimi|Образовање|Образование|Εκπαίδευση|Obrazovanje
salary=Maaş|Salary|Плата|Paga|Плата|Заплата|Μισθός|Plata
species=Tür|Species|Вид|Lloji|Врста|Вид|Είδος|Vrsta
breed=Cins|Breed|Раса|Raca|Раса|Порода|Ράτσα|Rasa
pet_age=Yaş|Age|Возраст|Mosha|Узраст|Възраст|Ηλικία|Starost
pet_gender=Cinsiyet|Gender|Пол|Gjinia|Пол|Пол|Φύλο|Spol
vaccinated=Aşıları yapılmış|Vaccinated|Вакцинирано|I vaksinuar|Вакцинисано|Ваксинирано|Εμβολιασμένο|Vakcinisano
pet_for=Hayvan türü|For animal|За животно|Për kafshën|За животињу|За животно|Για ζώο|Za životinju
volume=Hacim / miktar|Volume / amount|Волумен / количина|Vëllimi / sasia|Запремина / количина|Обем / количество|Όγκος / ποσότητα|Zapremina / količina
expiry=Son kullanma tarihi|Expiry date|Рок на траење|Data e skadimit|Рок трајања|Годен до|Ημερομηνία λήξης|Rok trajanja
origin_country=Menşei|Origin|Потекло|Origjina|Порекло|Произход|Προέλευση|Porijeklo
part_no=Parça no|Part number|Број на дел|Numri i pjesës|Број дела|Номер на част|Αριθμός ανταλλακτικού|Broj dijela
compatible=Uyumlu araç|Compatible vehicle|Компатибилно возило|Automjet i përputhshëm|Компатибилно возило|Съвместим автомобил|Συμβατό όχημα|Kompatibilno vozilo
property_type=Emlak tipi|Property type|Тип на недвижнина|Lloji i pronës|Тип некретнине|Вид имот|Τύπος ακινήτου|Vrsta nekretnine
building_age=Bina yaşı|Building age|Старост на зградата|Mosha e ndërtesës|Старост зграде|Възраст на сградата|Ηλικία κτιρίου|Starost zgrade
bathrooms=Banyo sayısı|Bathrooms|Бањи|Banjo|Купатила|Бани|Μπάνια|Kupatila
total_floors=Toplam kat|Total floors|Вкупно катови|Kate gjithsej|Укупно спратова|Общо етажи|Σύνολο ορόφων|Ukupno spratova
heating=Isıtma|Heating|Греење|Ngrohja|Грејање|Отопление|Θέρμανση|Grijanje
dues=Aidat / aylık gider|Monthly fees|Месечни трошоци|Tarifat mujore|Месечни трошкови|Месечни такси|Κοινόχρηστα|Mjesečni troškovi
seller_re=Kimden|Seller type|Од кого|Nga kush|Од кога|От кого|Πωλητής|Od koga
eq_re=Özellikler|Features|Карактеристики|Veçoritë|Карактеристике|Особености|Χαρακτηριστικά|Karakteristike
""")

CHOICES = _table("""
w_importer=İthalatçı garantili|Importer warranty|Гаранција од увозник|Garanci nga importuesi|Гаранција увозника|Гаранция от вносител|Εγγύηση εισαγωγέα|Garancija uvoznika
w_manufacturer=Üretici garantili|Manufacturer warranty|Гаранција од производител|Garanci nga prodhuesi|Гаранција произвођача|Гаранция от производител|Εγγύηση κατασκευαστή|Garancija proizvođača
w_none=Garantisiz|No warranty|Без гаранција|Pa garanci|Без гаранције|Без гаранция|Χωρίς εγγύηση|Bez garancije
o_local=Yurt içi|Domestic|Домашно|Vendase|Домаће|Местно|Εσωτερικό|Domaće
o_abroad=Yurt dışı|Abroad|Странство|Nga jashtë|Иностранство|Чужбина|Εξωτερικό|Inostranstvo
os_ios=iOS
os_android=Android
os_windows=Windows
os_macos=macOS
os_other=Diğer|Other|Друго|Tjetër|Друго|Друго|Άλλο|Drugo
g_female=Kadın|Women|Жени|Femra|Жене|Жени|Γυναικεία|Žene
g_male=Erkek|Men|Мажи|Meshkuj|Мушкарци|Мъже|Ανδρικά|Muškarci
g_unisex=Unisex|Unisex|Унисекс|Uniseks|Унисекс|Унисекс|Unisex|Uniseks
g_kids=Çocuk|Kids|Деца|Fëmijë|Деца|Деца|Παιδικά|Djeca
pg_female=Dişi|Female|Женско|Femër|Женка|Женско|Θηλυκό|Ženka
pg_male=Erkek|Male|Машко|Mashkull|Мужјак|Мъжко|Αρσενικό|Mužjak
exp_none=Deneyimsiz|No experience|Без искуство|Pa përvojë|Без искуства|Без опит|Χωρίς εμπειρία|Bez iskustva
exp_1_3=1–3 yıl|1–3 years|1–3 години|1–3 vjet|1–3 године|1–3 години|1–3 έτη|1–3 godine
exp_3_5=3–5 yıl|3–5 years|3–5 години|3–5 vjet|3–5 година|3–5 години|3–5 έτη|3–5 godina
exp_5=5+ yıl|5+ years|5+ години|5+ vjet|5+ година|5+ години|5+ έτη|5+ godina
re_apartment=Daire|Apartment|Стан|Apartament|Стан|Апартамент|Διαμέρισμα|Stan
re_house=Müstakil ev|House|Куќа|Shtëpi|Кућа|Къща|Μονοκατοικία|Kuća
re_villa=Villa|Villa|Вила|Vilë|Вила|Вила|Βίλα|Vila
re_land=Arsa|Land|Земјиште|Tokë|Земљиште|Парцел|Οικόπεδο|Zemljište
re_shop=İşyeri / dükkan|Commercial|Деловен простор|Hapësirë tregtare|Пословни простор|Търговски обект|Επαγγελματικός χώρος|Poslovni prostor
re_office=Ofis|Office|Канцеларија|Zyrë|Канцеларија|Офис|Γραφείο|Ured
h_central=Merkezi|Central|Централно|Qendrore|Централно|Централно|Κεντρική|Centralno
h_gas=Doğalgaz|Gas|Гас|Gaz|Гас|Газ|Φυσικό αέριο|Plin
h_stove=Soba|Stove|Печка|Sobë|Пећ|Печка|Σόμπα|Peć
h_ac=Klima|Air conditioner|Клима|Klimë|Клима|Климатик|Κλιματιστικό|Klima
h_none=Yok|None|Нема|Nuk ka|Нема|Няма|Κανένα|Nema
s_agent=Emlak ofisinden|From agency|Од агенција|Nga agjencia|Од агенције|От агенция|Από μεσιτικό|Iz agencije
r_balcony=Balkon|Balcony|Балкон|Ballkon|Балкон|Балкон|Μπαλκόνι|Balkon
r_elevator=Asansör|Elevator|Лифт|Ashensor|Лифт|Асансьор|Ασανσέρ|Lift
r_parking=Otopark|Parking|Паркинг|Parkim|Паркинг|Паркинг|Στάθμευση|Parking
r_garden=Bahçe|Garden|Градина|Kopsht|Башта|Градина|Κήπος|Vrt
r_pool=Havuz|Pool|Базен|Pishinë|Базен|Басейн|Πισίνα|Bazen
r_security=Güvenlik|Security|Обезбедување|Siguri|Обезбеђење|Охрана|Ασφάλεια|Osiguranje
r_furnished=Eşyalı|Furnished|Опремено|Me mobilje|Намештено|Обзаведено|Επιπλωμένο|Namješteno
r_fiber=İnternet / fiber|Internet / fiber|Интернет / оптика|Internet / fibër|Интернет / оптика|Интернет / оптика|Διαδίκτυο / οπτική ίνα|Internet / optika
""")

_COND = ("condition", "select", ["c_new", "c_used", "c_damaged"])
_SELLER = ("seller_type", "select", ["s_owner", "s_dealer"])
_SWAP = ("swap", "select", ["yes", "no"])
_COMMON = [_SELLER, _COND, _SWAP]
_T = lambda k: (k, "text", None)
_N = lambda k: (k, "number", None)
_COLOR = ("color", "select", ["col_black", "col_white", "col_silver", "col_grey", "col_red", "col_blue", "col_green",
                              "col_yellow", "col_brown", "col_orange", "col_beige", "col_other"])
_WARR = ("warranty_type", "select", ["w_importer", "w_manufacturer", "w_none"])
_GENDER = ("gender", "select", ["g_female", "g_male", "g_unisex", "g_kids"])

ELEKTRONIK = [_T("brand"), _T("model"), _COLOR, _N("storage_gb"), _N("ram_gb"), _T("screen_in"), _T("processor"),
              _N("camera_mp"), _N("front_cam_mp"),
              ("os", "select", ["os_ios", "os_android", "os_windows", "os_macos", "os_other"]),
              ("origin", "select", ["o_local", "o_abroad"]), _WARR] + _COMMON
HOME = [_T("brand"), _T("material"), _COLOR, _T("dimensions"), _WARR] + _COMMON
FASHION = [_T("brand"), _T("size"), _GENDER, _COLOR, _T("material")] + _COMMON
BABY = [_T("brand"), _T("age_group"), _GENDER, _COLOR] + _COMMON
HOBBY = [_T("brand"), _T("size"), _COLOR] + _COMMON
BOOK = [_T("author"), _T("publisher"), _T("language"), _N("year"), _COND, _SELLER, _SWAP]
BUSINESS = [_T("brand"), _T("model"), _N("year"), _WARR] + _COMMON
JOBS = [_T("position"), ("job_type", "select", ["fulltime", "parttime", "remote"]),
        ("experience", "select", ["exp_none", "exp_1_3", "exp_3_5", "exp_5"]), _T("education"), _T("salary")]
PETS = [_T("species"), _T("breed"), _T("pet_age"), ("pet_gender", "select", ["pg_female", "pg_male"]),
        ("vaccinated", "select", ["yes", "no"]), _SELLER, _SWAP]
PETSHOP = [_T("brand"), _T("pet_for"), _COND, _SELLER]
BEAUTY = [_T("brand"), _T("volume"), _GENDER, _COND, _SELLER]
MARKET = [_T("brand"), _T("volume"), _T("expiry"), _T("origin_country")]
AUTOPARTS = [_T("brand"), _T("model"), _T("part_no"), _T("compatible"), _WARR] + _COMMON
REALESTATE = [("deal", "select", ["sale", "rent"]),
              ("property_type", "select", ["re_apartment", "re_house", "re_villa", "re_land", "re_shop", "re_office"]),
              ("rooms", "select", ["1+0", "1+1", "2+1", "3+1", "4+1", "5+"]), _N("m2"), _N("floor"), _N("total_floors"),
              _N("building_age"), _N("bathrooms"),
              ("heating", "select", ["h_central", "h_gas", "h_stove", "h_ac", "h_none"]), _N("dues"),
              ("seller_re", "select", ["s_owner", "s_agent"]), _SWAP,
              ("eq_re", "multi", ["r_balcony", "r_elevator", "r_parking", "r_garden", "r_pool", "r_security",
                                  "r_furnished", "r_fiber"])]

SCHEMA = {"elektronik": ELEKTRONIK, "ev-yasam": HOME, "ev-mobilya": HOME, "giyim": FASHION, "moda": FASHION,
          "anne-bebek": BABY, "hobi-spor": HOBBY, "spor": HOBBY, "kitap-hobi": BOOK, "is-sanayi": BUSINESS,
          "is-ilanlari": JOBS, "hayvanlar": PETS, "evcil-hayvan": PETSHOP, "kozmetik": BEAUTY, "market": MARKET,
          "oto-yapi": AUTOPARTS, "emlak": REALESTATE}

# filtre cubugunda gosterilmeyecek (serbest metin) alanlar
FILTER_OFF = {"processor", "screen_in", "dimensions", "material", "age_group", "author", "publisher", "language",
              "position", "education", "salary", "species", "breed", "pet_age", "pet_for", "volume", "expiry",
              "origin_country", "part_no", "compatible", "storage_gb", "ram_gb", "camera_mp", "front_cam_mp",
              "dues", "bathrooms", "total_floors", "building_age"}


def groups():
    out = {}
    for root, fields in SCHEMA.items():
        info = [f[0] for f in fields if f[1] != "multi"]
        multi = [f[0] for f in fields if f[1] == "multi"]
        g = [("g_info", info, True)]
        if multi:
            g.append(("g_equip", multi, False))
        out[root] = g
    return out

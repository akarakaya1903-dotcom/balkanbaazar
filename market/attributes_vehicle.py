# -*- coding: utf-8 -*-
"""Vasita (arac) ilanlari icin genis alan seti: bilgi, teknik, boya/degisen, donanim gruplari. Diller: tr|en|mk|sq|sr|bg|el|bs"""

LANGS = ["tr", "en", "mk", "sq", "sr", "bg", "el", "bs"]


def _d(s):
    parts = s.split("|")
    if len(parts) == 1:
        parts = parts * 8
    assert len(parts) == 8, s
    return dict(zip(LANGS, parts))


def _table(text):
    out = {}
    for line in text.strip().splitlines():
        key, rest = line.split("=", 1)
        out[key.strip()] = _d(rest.strip())
    return out


LABELS = _table("""
series=Seri|Series|Серија|Seria|Серија|Серия|Σειρά|Serija
condition=Durum|Condition|Состојба|Gjendja|Стање|Състояние|Κατάσταση|Stanje
body=Kasa tipi|Body type|Тип на каросерија|Lloji i karrocerisë|Тип каросерије|Тип каросерия|Τύπος αμαξώματος|Tip karoserije
power_hp=Motor gücü (hp)|Engine power (hp)|Моќност (КС)|Fuqia (HP)|Снага (КС)|Мощност (к.с.)|Ισχύς (hp)|Snaga (KS)
engine_cc=Motor hacmi (cc)|Engine size (cc)|Зафатнина (cc)|Vëllimi i motorit (cc)|Запремина (cc)|Обем (cc)|Κυβισμός (cc)|Zapremina (cc)
drive=Çekiş|Drive|Погон|Tërheqja|Погон|Задвижване|Κίνηση|Pogon
color=Renk|Color|Боја|Ngjyra|Боја|Цвят|Χρώμα|Boja
warranty=Garanti|Warranty|Гаранција|Garancia|Гаранција|Гаранция|Εγγύηση|Garancija
heavy_damage=Ağır hasar kayıtlı|Heavily damaged|Тешко оштетено|I dëmtuar rëndë|Тешко оштећено|Тежко повреден|Βαριές ζημιές|Teško oštećen
plate=Plaka / Kayıt|Registration|Регистрација|Regjistrimi|Регистрација|Регистрация|Ταξινόμηση|Registracija
seller_type=Kimden|Seller type|Од кого|Nga kush|Од кога|От кого|Πωλητής|Od koga
swap=Takas|Swap|Замена|Këmbim|Замена|Замяна|Ανταλλαγή|Zamjena
accel=0-100 km/s hızlanma (sn)|0–100 km/h (s)|0–100 км/ч (с)|0–100 km/h (s)|0–100 км/х (с)|0–100 км/ч (с)|0–100 km/h (δλ)|0–100 km/h (s)
top_speed=Azami hız (km/s)|Top speed (km/h)|Максимална брзина (км/ч)|Shpejtësia maks. (km/h)|Максимална брзина (км/х)|Макс. скорост (км/ч)|Τελική ταχύτητα (km/h)|Maks. brzina (km/h)
cons_comb=Ortalama yakıt (lt/100 km)|Fuel, combined (l/100 km)|Потрошувачка, комб. (л/100 км)|Konsumi i përzier (l/100 km)|Потрошња, комб. (л/100 км)|Разход, комб. (л/100 км)|Κατανάλωση, μικτή (l/100 km)|Potrošnja, kombin. (l/100 km)
cons_city=Şehir içi yakıt (lt/100 km)|Fuel, city (l/100 km)|Потрошувачка, град (л/100 км)|Konsumi në qytet (l/100 km)|Потрошња, град (л/100 км)|Разход, град (л/100 км)|Κατανάλωση, πόλη (l/100 km)|Potrošnja, grad (l/100 km)
cons_hwy=Şehir dışı yakıt (lt/100 km)|Fuel, highway (l/100 km)|Потрошувачка, отворен пат (л/100 км)|Konsumi jashtë qytetit (l/100 km)|Потрошња, ван града (л/100 км)|Разход, извънградски (л/100 км)|Κατανάλωση, εθνική (l/100 km)|Potrošnja, van grada (l/100 km)
tank_l=Yakıt deposu (lt)|Fuel tank (l)|Резервоар (л)|Depozita (l)|Резервоар (л)|Резервоар (л)|Ρεζερβουάρ (l)|Rezervoar (l)
doors=Kapı sayısı|Doors|Врати|Dyer|Врата|Врати|Πόρτες|Vrata
seats=Koltuk sayısı|Seats|Седишта|Ulëse|Седишта|Седалки|Θέσεις|Sjedala
trunk_l=Bagaj hacmi (lt)|Trunk (l)|Багажник (л)|Bagazhi (l)|Пртљажник (л)|Багажник (л)|Χώρος αποσκευών (l)|Prtljažnik (l)
weight_kg=Boş ağırlık (kg)|Curb weight (kg)|Маса (кг)|Pesha (kg)|Маса (кг)|Маса (кг)|Βάρος (kg)|Masa (kg)
p_hood=Motor kaputu|Hood|Хауба|Kapaku i motorit|Хауба|Преден капак|Καπό|Hauba
p_roof=Tavan|Roof|Покрив|Çatia|Кров|Покрив|Οροφή|Krov
p_trunk=Bagaj kapağı|Trunk lid|Капак на багажник|Kapaku i bagazhit|Поклопац пртљажника|Заден капак|Πορτ-μπαγκάζ|Poklopac prtljažnika
p_fl_fender=Sol ön çamurluk|Front left fender|Преден лев блатобран|Krahu i përparmë i majtë|Предњи леви блатобран|Преден ляв калник|Μπροστινό αριστερό φτερό|Prednji lijevi blatobran
p_fr_fender=Sağ ön çamurluk|Front right fender|Преден десен блатобран|Krahu i përparmë i djathtë|Предњи десни блатобран|Преден десен калник|Μπροστινό δεξί φτερό|Prednji desni blatobran
p_rl_fender=Sol arka çamurluk|Rear left fender|Заден лев блатобран|Krahu i pasmë i majtë|Задњи леви блатобран|Заден ляв калник|Πίσω αριστερό φτερό|Stražnji lijevi blatobran
p_rr_fender=Sağ arka çamurluk|Rear right fender|Заден десен блатобран|Krahu i pasmë i djathtë|Задњи десни блатобран|Заден десен калник|Πίσω δεξί φτερό|Stražnji desni blatobran
p_fl_door=Sol ön kapı|Front left door|Предна лева врата|Dera e përparme e majtë|Предња лева врата|Предна лява врата|Μπροστινή αριστερή πόρτα|Prednja lijeva vrata
p_fr_door=Sağ ön kapı|Front right door|Предна десна врата|Dera e përparme e djathtë|Предња десна врата|Предна дясна врата|Μπροστινή δεξιά πόρτα|Prednja desna vrata
p_rl_door=Sol arka kapı|Rear left door|Задна лева врата|Dera e pasme e majtë|Задња лева врата|Задна лява врата|Πίσω αριστερή πόρτα|Stražnja lijeva vrata
p_rr_door=Sağ arka kapı|Rear right door|Задна десна врата|Dera e pasme e djathtë|Задња десна врата|Задна дясна врата|Πίσω δεξιά πόρτα|Stražnja desna vrata
p_front_bumper=Ön tampon|Front bumper|Преден браник|Parakolpi i përparmë|Предњи браник|Предна броня|Μπροστινός προφυλακτήρας|Prednji branik
p_rear_bumper=Arka tampon|Rear bumper|Заден браник|Parakolpi i pasmë|Задњи браник|Задна броня|Πίσω προφυλακτήρας|Stražnji branik
eq_safety=Güvenlik|Safety|Безбедност|Siguria|Безбедност|Безопасност|Ασφάλεια|Sigurnost
eq_interior=İç donanım|Interior|Ентериер|Brendshme|Ентеријер|Интериор|Εσωτερικό|Enterijer
eq_exterior=Dış donanım|Exterior|Екстериер|Jashtme|Екстеријер|Екстериор|Εξωτερικό|Eksterijer
eq_media=Multimedya|Multimedia|Мултимедија|Multimedia|Мултимедија|Мултимедия|Πολυμέσα|Multimedija
g_info=İlan bilgileri|Listing details|Информации за огласот|Detajet e shpalljes|Подаци о огласу|Информация за обявата|Στοιχεία αγγελίας|Podaci o oglasu
g_tech=Teknik özellikler|Technical specs|Технички спецификации|Specifikimet teknike|Техничке спецификације|Технически характеристики|Τεχνικά χαρακτηριστικά|Tehničke specifikacije
g_paint=Boya / Değişen|Paint / Replaced parts|Боја / Заменети делови|Bojë / Pjesë të ndërruara|Фарбање / Замењени делови|Боя / Сменени части|Βαφές / Αντικαταστάσεις|Farbanje / Zamijenjeni dijelovi
g_equip=Donanım|Equipment|Опрема|Pajisjet|Опрема|Оборудване|Εξοπλισμός|Oprema
""")

CHOICES = _table("""
yes=Evet|Yes|Да|Po|Да|Да|Ναι|Da
no=Hayır|No|Не|Jo|Не|Не|Όχι|Ne
c_new=Sıfır|New|Ново|I ri|Ново|Ново|Καινούργιο|Novo
c_used=İkinci el – iyi durumda|Used – good condition|Користено – добра состојба|I përdorur – gjendje e mirë|Половно – добро стање|Употребяван – добро състояние|Μεταχειρισμένο – καλή κατάσταση|Korišteno – dobro stanje
c_damaged=Hasarlı / kazalı|Damaged|Оштетено|I dëmtuar|Оштећено|Повреден|Κατεστραμμένο|Oštećeno
b_sedan=Sedan|Sedan|Седан|Sedan|Седан|Седан|Sedan|Sedan
b_hatch=Hatchback|Hatchback|Хечбек|Hatchback|Хечбек|Хечбек|Hatchback|Hatchback
b_wagon=Station Wagon|Station wagon|Караван|Karavan|Караван|Комби|Station wagon|Karavan
b_suv=SUV / Arazi|SUV|SUV|SUV|SUV|SUV / Джип|SUV|SUV
b_coupe=Coupe|Coupe|Купе|Kupe|Купе|Купе|Coupe|Coupe
b_cabrio=Cabrio|Convertible|Кабриолет|Kabriolet|Кабриолет|Кабрио|Cabrio|Kabriolet
b_van=Panelvan|Van|Комбе|Furgon|Комби|Ван|Van|Kombi
b_minivan=Minivan|Minivan|Миниван|Minivan|Миниван|Миниван|Minivan|Minivan
b_pickup=Pikap|Pickup|Пикап|Pickup|Пикап|Пикап|Pickup|Pickup
d_fwd=Önden çekiş|Front-wheel drive|Предно погон|Tërheqje e përparme|Предњи погон|Предно задвижване|Κίνηση εμπρός|Prednji pogon
d_rwd=Arkadan itiş|Rear-wheel drive|Задно погон|Tërheqje e pasme|Задњи погон|Задно задвижване|Κίνηση πίσω|Stražnji pogon
d_awd=4x4 / AWD|4x4 / AWD|4x4 / AWD|4x4 / AWD|4x4 / AWD|4x4 / AWD|4x4 / AWD|4x4 / AWD
pl_local=Yerli plaka|Local plates|Домашни таблички|Targa vendase|Домаће таблице|Местна регистрация|Τοπική ταξινόμηση|Domaće tablice
pl_foreign=Yabancı plaka|Foreign plates|Странски таблички|Targa të huaja|Стране таблице|Чуждестранна регистрация|Ξένη ταξινόμηση|Strane tablice
s_owner=Sahibinden|By owner|Од сопственик|Nga pronari|Од власника|От собственик|Από ιδιοκτήτη|Od vlasnika
s_dealer=Galeriden / Bayiden|From dealer|Од салон|Nga salloni|Из салона|От автокъща|Από αντιπροσωπεία|Iz salona
pt_original=Orijinal|Original|Оригинално|Origjinale|Оригинално|Оригинално|Αρχικό|Originalno
pt_painted=Boyalı|Painted|Лакирано|E lyer|Фарбано|Боядисано|Βαμμένο|Farbano
pt_local=Lokal boyalı|Locally painted|Локално лакирано|E lyer lokalisht|Локално фарбано|Локално боядисано|Τοπική βαφή|Lokalno farbano
pt_changed=Değişmiş|Replaced|Заменето|E ndërruar|Замењено|Сменено|Αντικατεστημένο|Zamijenjeno
col_black=Siyah|Black|Црна|E zezë|Црна|Черен|Μαύρο|Crna
col_white=Beyaz|White|Бела|E bardhë|Бела|Бял|Λευκό|Bijela
col_silver=Gümüş|Silver|Сребрена|Argjendi|Сребрна|Сребрист|Ασημί|Srebrna
col_grey=Gri|Grey|Сива|Gri|Сива|Сив|Γκρι|Siva
col_red=Kırmızı|Red|Црвена|E kuqe|Црвена|Червен|Κόκκινο|Crvena
col_blue=Mavi|Blue|Сина|Blu|Плава|Син|Μπλε|Plava
col_green=Yeşil|Green|Зелена|E gjelbër|Зелена|Зелен|Πράσινο|Zelena
col_yellow=Sarı|Yellow|Жолта|E verdhë|Жута|Жълт|Κίτρινο|Žuta
col_brown=Kahverengi|Brown|Кафена|Kafe|Браон|Кафяв|Καφέ|Smeđa
col_orange=Turuncu|Orange|Портокалова|Portokalli|Наранџаста|Оранжев|Πορτοκαλί|Narandžasta
col_beige=Bej|Beige|Беж|Bezhë|Беж|Бежов|Μπεζ|Bež
col_other=Diğer|Other|Друга|Tjetër|Друга|Друг|Άλλο|Druga
e_abs=ABS
e_esp=ESP
e_tc=Çekiş kontrolü|Traction control|Контрола на влечење|Kontrolli i tërheqjes|Контрола вуче|Контрол на сцеплението|Έλεγχος πρόσφυσης|Kontrola trakcije
e_airbag=Hava yastığı (sürücü/yolcu)|Airbags (driver/passenger)|Воздушни перничиња (возач/сопатник)|Airbag (shoferi/pasagjeri)|Ваздушни јастуци (возач/сувозач)|Въздушни възглавници (шофьор/пасажер)|Αερόσακοι (οδηγού/συνοδηγού)|Zračni jastuci (vozač/suvozač)
e_side_airbag=Yan hava yastığı|Side airbags|Странични воздушни перничиња|Airbag anësorë|Бочни ваздушни јастуци|Странични въздушни възглавници|Πλευρικοί αερόσακοι|Bočni zračni jastuci
e_isofix=ISOFIX
e_park_sensor=Park sensörü|Parking sensors|Парк сензори|Sensorë parkimi|Парк сензори|Парктроник|Αισθητήρες στάθμευσης|Parking senzori
e_rear_cam=Geri görüş kamerası|Rear camera|Задна камера|Kamera e pasme|Задња камера|Камера за задно виждане|Κάμερα οπισθοπορείας|Stražnja kamera
e_cruise=Hız sabitleyici|Cruise control|Темпомат|Cruise control|Темпомат|Круиз контрол|Cruise control|Tempomat
e_lane=Şerit takip sistemi|Lane assist|Асистент за лента|Asistent i korsisë|Асистент за траку|Асистент за лента|Υποβοήθηση λωρίδας|Asistent za traku
e_alarm=Alarm|Alarm|Аларм|Alarm|Аларм|Аларма|Συναγερμός|Alarm
e_immo=Immobilizer|Immobiliser|Имобилајзер|Imobilizer|Имобилајзер|Имобилайзер|Immobilizer|Imobilajzer
e_leather=Deri döşeme|Leather seats|Кожни седишта|Ulëse prej lëkure|Кожна седишта|Кожен салон|Δερμάτινα καθίσματα|Kožna sjedala
e_heat_seat=Isıtmalı koltuk|Heated seats|Греени седишта|Ulëse të ngrohura|Грејана седишта|Загряване на седалките|Θερμαινόμενα καθίσματα|Grijana sjedala
e_el_seat=Elektrikli koltuk|Power seats|Електрични седишта|Ulëse elektrike|Електрична седишта|Електрически седалки|Ηλεκτρικά καθίσματα|Električna sjedala
e_sunroof=Sunroof|Sunroof|Шибедах|Çati e hapur|Шибер|Люк|Ηλιοροφή|Šiber
e_pano=Panoramik cam tavan|Panoramic roof|Панорамски покрив|Çati panoramike|Панорамски кров|Панорамен покрив|Πανοραμική οροφή|Panoramski krov
e_climate=Otomatik klima|Automatic climate control|Автоматска клима|Klimë automatike|Аутоматска клима|Автоматичен климатик|Αυτόματος κλιματισμός|Automatska klima
e_ac=Klima|Air conditioning|Клима|Klimë|Клима|Климатик|Κλιματισμός|Klima
e_pwin=Elektrikli cam|Power windows|Електрични прозорци|Dritare elektrike|Електрични прозори|Електрически стъкла|Ηλεκτρικά παράθυρα|Električni prozori
e_keyless=Anahtarsız giriş|Keyless entry|Влез без клуч|Hyrje pa çelës|Улаз без кључа|Достъп без ключ|Είσοδος χωρίς κλειδί|Ulaz bez ključa
e_steer_ctl=Direksiyon kumandaları|Steering wheel controls|Команди на воланот|Komanda në timon|Команде на волану|Управление от волана|Χειριστήρια τιμονιού|Komande na volanu
e_alloy=Alaşım jant|Alloy wheels|Алуминиумски фелни|Disqe alumini|Алуминијумске фелне|Алуминиеви джанти|Ζάντες αλουμινίου|Aluminijski naplatci
e_led=Xenon / LED far|Xenon / LED headlights|Ксенон / LED фарови|Fara xenon / LED|Ксенон / LED фарови|Ксенон / LED фарове|Φώτα Xenon / LED|Xenon / LED farovi
e_fog=Sis farı|Fog lights|Фарови за магла|Drita mjegulle|Фарови за маглу|Халогени|Προβολείς ομίχλης|Maglenke
e_rails=Tavan çıtası|Roof rails|Рејлинг|Shina çatie|Рејлинг|Надлъжни греди|Ράγες οροφής|Krovni nosači
e_tow=Çeki demiri|Tow bar|Кука за влекење|Grepi tërheqës|Кука за вучу|Теглич|Κοτσαδόρος|Kuka za vuču
e_tint=Cam filmi|Tinted windows|Затемнети стакла|Xhama të errësuar|Затамњена стакла|Затъмнени стъкла|Φιμέ τζάμια|Zatamnjena stakla
e_el_mirror=Elektrikli ayna|Power mirrors|Електрични ретровизори|Pasqyra elektrike|Електрична огледала|Електрически огледала|Ηλεκτρικοί καθρέφτες|Električna ogledala
e_rain=Yağmur sensörü|Rain sensor|Сензор за дожд|Sensor shiu|Сензор кише|Сензор за дъжд|Αισθητήρας βροχής|Senzor kiše
e_spoiler=Spoiler|Spoiler|Спојлер|Spoiler|Спојлер|Спойлер|Αεροτομή|Spojler
e_bt=Bluetooth
e_usb=USB / AUX
e_nav=Navigasyon|Navigation|Навигација|Navigacion|Навигација|Навигация|Πλοήγηση|Navigacija
e_carplay=Apple CarPlay / Android Auto
e_touch=Dokunmatik ekran|Touchscreen|Екран на допир|Ekran me prekje|Екран осетљив на додир|Сензорен екран|Οθόνη αφής|Ekran osjetljiv na dodir
e_audio=Premium ses sistemi|Premium sound system|Премиум аудио систем|Sistem audio premium|Премијум аудио систем|Премиум аудио система|Σύστημα ήχου premium|Premium audio sistem
e_radio=Radyo / CD|Radio / CD|Радио / CD|Radio / CD|Радио / CD|Радио / CD|Ραδιόφωνο / CD|Radio / CD
e_hud=Head-up ekran|Head-up display|Head-up дисплеј|Head-up display|Head-up дисплеј|Head-up дисплей|Head-up display|Head-up display
""")

_YN = ["yes", "no"]
_PAINT = ["pt_original", "pt_painted", "pt_local", "pt_changed"]
_PARTS = ["p_hood", "p_roof", "p_trunk", "p_fl_fender", "p_fr_fender", "p_rl_fender", "p_rr_fender",
          "p_fl_door", "p_fr_door", "p_rl_door", "p_rr_door", "p_front_bumper", "p_rear_bumper"]
_COLORS = ["col_black", "col_white", "col_silver", "col_grey", "col_red", "col_blue", "col_green",
           "col_yellow", "col_brown", "col_orange", "col_beige", "col_other"]
_EQ = {
    "eq_safety": ["e_abs", "e_esp", "e_tc", "e_airbag", "e_side_airbag", "e_isofix", "e_park_sensor", "e_rear_cam",
                  "e_cruise", "e_lane", "e_alarm", "e_immo"],
    "eq_interior": ["e_leather", "e_heat_seat", "e_el_seat", "e_sunroof", "e_pano", "e_climate", "e_ac", "e_pwin",
                    "e_keyless", "e_steer_ctl"],
    "eq_exterior": ["e_alloy", "e_led", "e_fog", "e_rails", "e_tow", "e_tint", "e_el_mirror", "e_rain", "e_spoiler"],
    "eq_media": ["e_bt", "e_usb", "e_nav", "e_carplay", "e_touch", "e_audio", "e_radio", "e_hud"],
}

INFO = [("deal", "select", ["sale", "rent"]), ("brand", "text", None), ("series", "text", None), ("model", "text", None),
        ("year", "number", None), ("fuel", "select", ["petrol", "diesel", "lpg", "hybrid", "electric"]),
        ("gearbox", "select", ["manual", "automatic"]),
        ("condition", "select", ["c_new", "c_used", "c_damaged"]), ("km", "number", None),
        ("body", "select", ["b_sedan", "b_hatch", "b_wagon", "b_suv", "b_coupe", "b_cabrio", "b_van", "b_minivan", "b_pickup"]),
        ("power_hp", "number", None), ("engine_cc", "number", None),
        ("drive", "select", ["d_fwd", "d_rwd", "d_awd"]), ("color", "select", _COLORS),
        ("warranty", "select", _YN), ("heavy_damage", "select", _YN),
        ("plate", "select", ["pl_local", "pl_foreign"]), ("seller_type", "select", ["s_owner", "s_dealer"]),
        ("swap", "select", _YN)]
TECH = [("accel", "text", None), ("top_speed", "number", None), ("cons_comb", "text", None), ("cons_city", "text", None),
        ("cons_hwy", "text", None), ("tank_l", "number", None), ("doors", "number", None), ("seats", "number", None),
        ("trunk_l", "number", None), ("weight_kg", "number", None)]
PAINT = [(p, "select", _PAINT) for p in _PARTS]
EQUIP = [(k, "multi", v) for k, v in _EQ.items()]

SCHEMA_VASITA = INFO + TECH + PAINT + EQUIP
# bolum: (baslik anahtari, alan anahtarlari, filtrelenebilir mi)
GROUPS = [("g_info", [f[0] for f in INFO], True), ("g_tech", [f[0] for f in TECH], False),
          ("g_paint", [f[0] for f in PAINT], False), ("g_equip", [f[0] for f in EQUIP], False)]

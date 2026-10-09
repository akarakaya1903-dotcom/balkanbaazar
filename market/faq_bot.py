# -*- coding: utf-8 -*-
"""Site ici yardim botu: hazir cevaplar (API gerektirmez). Dil yoksa Ingilizce kullanilir.
Her giris: (soru, cevap, anahtar kelimeler, link_anahtari). link_anahtari: post|safe|car|ad|contact|shops"""

UI = {
    "tr": {"title": "Yardım", "hello": "Merhaba! Sana nasıl yardımcı olabilirim? Bir soru seç ya da yaz.", "ph": "Sorunu yaz…", "none": "Bunu tam anlayamadım. Aşağıdaki sorulardan birini seçebilir ya da bize yazabilirsin.", "more": "Daha fazlası", "contact": "Bize yaz", "wave": "👋 Hoş geldin! Yardımcı olabilir miyim?"},
    "en": {"title": "Help", "hello": "Hi! How can I help? Pick a question or type your own.", "ph": "Type your question…", "none": "I did not quite get that. Pick one of the questions below or write to us.", "more": "Read more", "contact": "Contact us", "wave": "👋 Welcome! Can I help you?"},
    "mk": {"title": "Помош", "hello": "Здраво! Како можам да помогнам? Избери прашање или напиши свое.", "ph": "Напиши прашање…", "none": "Не разбрав сосема. Избери едно од прашањата подолу или пиши ни.", "more": "Повеќе", "contact": "Пиши ни", "wave": "👋 Добре дојде! Може ли да помогнам?"},
    "sq": {"title": "Ndihmë", "hello": "Përshëndetje! Si mund të ndihmoj? Zgjidh një pyetje ose shkruaj të tuajën.", "ph": "Shkruaj pyetjen…", "none": "Nuk e kuptova mirë. Zgjidh një nga pyetjet më poshtë ose na shkruaj.", "more": "Më shumë", "contact": "Na shkruaj", "wave": "👋 Mirë se erdhe! Mund të të ndihmoj?"},
}

QA = {
    "tr": [
        ("Nasıl ilan veririm?", "Üst menüdeki “İlan ver” düğmesine bas, kategori seç, başlık, fiyat ve en az 1 fotoğraf ekle (en fazla 20). İlk ilanın yaklaşık 2 dakika sürer. Fiyatı kendi para biriminde ya da Euro olarak girebilirsin.", "ilan ver vermek nasıl yayınla ekle sat satmak post", "post"),
        ("İlan vermek ücretli mi?", "Bireysel ilan vermek ücretsizdir ve komisyon alınmaz. Öne çıkarma gibi isteğe bağlı hizmetler ayrıca belirtilir.", "ücret ücretli ucret para komisyon bedava ücretsiz fiyat ne kadar", ""),
        ("Dolandırılmamak için ne yapmalıyım?", "Ürünü görmeden ön ödeme yapma, kalabalık bir yerde buluş, kimlik veya kart bilgisi paylaşma, çok ucuz fiyatlara şüpheyle yaklaş. Şüpheli ilanda “Şikâyet et” düğmesini kullan.", "dolandır güvenli güven sahte şikayet tuzak kapora", "safe"),
        ("Mağaza nasıl açarım?", "Hesap açıp “Mağaza aç” sayfasından başvuru yapabilirsin. Başvurun incelenir, onaylanınca ürün ekleyip sipariş alabilirsin.", "mağaza magaza dükkan işletme satıcı başvuru kurumsal", "shops"),
        ("Ödeme nasıl yapılıyor?", "Şu an sitede online kart ödemesi yok. Mağaza siparişleri kapıda ödenir. Bireysel ilanlarda ödeme ve teslimat alıcı ile satıcı arasında belirlenir.", "ödeme odeme kart kapıda teslimat kargo nasıl öde", ""),
        ("İkinci el araba alırken nelere bakmalıyım?", "Belgeleri, kilometreyi ve bakım geçmişini kontrol et, test sürüşü yap, aracın borç/ceza durumunu sor. Ayrıntılı rehberimizi oku.", "araba araç otomobil vasıta ikinci el araç", "car"),
        ("İlanım neden görünmüyor?", "İlanın yönetici onayında bekliyor ya da süresi dolmuş olabilir. “İlanlarım” sayfasından durumuna bakabilir ve süresi dolmuşsa yenileyebilirsin.", "görünmüyor gorunmuyor yayında onay bekliyor süresi dolmuş neden ilanım", ""),
    ],
    "en": [
        ("How do I post an ad?", "Tap “Post an ad” in the menu, pick a category, add a title, a price and at least 1 photo (up to 20). Your first ad takes about 2 minutes. You can enter the price in your own currency or in Euro.", "post ad sell listing how add publish create", "post"),
        ("Is posting an ad free?", "Posting a private ad is free and there is no commission. Optional services such as promotion are shown separately.", "free cost price fee commission pay charge", ""),
        ("How do I avoid scams?", "Never pay in advance without seeing the item, meet in a busy place, never share ID or card details, and be wary of prices far below the market. Use the “Report” button on suspicious ads.", "scam fraud safe safety fake report trust deposit", "safe"),
        ("How do I open a shop?", "Create an account and apply from the “Open a shop” page. Your application is reviewed and once approved you can add products and take orders.", "shop store business seller apply open", "shops"),
        ("How does payment work?", "There are no online card payments at the moment. Shop orders are paid on delivery. For private ads, payment and delivery are agreed between buyer and seller.", "payment pay card delivery shipping cash", ""),
        ("What should I check when buying a used car?", "Check the documents, mileage and service history, take a test drive and ask about debts or fines. Read our detailed guide.", "car vehicle used auto buy", "car"),
        ("Why is my ad not showing?", "It may be waiting for approval or it may have expired. Check its status on the “My ads” page and renew it if it expired.", "not showing visible missing approval expired my ad", ""),
    ],
    "mk": [
        ("Како да објавам оглас?", "Притисни „Објави оглас“ во менито, избери категорија, додај наслов, цена и најмалку 1 фотографија (најмногу 20). Првиот оглас трае околу 2 минути. Цената можеш да ја внесеш во своја валута или во евра.", "оглас објави продава додаде како", "post"),
        ("Дали објавувањето е бесплатно?", "Објавувањето оглас за физички лица е бесплатно и без провизија. Дополнителните услуги, како истакнување, се наведени посебно.", "бесплатно цена провизија плаќање чини", ""),
        ("Како да не бидам измамен?", "Не плаќај однапред без да го видиш производот, сретни се на јавно место, не споделувај лична карта или картичка и внимавај на премногу ниски цени. На сомнителен оглас користи „Пријави“.", "измама безбедно лажен пријава капара", "safe"),
        ("Како да отворам продавница?", "Направи профил и аплицирај од страницата „Отвори продавница“. Апликацијата се проверува, а потоа можеш да додаваш производи и да примаш нарачки.", "продавница бизнис продавач аплицирај", "shops"),
        ("Како се плаќа?", "Моментално нема онлајн плаќање со картичка. Нарачките од продавници се плаќаат при достава. Кај огласите на физички лица плаќањето и доставата се договараат меѓу купувачот и продавачот.", "плаќање картичка достава готовина", ""),
        ("Што да проверам кога купувам половен автомобил?", "Провери ги документите, километражата и сервисната историја, направи пробна вожња и прашај за долгови или казни. Прочитај го нашиот водич.", "автомобил кола возило половен", "car"),
        ("Зошто не се гледа мојот оглас?", "Можеби чека одобрување или му истекол рокот. Провери го статусот на страницата „Мои огласи“ и обнови го ако е истечен.", "не се гледа одобрување истечен мој оглас", ""),
    ],
    "sq": [
        ("Si të publikoj një shpallje?", "Shtyp “Posto shpallje” në meny, zgjidh kategorinë, shto titullin, çmimin dhe të paktën 1 foto (maksimumi 20). Shpallja e parë zgjat rreth 2 minuta. Çmimin mund ta shkruash në monedhën tënde ose në euro.", "shpallje posto publiko shes shtoj si", "post"),
        ("A është falas publikimi?", "Publikimi i shpalljes private është falas dhe pa komision. Shërbimet opsionale, si promovimi, tregohen veçmas.", "falas çmim komision pagesë kushton", ""),
        ("Si të mos mashtrohem?", "Mos paguaj paraprakisht pa e parë artikullin, takohu në vend publik, mos ndaj letërnjoftimin ose kartën dhe ji i kujdesshëm me çmimet shumë të ulëta. Te shpallja e dyshimtë përdor “Raporto”.", "mashtrim sigurt rrenë raport kapar", "safe"),
        ("Si të hap një dyqan?", "Krijo llogari dhe apliko nga faqja “Hap dyqan”. Aplikimi shqyrtohet dhe pasi miratohet mund të shtosh produkte dhe të marrësh porosi.", "dyqan biznes shitës apliko", "shops"),
        ("Si bëhet pagesa?", "Aktualisht nuk ka pagesë online me kartë. Porositë e dyqaneve paguhen në dorëzim. Te shpalljet private pagesa dhe dorëzimi merren vesh mes blerësit dhe shitësit.", "pagesa kartë dorëzim para", ""),
        ("Çfarë të kontrollosh kur blen makinë të përdorur?", "Kontrollo dokumentet, kilometrazhin dhe historikun e servisit, bëj provë vozitjeje dhe pyet për borxhe ose gjoba. Lexo udhëzuesin tonë.", "makinë automjet përdorur veturë", "car"),
        ("Pse nuk shfaqet shpallja ime?", "Mund të jetë në pritje të miratimit ose të ketë skaduar. Kontrollo statusin te “Shpalljet e mia” dhe rinovoje nëse ka skaduar.", "nuk shfaqet miratim skaduar shpallja ime", ""),
    ],
}

UI.update({
    "sr": {"title": "Помоћ", "hello": "Здраво! Како могу да помогнем? Изабери питање или напиши своје.", "ph": "Напиши питање…", "none": "Нисам најбоље разумео. Изабери једно од питања испод или нам пиши.", "more": "Више", "contact": "Пиши нам", "wave": "👋 Добродошли! Могу ли да помогнем?"},
    "bs": {"title": "Pomoć", "hello": "Zdravo! Kako mogu pomoći? Odaberi pitanje ili napiši svoje.", "ph": "Napiši pitanje…", "none": "Nisam najbolje razumio. Odaberi jedno od pitanja ispod ili nam piši.", "more": "Više", "contact": "Piši nam", "wave": "👋 Dobrodošli! Mogu li pomoći?"},
    "hr": {"title": "Pomoć", "hello": "Bok! Kako vam mogu pomoći? Odaberite pitanje ili napišite svoje.", "ph": "Napišite pitanje…", "none": "Nisam baš razumio. Odaberite jedno od pitanja ispod ili nam pišite.", "more": "Više", "contact": "Pišite nam", "wave": "👋 Dobrodošli! Mogu li pomoći?"},
    "cnr": {"title": "Pomoć", "hello": "Zdravo! Kako mogu pomoći? Izaberi pitanje ili napiši svoje.", "ph": "Napiši pitanje…", "none": "Nijesam najbolje razumio. Izaberi jedno od pitanja ispod ili nam piši.", "more": "Više", "contact": "Piši nam", "wave": "👋 Dobrodošli! Mogu li pomoći?"},
    "bg": {"title": "Помощ", "hello": "Здравей! Как мога да помогна? Избери въпрос или напиши свой.", "ph": "Напиши въпрос…", "none": "Не разбрах напълно. Избери някой от въпросите по-долу или ни пиши.", "more": "Повече", "contact": "Пиши ни", "wave": "👋 Добре дошли! Мога ли да помогна?"},
    "el": {"title": "Βοήθεια", "hello": "Γεια σου! Πώς μπορώ να βοηθήσω; Διάλεξε μια ερώτηση ή γράψε τη δική σου.", "ph": "Γράψε την ερώτησή σου…", "none": "Δεν κατάλαβα καλά. Διάλεξε μία από τις ερωτήσεις παρακάτω ή γράψε μας.", "more": "Περισσότερα", "contact": "Επικοινωνία", "wave": "👋 Καλώς ήρθες! Μπορώ να βοηθήσω;"},
})

_BS = [
    ("Kako objaviti oglas?", "Pritisni “Objavi” u meniju, odaberi kategoriju, dodaj naslov, cijenu i najmanje 1 fotografiju (najviše 20). Prvi oglas traje oko 2 minute. Cijenu možeš unijeti u svojoj valuti ili u eurima.", "oglas objavi prodati dodati kako postaviti", "post"),
    ("Da li je objava oglasa besplatna?", "Objava privatnog oglasa je besplatna i bez provizije. Dodatne usluge, poput isticanja, navedene su posebno.", "besplatno cijena cena provizija plaćanje košta", ""),
    ("Kako da me ne prevare?", "Ne plaćaj unaprijed bez viđenja artikla, nađi se na javnom mjestu, ne dijeli ličnu kartu ni podatke o kartici i budi oprezan s previše niskim cijenama. Na sumnjivom oglasu koristi “Prijavi”.", "prevara sigurno lažno prijava kapara", "safe"),
    ("Kako otvoriti trgovinu?", "Napravi račun i prijavi se na stranici za otvaranje trgovine. Prijava se pregleda, a nakon odobrenja možeš dodavati proizvode i primati narudžbe.", "trgovina prodavnica radnja biznis prodavač prijava", "shops"),
    ("Kako se plaća?", "Trenutno nema online plaćanja karticom. Narudžbe iz trgovina plaćaju se pri dostavi. Kod privatnih oglasa plaćanje i dostava dogovaraju se između kupca i prodavca.", "plaćanje kartica dostava gotovina", ""),
    ("Na šta paziti pri kupovini polovnog auta?", "Provjeri dokumente, kilometražu i servisnu historiju, napravi probnu vožnju i pitaj za dugove ili kazne. Pročitaj naš vodič.", "auto automobil vozilo polovni", "car"),
    ("Zašto se moj oglas ne vidi?", "Možda čeka odobrenje ili mu je istekao rok. Provjeri status na stranici “Moji oglasi” i obnovi ga ako je istekao.", "ne vidi odobrenje istekao moj oglas", ""),
]

QA.update({
    "bs": _BS, "hr": _BS, "cnr": _BS,
    "sr": [
        ("Како да објавим оглас?", "Притисни „Објави“ у менију, изабери категорију, додај наслов, цену и бар 1 фотографију (највише 20). Први оглас траје око 2 минута. Цену можеш да унесеш у својој валути или у еврима.", "оглас објави продати додати како", "post"),
        ("Да ли је објава огласа бесплатна?", "Објава приватног огласа је бесплатна и без провизије. Додатне услуге, попут истицања, наведене су посебно.", "бесплатно цена провизија плаћање кошта", ""),
        ("Како да ме не преваре?", "Не плаћај унапред без виђења артикла, нађи се на јавном месту, не дели личну карту ни податке о картици и буди опрезан са превише ниским ценама. На сумњивом огласу користи „Пријави“.", "превара безбедно лажно пријава капара", "safe"),
        ("Како да отворим радњу?", "Направи налог и пријави се на страници за отварање радње. Пријава се прегледа, а након одобрења можеш да додајеш производе и примаш поруџбине.", "радња продавница бизнис продавац пријава", "shops"),
        ("Како се плаћа?", "Тренутно нема онлајн плаћања картицом. Поруџбине из радњи плаћају се при достави. Код приватних огласа плаћање и достава договарају се између купца и продавца.", "плаћање картица достава готовина", ""),
        ("На шта пазити при куповини половног аута?", "Провери документа, километражу и сервисну историју, направи пробну вожњу и питај за дугове или казне. Прочитај наш водич.", "ауто аутомобил возило половни", "car"),
        ("Зашто се мој оглас не види?", "Можда чека одобрење или му је истекао рок. Провери статус на страници „Моји огласи“ и обнови га ако је истекао.", "не види одобрење истекао мој оглас", ""),
    ],
    "bg": [
        ("Как да публикувам обява?", "Натисни „Публикувай“ в менюто, избери категория, добави заглавие, цена и поне 1 снимка (най-много 20). Първата обява отнема около 2 минути. Цената можеш да въведеш в своята валута или в евро.", "обява публикувам продавам добавя как", "post"),
        ("Безплатно ли е публикуването?", "Публикуването на обява от физическо лице е безплатно и без комисиона. Допълнителните услуги, като подчертаване, са посочени отделно.", "безплатно цена комисиона плащане струва", ""),
        ("Как да не ме измамят?", "Не плащай предварително, без да си видял артикула, срещни се на обществено място, не споделяй лична карта или данни за карта и внимавай с твърде ниски цени. При съмнителна обява използвай „Докладвай“.", "измама сигурно фалшив докладвай капаро", "safe"),
        ("Как да отворя магазин?", "Направи профил и кандидатствай от страницата за отваряне на магазин. Заявката се преглежда, а след одобрение можеш да добавяш продукти и да получаваш поръчки.", "магазин бизнис продавач кандидатствай", "shops"),
        ("Как се плаща?", "Към момента няма онлайн плащане с карта. Поръчките от магазини се плащат при доставка. При обяви от физически лица плащането и доставката се уговарят между купувача и продавача.", "плащане карта доставка наложен", ""),
        ("Какво да проверя при купуване на кола втора ръка?", "Провери документите, километража и сервизната история, направи тестово шофиране и питай за задължения или глоби. Прочети нашето ръководство.", "кола автомобил превозно средство втора ръка", "car"),
        ("Защо не се вижда моята обява?", "Може да чака одобрение или да е изтекла. Провери статуса на страницата „Моите обяви“ и я поднови, ако е изтекла.", "не се вижда одобрение изтекла моята обява", ""),
    ],
    "el": [
        ("Πώς δημοσιεύω αγγελία;", "Πάτησε «Πώληση» στο μενού, διάλεξε κατηγορία, πρόσθεσε τίτλο, τιμή και τουλάχιστον 1 φωτογραφία (έως 20). Η πρώτη αγγελία παίρνει περίπου 2 λεπτά. Την τιμή μπορείς να τη βάλεις στο νόμισμά σου ή σε ευρώ.", "αγγελία δημοσίευση πώληση προσθήκη πώς", "post"),
        ("Είναι δωρεάν η δημοσίευση;", "Η δημοσίευση ιδιωτικής αγγελίας είναι δωρεάν και χωρίς προμήθεια. Οι προαιρετικές υπηρεσίες, όπως η προβολή, αναγράφονται ξεχωριστά.", "δωρεάν τιμή προμήθεια πληρωμή κόστος", ""),
        ("Πώς να μην με εξαπατήσουν;", "Μην πληρώνεις προκαταβολικά χωρίς να δεις το προϊόν, συναντήσου σε δημόσιο χώρο, μην μοιράζεσαι ταυτότητα ή στοιχεία κάρτας και πρόσεχε τις πολύ χαμηλές τιμές. Στις ύποπτες αγγελίες χρησιμοποίησε το «Αναφορά».", "απάτη ασφαλές πλαστό αναφορά προκαταβολή", "safe"),
        ("Πώς ανοίγω κατάστημα;", "Φτιάξε λογαριασμό και κάνε αίτηση από τη σελίδα ανοίγματος καταστήματος. Η αίτηση ελέγχεται και μετά την έγκριση μπορείς να προσθέτεις προϊόντα και να λαμβάνεις παραγγελίες.", "κατάστημα επιχείρηση πωλητής αίτηση", "shops"),
        ("Πώς γίνεται η πληρωμή;", "Προς το παρόν δεν υπάρχει online πληρωμή με κάρτα. Οι παραγγελίες καταστημάτων πληρώνονται κατά την παράδοση. Στις ιδιωτικές αγγελίες η πληρωμή και η παράδοση συμφωνούνται μεταξύ αγοραστή και πωλητή.", "πληρωμή κάρτα παράδοση μετρητά", ""),
        ("Τι να προσέξω αγοράζοντας μεταχειρισμένο αυτοκίνητο;", "Έλεγξε τα έγγραφα, τα χιλιόμετρα και το ιστορικό service, κάνε δοκιμαστική οδήγηση και ρώτα για οφειλές ή πρόστιμα. Διάβασε τον οδηγό μας.", "αυτοκίνητο όχημα μεταχειρισμένο αμάξι", "car"),
        ("Γιατί δεν εμφανίζεται η αγγελία μου;", "Ίσως περιμένει έγκριση ή έχει λήξει. Δες την κατάσταση στη σελίδα «Οι αγγελίες μου» και ανανέωσέ την αν έληξε.", "δεν εμφανίζεται έγκριση έληξε αγγελία μου", ""),
    ],
})

LINK_SLUGS = {"safe": "guvenli-alisveris-rehberi", "car": "ikinci-el-araba-rehberi", "ad": "ilan-nasil-verilir"}


def bot_data(lang):
    """(ui, qa) secili dil icin; dil yoksa Ingilizce."""
    code = lang if lang in QA else "en"
    ui = UI.get(lang) or UI["en"]
    qa = [{"q": q, "a": a, "k": k.lower(), "l": l} for q, a, k, l in QA[code]]
    return ui, qa

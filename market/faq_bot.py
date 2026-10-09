# -*- coding: utf-8 -*-
"""Site ici yardim botu: hazir cevaplar (API gerektirmez). Dil yoksa Ingilizce kullanilir.
Her giris: (soru, cevap, anahtar kelimeler, link_anahtari). link_anahtari: post|safe|car|ad|contact|shops"""

UI = {
    "tr": {"title": "Yardım", "hello": "Merhaba! Sana nasıl yardımcı olabilirim? Bir soru seç ya da yaz.", "ph": "Sorunu yaz…", "none": "Bunu tam anlayamadım. Aşağıdaki sorulardan birini seçebilir ya da bize yazabilirsin.", "more": "Daha fazlası", "contact": "Bize yaz"},
    "en": {"title": "Help", "hello": "Hi! How can I help? Pick a question or type your own.", "ph": "Type your question…", "none": "I did not quite get that. Pick one of the questions below or write to us.", "more": "Read more", "contact": "Contact us"},
    "mk": {"title": "Помош", "hello": "Здраво! Како можам да помогнам? Избери прашање или напиши свое.", "ph": "Напиши прашање…", "none": "Не разбрав сосема. Избери едно од прашањата подолу или пиши ни.", "more": "Повеќе", "contact": "Пиши ни"},
    "sq": {"title": "Ndihmë", "hello": "Përshëndetje! Si mund të ndihmoj? Zgjidh një pyetje ose shkruaj të tuajën.", "ph": "Shkruaj pyetjen…", "none": "Nuk e kuptova mirë. Zgjidh një nga pyetjet më poshtë ose na shkruaj.", "more": "Më shumë", "contact": "Na shkruaj"},
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

LINK_SLUGS = {"safe": "guvenli-alisveris-rehberi", "car": "ikinci-el-araba-rehberi", "ad": "ilan-nasil-verilir"}


def bot_data(lang):
    """(ui, qa) secili dil icin; dil yoksa Ingilizce."""
    code = lang if lang in QA else "en"
    ui = UI.get(lang) or UI["en"]
    qa = [{"q": q, "a": a, "k": k.lower(), "l": l} for q, a, k, l in QA[code]]
    return ui, qa

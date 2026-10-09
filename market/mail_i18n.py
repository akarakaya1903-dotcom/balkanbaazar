# -*- coding: utf-8 -*-
"""Hos geldin ve e-posta dogrulama e-postalari: 10 dil + logolu HTML sablon."""
from html import escape

from django.conf import settings

# welcome: subject, hello({name}), p1, p2, p3, cta, foot   |  verify: subject, p, cta, note
_BCS_W = {
    "subject": "Dobrodošli na Balkan Baazar", "hello": "Zdravo {name},",
    "p1": "Vaš račun je spreman. Na Balkan Baazar možete besplatno prodavati stvari koje vam ne trebaju, bez provizije.",
    "p2": "Prvi oglas objavljujete za 2 minute: dodajte fotografije, upišite cijenu i pošaljite. Oglas se objavljuje nakon odobrenja administratora.",
    "p3": "Da biste objavljivali oglase, potrebno je da potvrdite e-poštu. Link za potvrdu stigao je u posebnoj poruci.",
    "cta": "Objavi prvi oglas", "foot": "Ovu poruku ste primili jer ste se registrovali na Balkan Baazar.",
}
_BCS_V = {
    "subject": "Potvrdite e-poštu – Balkan Baazar",
    "p": "Kliknite na dugme da potvrdite adresu e-pošte. Link vrijedi 3 dana.",
    "cta": "Potvrdi e-poštu", "note": "Ako to niste učinili vi, zanemarite ovu poruku.",
}

WELCOME = {
    "tr": {"subject": "Balkan Baazar'a hoş geldin", "hello": "Merhaba {name},",
           "p1": "Hesabın hazır. Balkan Baazar'da kullanmadığın eşyaları ücretsiz satabilirsin, komisyon yok.",
           "p2": "İlk ilanını vermek 2 dakika sürer: fotoğraf ekle, fiyatı yaz, gönder. İlanın yönetici onayından sonra yayına girer.",
           "p3": "İlan verebilmek için e-posta adresini doğrulaman gerekir. Doğrulama bağlantısı ayrı bir e-postayla geldi.",
           "cta": "İlk ilanını ver", "foot": "Bu e-postayı Balkan Baazar'a kayıt olduğun için aldın."},
    "en": {"subject": "Welcome to Balkan Baazar", "hello": "Hi {name},",
           "p1": "Your account is ready. On Balkan Baazar you can sell things you no longer need for free, with no commission.",
           "p2": "Posting your first ad takes 2 minutes: add photos, set a price and send. Your ad goes live after an administrator approves it.",
           "p3": "To post ads you need to verify your email. The verification link arrived in a separate email.",
           "cta": "Post your first ad", "foot": "You received this email because you signed up on Balkan Baazar."},
    "mk": {"subject": "Добредојде во Balkan Baazar", "hello": "Здраво {name},",
           "p1": "Твојата сметка е подготвена. На Balkan Baazar можеш бесплатно да ги продаваш работите што не ти требаат, без провизија.",
           "p2": "Првиот оглас го објавуваш за 2 минути: додај фотографии, впиши цена и испрати. Огласот се објавува откако ќе го одобри администратор.",
           "p3": "За да објавуваш огласи, треба да ја потврдиш е-поштата. Врската за потврда стигна во посебна порака.",
           "cta": "Објави прв оглас", "foot": "Ја добивте оваа порака затоа што се регистриравте на Balkan Baazar."},
    "sq": {"subject": "Mirë se erdhe në Balkan Baazar", "hello": "Përshëndetje {name},",
           "p1": "Llogaria jote është gati. Në Balkan Baazar mund të shesësh falas gjërat që nuk të duhen, pa komision.",
           "p2": "Shpalljen e parë e publikon në 2 minuta: shto foto, shkruaj çmimin dhe dërgo. Shpallja publikohet pasi ta miratojë administratori.",
           "p3": "Për të publikuar shpallje duhet të verifikosh email-in. Lidhja e verifikimit të erdhi në një mesazh tjetër.",
           "cta": "Publiko shpalljen e parë", "foot": "E more këtë mesazh sepse u regjistrove në Balkan Baazar."},
    "sr": {"subject": "Dobrodošli na Balkan Baazar", "hello": "Zdravo {name},",
           "p1": "Vaš nalog je spreman. Na Balkan Baazar možete besplatno prodavati stvari koje vam ne trebaju, bez provizije.",
           "p2": "Prvi oglas objavljujete za 2 minuta: dodajte fotografije, upišite cenu i pošaljite. Oglas se objavljuje nakon odobrenja administratora.",
           "p3": "Da biste objavljivali oglase, potrebno je da potvrdite e-poštu. Link za potvrdu stigao je u posebnoj poruci.",
           "cta": "Objavi prvi oglas", "foot": "Ovu poruku ste dobili jer ste se registrovali na Balkan Baazar."},
    "bs": dict(_BCS_W),
    "cnr": dict(_BCS_W),
    "hr": {"subject": "Dobrodošli na Balkan Baazar", "hello": "Bok {name},",
           "p1": "Vaš račun je spreman. Na Balkan Baazar možete besplatno prodavati stvari koje vam ne trebaju, bez provizije.",
           "p2": "Prvi oglas objavljujete za 2 minute: dodajte fotografije, upišite cijenu i pošaljite. Oglas se objavljuje nakon odobrenja administratora.",
           "p3": "Za objavu oglasa potrebno je potvrditi e-poštu. Poveznica za potvrdu stigla je u zasebnoj poruci.",
           "cta": "Objavi prvi oglas", "foot": "Ovu poruku primili ste jer ste se registrirali na Balkan Baazar."},
    "bg": {"subject": "Добре дошли в Balkan Baazar", "hello": "Здравейте, {name},",
           "p1": "Профилът ви е готов. В Balkan Baazar можете да продавате безплатно ненужните си вещи, без комисионна.",
           "p2": "Първата обява публикувате за 2 минути: добавете снимки, въведете цена и изпратете. Обявата се публикува след одобрение от администратор.",
           "p3": "За да публикувате обяви, трябва да потвърдите имейла си. Линкът за потвърждение пристигна в отделно съобщение.",
           "cta": "Публикувай първата обява", "foot": "Получавате това съобщение, защото се регистрирахте в Balkan Baazar."},
    "el": {"subject": "Καλώς ήρθατε στο Balkan Baazar", "hello": "Γεια σας {name},",
           "p1": "Ο λογαριασμός σας είναι έτοιμος. Στο Balkan Baazar μπορείτε να πουλάτε δωρεάν όσα δεν χρειάζεστε, χωρίς προμήθεια.",
           "p2": "Η πρώτη αγγελία ανεβαίνει σε 2 λεπτά: προσθέστε φωτογραφίες, γράψτε την τιμή και στείλτε. Η αγγελία δημοσιεύεται μετά την έγκριση του διαχειριστή.",
           "p3": "Για να δημοσιεύετε αγγελίες πρέπει να επιβεβαιώσετε το email σας. Ο σύνδεσμος επιβεβαίωσης στάλθηκε σε ξεχωριστό μήνυμα.",
           "cta": "Δημοσίευσε την πρώτη αγγελία", "foot": "Λάβατε αυτό το μήνυμα επειδή εγγραφήκατε στο Balkan Baazar."},
}

VERIFY = {
    "tr": {"subject": "E-postanı doğrula – Balkan Baazar",
           "p": "E-posta adresini doğrulamak için aşağıdaki düğmeye tıkla. Bağlantı 3 gün geçerlidir.",
           "cta": "E-postamı doğrula", "note": "Bu işlemi sen yapmadıysan bu e-postayı yok sayabilirsin."},
    "en": {"subject": "Verify your email – Balkan Baazar",
           "p": "Click the button below to verify your email address. The link is valid for 3 days.",
           "cta": "Verify my email", "note": "If you didn't do this, you can ignore this email."},
    "mk": {"subject": "Потврди ја е-поштата – Balkan Baazar",
           "p": "Кликни на копчето за да ја потврдиш твојата е-пошта. Врската важи 3 дена.",
           "cta": "Потврди ја е-поштата", "note": "Ако не си го направил ова ти, игнорирај ја пораката."},
    "sq": {"subject": "Verifiko email-in – Balkan Baazar",
           "p": "Kliko butonin për të verifikuar adresën tënde të email-it. Lidhja vlen 3 ditë.",
           "cta": "Verifiko email-in", "note": "Nëse nuk e ke bërë ti këtë, injoroje këtë mesazh."},
    "sr": {"subject": "Potvrdite e-poštu – Balkan Baazar",
           "p": "Kliknite na dugme da potvrdite adresu e-pošte. Link važi 3 dana.",
           "cta": "Potvrdi e-poštu", "note": "Ako to niste uradili vi, ignorišite ovu poruku."},
    "bs": dict(_BCS_V),
    "cnr": dict(_BCS_V),
    "hr": {"subject": "Potvrdite e-poštu – Balkan Baazar",
           "p": "Kliknite gumb kako biste potvrdili adresu e-pošte. Poveznica vrijedi 3 dana.",
           "cta": "Potvrdi e-poštu", "note": "Ako niste vi to učinili, zanemarite ovu poruku."},
    "bg": {"subject": "Потвърдете имейла си – Balkan Baazar",
           "p": "Натиснете бутона, за да потвърдите имейл адреса си. Линкът е валиден 3 дни.",
           "cta": "Потвърди имейла", "note": "Ако не сте го направили вие, игнорирайте това съобщение."},
    "el": {"subject": "Επιβεβαιώστε το email σας – Balkan Baazar",
           "p": "Πατήστε το κουμπί για να επιβεβαιώσετε τη διεύθυνση email σας. Ο σύνδεσμος ισχύει για 3 ημέρες.",
           "cta": "Επιβεβαίωση email", "note": "Αν δεν το κάνατε εσείς, αγνοήστε αυτό το μήνυμα."},
}


def pick(table, lang):
    return table.get(lang) or table["en"]


def html_mail(paragraphs, cta_label, cta_url, foot):
    """Logolu, telefonda duzgun gorunen basit HTML e-posta (tum stiller satir ici)."""
    site = settings.SITE_URL.rstrip("/")
    logo = site + "/static/img/logo-192.png"
    body = "".join(
        f'<p style="margin:0 0 14px;font-size:16px;line-height:1.55;color:#1c2b36">{escape(p)}</p>' for p in paragraphs)
    return (
        '<!doctype html><html><body style="margin:0;padding:0;background:#EEF3F6">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EEF3F6;padding:24px 12px">'
        '<tr><td align="center">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:16px;overflow:hidden;font-family:Arial,Helvetica,sans-serif">'
        '<tr><td style="background:#0D2A3A;padding:22px 28px">'
        f'<table role="presentation" cellpadding="0" cellspacing="0"><tr>'
        f'<td><img src="{logo}" width="48" height="48" alt="Balkan Baazar" style="display:block;border-radius:12px"></td>'
        '<td style="padding-left:14px;font-size:22px;font-weight:bold;color:#ffffff">Balkan<span style="color:#FFB020">Baazar</span></td>'
        '</tr></table></td></tr>'
        f'<tr><td style="padding:28px 28px 8px">{body}</td></tr>'
        f'<tr><td align="center" style="padding:6px 28px 28px"><a href="{escape(cta_url)}" '
        'style="display:inline-block;background:#0B8FA6;color:#ffffff;text-decoration:none;font-weight:bold;font-size:16px;padding:14px 28px;border-radius:12px">'
        f'{escape(cta_label)}</a></td></tr>'
        f'<tr><td style="background:#F6F9FB;padding:16px 28px;font-size:12px;color:#6b7c88;line-height:1.5">{escape(foot)}<br>'
        f'<a href="{site}" style="color:#0B8FA6;text-decoration:none">balkanbaazar.com</a></td></tr>'
        '</table></td></tr></table></body></html>')


# ---------------------------------------------------------------------------
# Olay e-postalari (10 dil). Her kayit: (konu, [paragraflar], dugme yazisi)
# Yer tutucular: {name} {title} {n} {shop}
# ---------------------------------------------------------------------------
_L = "bs"  # bs/hr/cnr ayni Latin metni kullanir

EVENTS = {
    "listing_received": {
        "tr": ("İlanın alındı: {title}", ["Merhaba {name},", "“{title}” ilanını aldık. Yönetici incelemesinden sonra yayına girecek, genellikle kısa sürede.", "Yayına girince sana yeni bir e-posta göndereceğiz."], "İlanlarımı gör"),
        "en": ("We received your ad: {title}", ["Hi {name},", "We received your ad “{title}”. It goes live after a quick review, usually shortly.", "We will email you again as soon as it is published."], "View my ads"),
        "mk": ("Го примивме огласот: {title}", ["Здраво {name},", "Го примивме твојот оглас „{title}“. Ќе биде објавен по кратка проверка, обично за кратко време.", "Ќе ти испратиме нов е-маил штом биде објавен."], "Моите огласи"),
        "sq": ("E morëm shpalljen: {title}", ["Përshëndetje {name},", "E morëm shpalljen tënde “{title}”. Do të publikohet pas një shqyrtimi të shkurtër, zakonisht shpejt.", "Do të të dërgojmë një email tjetër sapo të publikohet."], "Shpalljet e mia"),
        "sr": ("Примили смо оглас: {title}", ["Здраво {name},", "Примили смо твој оглас „{title}“. Биће објављен након кратке провере, обично брзо.", "Послаћемо ти нову поруку чим буде објављен."], "Моји огласи"),
        "bs": ("Primili smo oglas: {title}", ["Zdravo {name},", "Primili smo tvoj oglas „{title}“. Bit će objavljen nakon kratke provjere, obično brzo.", "Poslat ćemo ti novu poruku čim bude objavljen."], "Moji oglasi"),
        "bg": ("Получихме обявата: {title}", ["Здравей {name},", "Получихме обявата ти „{title}“. Ще бъде публикувана след кратка проверка, обикновено скоро.", "Ще ти изпратим нов имейл, щом бъде публикувана."], "Моите обяви"),
        "el": ("Λάβαμε την αγγελία: {title}", ["Γεια σου {name},", "Λάβαμε την αγγελία σου «{title}». Θα δημοσιευτεί μετά από σύντομο έλεγχο, συνήθως σύντομα.", "Θα σου στείλουμε νέο email μόλις δημοσιευτεί."], "Οι αγγελίες μου"),
    },
    "listing_approved": {
        "tr": ("İlanın yayında: {title}", ["Merhaba {name},", "Güzel haber: “{title}” ilanın onaylandı ve yayına girdi.", "İlanına gelen mesajları “Mesajlar” bölümünden takip edebilirsin."], "İlanı gör"),
        "en": ("Your ad is live: {title}", ["Hi {name},", "Good news: your ad “{title}” was approved and is now live.", "You can follow messages about it in the “Messages” section."], "View the ad"),
        "mk": ("Огласот е објавен: {title}", ["Здраво {name},", "Добра вест: твојот оглас „{title}“ е одобрен и објавен.", "Пораките за него можеш да ги следиш во делот „Пораки“."], "Види го огласот"),
        "sq": ("Shpallja është publikuar: {title}", ["Përshëndetje {name},", "Lajm i mirë: shpallja jote “{title}” u miratua dhe u publikua.", "Mesazhet për të mund t'i ndjekësh te “Mesazhet”."], "Shiko shpalljen"),
        "sr": ("Оглас је објављен: {title}", ["Здраво {name},", "Добра вест: твој оглас „{title}“ је одобрен и објављен.", "Поруке о њему можеш да пратиш у одељку „Поруке“."], "Погледај оглас"),
        "bs": ("Oglas je objavljen: {title}", ["Zdravo {name},", "Dobra vijest: tvoj oglas „{title}“ je odobren i objavljen.", "Poruke o njemu možeš pratiti u odjeljku „Poruke“."], "Pogledaj oglas"),
        "bg": ("Обявата е публикувана: {title}", ["Здравей {name},", "Добра новина: обявата ти „{title}“ е одобрена и публикувана.", "Съобщенията за нея можеш да следиш в раздел „Съобщения“."], "Виж обявата"),
        "el": ("Η αγγελία δημοσιεύτηκε: {title}", ["Γεια σου {name},", "Καλά νέα: η αγγελία σου «{title}» εγκρίθηκε και δημοσιεύτηκε.", "Μπορείς να βλέπεις τα μηνύματα στην ενότητα «Μηνύματα»."], "Δες την αγγελία"),
    },
    "shop_received": {
        "tr": ("Mağaza başvurun alındı: {shop}", ["Merhaba {name},", "{shop} için mağaza başvurunu aldık. Ekibimiz iki iş günü içinde dönüş yapacak.", "Başvurunun durumunu panelinden takip edebilirsin."], "Panelime git"),
        "en": ("We received your shop application: {shop}", ["Hi {name},", "We received your shop application for {shop}. Our team will reply within two business days.", "You can follow its status in your panel."], "Go to my panel"),
        "mk": ("Ја примивме апликацијата за продавница: {shop}", ["Здраво {name},", "Ја примивме твојата апликација за продавницата {shop}. Тимот ќе одговори во рок од два работни дена.", "Статусот можеш да го следиш во твојот панел."], "Мојот панел"),
        "sq": ("E morëm aplikimin për dyqan: {shop}", ["Përshëndetje {name},", "E morëm aplikimin tënd për dyqanin {shop}. Ekipi ynë do të përgjigjet brenda dy ditëve pune.", "Statusin mund ta ndjekësh te paneli yt."], "Paneli im"),
        "sr": ("Примили смо пријаву за радњу: {shop}", ["Здраво {name},", "Примили смо твоју пријаву за радњу {shop}. Наш тим ће одговорити у року од два радна дана.", "Статус можеш да пратиш у свом панелу."], "Мој панел"),
        "bs": ("Primili smo prijavu za trgovinu: {shop}", ["Zdravo {name},", "Primili smo tvoju prijavu za trgovinu {shop}. Naš tim će odgovoriti u roku od dva radna dana.", "Status možeš pratiti u svom panelu."], "Moj panel"),
        "bg": ("Получихме заявката за магазин: {shop}", ["Здравей {name},", "Получихме заявката ти за магазин {shop}. Екипът ни ще отговори до два работни дни.", "Статуса можеш да следиш в своя панел."], "Моят панел"),
        "el": ("Λάβαμε την αίτηση καταστήματος: {shop}", ["Γεια σου {name},", "Λάβαμε την αίτησή σου για το κατάστημα {shop}. Η ομάδα μας θα απαντήσει εντός δύο εργάσιμων ημερών.", "Μπορείς να δεις την κατάσταση στο πάνελ σου."], "Το πάνελ μου"),
    },
    "shop_approved": {
        "tr": ("Mağazan onaylandı: {shop}", ["Merhaba {name},", "Tebrikler! {shop} onaylandı ve açıldı. İlk üç ay ücretsiz.", "Panelinden hemen ürün eklemeye başlayabilirsin."], "Ürün ekle"),
        "en": ("Your shop is approved: {shop}", ["Hi {name},", "Congratulations! {shop} was approved and is now open. The first three months are free.", "You can start adding products from your panel right away."], "Add products"),
        "mk": ("Продавницата е одобрена: {shop}", ["Здраво {name},", "Честитки! {shop} е одобрена и отворена. Првите три месеци се бесплатни.", "Веднаш можеш да додаваш производи од твојот панел."], "Додај производи"),
        "sq": ("Dyqani u miratua: {shop}", ["Përshëndetje {name},", "Urime! {shop} u miratua dhe u hap. Tre muajt e parë janë falas.", "Mund të shtosh produkte menjëherë nga paneli yt."], "Shto produkte"),
        "sr": ("Радња је одобрена: {shop}", ["Здраво {name},", "Честитамо! {shop} је одобрена и отворена. Прва три месеца су бесплатна.", "Одмах можеш да додајеш производе из свог панела."], "Додај производе"),
        "bs": ("Trgovina je odobrena: {shop}", ["Zdravo {name},", "Čestitamo! {shop} je odobrena i otvorena. Prva tri mjeseca su besplatna.", "Odmah možeš dodavati proizvode iz svog panela."], "Dodaj proizvode"),
        "bg": ("Магазинът е одобрен: {shop}", ["Здравей {name},", "Поздравления! {shop} е одобрен и отворен. Първите три месеца са безплатни.", "Веднага можеш да добавяш продукти от панела си."], "Добави продукти"),
        "el": ("Το κατάστημα εγκρίθηκε: {shop}", ["Γεια σου {name},", "Συγχαρητήρια! Το {shop} εγκρίθηκε και άνοιξε. Οι πρώτοι τρεις μήνες είναι δωρεάν.", "Μπορείς να προσθέσεις προϊόντα αμέσως από το πάνελ σου."], "Προσθήκη προϊόντων"),
    },
    "order_paid": {
        "tr": ("Siparişin alındı: #{n}", ["Merhaba {name},", "#{n} numaralı siparişini aldık. Satıcı hazırlayıp kargolayınca sana haber vereceğiz."], "Siparişlerim"),
        "en": ("We received your order: #{n}", ["Hi {name},", "We received your order #{n}. We will let you know when the seller ships it."], "My orders"),
        "mk": ("Ја примивме нарачката: #{n}", ["Здраво {name},", "Ја примивме твојата нарачка #{n}. Ќе те известиме кога продавачот ќе ја испрати."], "Мои нарачки"),
        "sq": ("E morëm porosinë: #{n}", ["Përshëndetje {name},", "E morëm porosinë tënde #{n}. Do të të njoftojmë kur shitësi ta dërgojë."], "Porositë e mia"),
        "sr": ("Примили смо поруџбину: #{n}", ["Здраво {name},", "Примили смо твоју поруџбину #{n}. Јавићемо ти када продавац пошаље пакет."], "Моје поруџбине"),
        "bs": ("Primili smo narudžbu: #{n}", ["Zdravo {name},", "Primili smo tvoju narudžbu #{n}. Javit ćemo ti kada prodavač pošalje paket."], "Moje narudžbe"),
        "bg": ("Получихме поръчката: #{n}", ["Здравей {name},", "Получихме поръчката ти #{n}. Ще ти кажем, когато продавачът я изпрати."], "Моите поръчки"),
        "el": ("Λάβαμε την παραγγελία: #{n}", ["Γεια σου {name},", "Λάβαμε την παραγγελία σου #{n}. Θα σε ενημερώσουμε όταν ο πωλητής την αποστείλει."], "Οι παραγγελίες μου"),
    },
}
for _ev in EVENTS.values():
    for _c in ("hr", "cnr"):
        _ev[_c] = _ev["bs"]

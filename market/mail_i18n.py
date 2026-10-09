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

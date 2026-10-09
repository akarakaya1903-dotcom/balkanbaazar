from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from django.contrib.auth.decorators import login_required
from . import views, views_2fa, views_account, views_google, views_market, views_staff

app_name = "market"

urlpatterns = [
    path("", views.home, name="home"),
    path("ilanlar/", views.listings, name="listings"),
    path("ilan/<int:pk>/sikayet/", views_market.report_listing, name="report_listing"),
    path("uyelik/dogrula/<str:token>/", views_account.verify_email, name="verify_email"),
    path("uyelik/dogrulama-gonder/", views_account.resend_verification, name="resend_verification"),
    path("ilanlarim/<int:pk>/yenile/", views_market.renew_listing, name="renew_listing"),
    path("satici/<int:pk>/", views_market.seller_profile, name="seller_profile"),
    path("engelle/<int:pk>/", views_market.block_user, name="block_user"),
    path("kategori/<str:mode>/<slug:cat>/", views.seo_listing, name="seo_category"),
    path("kategori/<str:mode>/<slug:cat>/<slug:sub>/", views.seo_listing, name="seo_sub"),
    path("sehir/<slug:city>/<str:mode>/<slug:cat>/", views.seo_listing, name="seo_city"),
    path("sehir/<slug:city>/<str:mode>/<slug:cat>/<slug:sub>/", views.seo_listing, name="seo_city_sub"),
    path("bildirim/abone/", views_market.push_subscribe, name="push_subscribe"),
    path("mesaj-durumu/", views_market.messages_status, name="messages_status"),
    path("kayitli-aramalar/", views_market.saved_searches, name="saved_searches"),
    path("kayitli-aramalar/kaydet/", views_market.save_search, name="save_search"),
    path("kayitli-aramalar/<int:pk>/sil/", views_market.delete_saved_search, name="delete_saved_search"),
    path("panel/dogrulama/", views_account.panel_verification, name="panel_verification"),
    path("satici/<int:pk>/degerlendir/", views_market.review_seller, name="review_seller"),
    path("dogrulama-belge/<int:pk>/", views_market.verification_doc, name="verification_doc"),
    path("trend/", views.trending, name="trending"),
    path("sayfa/<slug:slug>/", views.page_detail, name="page"),
    path("r/<int:pk>/", views.banner_go, name="banner_go"),
    path("ilan/<int:pk>/<slug:slug>/", views.listing_detail, name="listing_detail"),
    path("magazalar/", views.shops, name="shops"),
    path("magaza/<slug:slug>/", views.shop_detail, name="shop_detail"),
    path("paketler/", views.pricing, name="pricing"),

    # uyelik
    path("uyelik/kayit/", views_account.signup, name="signup"),
    path("uyelik/iki-adim/", views_2fa.staff_2fa, name="staff_2fa"),
    path("uyelik/giris/",
         auth_views.LoginView.as_view(template_name="market/account/login.html"),
         name="login"),
    path("uyelik/cikis/", auth_views.LogoutView.as_view(next_page="market:home"),
         name="logout"),

    path("uyelik/profil/", views_account.profile, name="profile"),
    path("uyelik/hesabi-sil/", views_account.delete_account, name="delete_account"),
    path("uyelik/sifre-sifirla/", auth_views.PasswordResetView.as_view(
        template_name="market/account/pw_form.html",
        email_template_name="market/account/pw_email.txt",
        subject_template_name="market/account/pw_subject.txt",
        success_url=reverse_lazy("market:password_reset_done")), name="password_reset"),
    path("uyelik/sifre-sifirla/gonderildi/", auth_views.PasswordResetDoneView.as_view(
        template_name="market/account/pw_done.html"), name="password_reset_done"),
    path("uyelik/sifre-sifirla/<uidb64>/<token>/", views_account.PwResetConfirm.as_view(), name="password_reset_confirm"),
    path("uyelik/sifre-degistir/", login_required(views_account.PwChange.as_view()), name="password_change"),
    path("uyelik/google/", views_google.google_login, name="google_login"),
    path("uyelik/google/geri/", views_google.google_callback, name="google_callback"),
    path("uyelik/sifre-sifirla/tamam/", auth_views.PasswordResetCompleteView.as_view(
        template_name="market/account/pw_complete.html"), name="password_reset_complete"),

    # magaza basvurusu
    path("magaza-basvuru/", views_account.shop_apply, name="shop_apply"),

    # satici paneli
    path("panel/", views_account.panel, name="panel"),
    path("panel/urunler/", views_account.panel_products, name="panel_products"),
    path("panel/urun/yeni/", views_account.panel_product_form, name="panel_product_new"),
    path("panel/urun/<int:pk>/", views_account.panel_product_form, name="panel_product_edit"),
    path("panel/urun/<int:pk>/sil/", views_account.panel_product_delete,
         name="panel_product_delete"),
    path("panel/magaza/", views_account.panel_settings, name="panel_settings"),
    path("panel/odeme/", views_account.panel_billing, name="panel_billing"),
    path("panel/siparisler/", views_account.panel_orders, name="panel_orders"),
    path("panel/siparis/<int:item_id>/kargo/", views_account.panel_order_ship, name="panel_order_ship"),

    # ozel yonetim paneli (site sahibi)
    path("yonetim/", views_staff.dashboard, name="staff_dashboard"),
    path("yonetim/basvurular/", views_staff.applications, name="staff_applications"),
    path("yonetim/basvuru/<int:pk>/onayla/", views_staff.application_approve, name="staff_app_approve"),
    path("yonetim/basvuru/<int:pk>/reddet/", views_staff.application_reject, name="staff_app_reject"),
    path("yonetim/magazalar/", views_staff.shops, name="staff_shops"),
    path("yonetim/magaza/<int:pk>/dogrula/", views_staff.shop_toggle_verified, name="staff_shop_verify"),
    path("yonetim/magaza/<int:pk>/paket/", views_staff.shop_set_plan, name="staff_shop_plan"),
    path("yonetim/ilanlar/", views_staff.listings, name="staff_listings"),
    path("yonetim/ilan/<int:pk>/durum/", views_staff.listing_toggle_active, name="staff_listing_toggle"),
    path("yonetim/ilan/<int:pk>/sil/", views_staff.listing_delete, name="staff_listing_delete"),
    path("yonetim/ulkeler/", views_staff.countries, name="staff_countries"),
    path("yonetim/onbellek-temizle/", views_staff.clear_cache, name="staff_clear_cache"),

    # bireysel ilan verme
    path("ilanlarim/", views_market.my_listings, name="my_listings"),
    path("ilanlarim/yeni/", views_market.my_listing_form, name="my_listing_new"),
    path("ilanlarim/<int:pk>/", views_market.my_listing_form, name="my_listing_edit"),
    path("ilanlarim/<int:pk>/sil/", views_market.my_listing_delete, name="my_listing_delete"),

    # sepet / odeme
    path("sepet/", views_market.cart_view, name="cart"),
    path("sepet/ekle/<int:pk>/", views_market.cart_add, name="cart_add"),
    path("sepet/adet/<str:key>/", views_market.cart_set_qty, name="cart_set_qty"),
    path("sepet/cikar/<str:key>/", views_market.cart_remove, name="cart_remove"),
    path("odeme/", views_market.checkout, name="checkout"),
    path("odeme/basarili/", views_market.order_payment_success, name="order_payment_success"),
    path("odeme/webhook/", views_market.stripe_webhook, name="stripe_webhook"),
    path("siparis/<int:pk>/tamam/", views_market.order_success, name="order_success"),
    path("siparis/<int:pk>/iptal/", views_market.order_cancel, name="order_cancel"),
    path("siparislerim/", views_market.my_orders, name="my_orders"),
    path("yorum/<int:order_item_id>/", views_market.review_create, name="review_create"),

    # favoriler
    path("favorilerim/", views_market.my_favorites, name="my_favorites"),
    path("favori/ilan/<int:pk>/", views_market.favorite_toggle_listing, name="favorite_toggle_listing"),
    path("favori/magaza/<int:pk>/", views_market.favorite_toggle_shop, name="favorite_toggle_shop"),

    # ilan one cikarma
    path("vitrin/<int:listing_id>/", views_market.boost_options, name="boost_options"),
    path("vitrin/<int:listing_id>/odeme/", views_market.boost_checkout, name="boost_checkout"),
    path("vitrin/odeme/basarili/", views_market.boost_payment_success, name="boost_payment_success"),

    # mesajlasma
    path("mesajlar/", views_market.inbox, name="inbox"),
    path("mesaj/baslat/<int:listing_id>/", views_market.start_conversation, name="start_conversation"),
    path("mesaj/<int:pk>/", views_market.message_thread, name="message_thread"),

    # tercihler
    path("ayar/ulke/<str:code>/", views.set_country, name="set_country"),
    path("ayar/dil/<str:code>/", views.set_lang, name="set_lang"),
    path("ayar/mod/<str:code>/", views.set_mode, name="set_mode"),
]

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views, views_account, views_market, views_staff

app_name = "market"

urlpatterns = [
    path("", views.home, name="home"),
    path("ilanlar/", views.listings, name="listings"),
    path("trend/", views.trending, name="trending"),
    path("r/<int:pk>/", views.banner_go, name="banner_go"),
    path("ilan/<int:pk>/<slug:slug>/", views.listing_detail, name="listing_detail"),
    path("magazalar/", views.shops, name="shops"),
    path("magaza/<slug:slug>/", views.shop_detail, name="shop_detail"),
    path("paketler/", views.pricing, name="pricing"),

    # uyelik
    path("uyelik/kayit/", views_account.signup, name="signup"),
    path("uyelik/giris/",
         auth_views.LoginView.as_view(template_name="market/account/login.html"),
         name="login"),
    path("uyelik/cikis/", auth_views.LogoutView.as_view(next_page="market:home"),
         name="logout"),

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

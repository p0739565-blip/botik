# Впишите сюда ваши реальные ссылки конфигов — тот же список, что был
# в vlessLinks / deadLinks в worker.js. Формат идентичен: каждая строка —
# готовая vless:// или hy2:// ссылка с #<название WiFi/точки>.

VLESS_LINK_TEMPLATES: list[str] = [
    "vless://f182edc9-0f53-477b-9496-ec481c983467@vd.freelink.online:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=vd.freelink.online&fp=firefox&pbk=DrpLWgeVVCQkLvIh6TxJ7qQLxGgEcyNcEvJypSPYX1Y&type=tcp&headerType=none&spx=%2F#🇷🇺%20Youtube%20без%20рекламы,%20Инста%20(WiFi)",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@dutch1.freelink.online:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=dutch1.freelink.online&fp=firefox&pbk=we-aFs9VY_MApvI4kqHQxHbQcKLD-_fTYGRosHx0CAw&spx=/#%F0%9F%87%B3%F0%9F%87%B1%20%20%F0%9F%87%B3%F0%9F%87%B1%20%D0%9D%D0%B8%D0%B4%D0%B5%D1%80%D0%BB%D0%B0%D0%BD%D0%B4%D1%8B%20%28WiFi%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@de10.freelink.online:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=de10.freelink.online&fp=firefox&pbk=z97armwRYEXFuOLtlU_3pKNWhyGA6ZJZRN0Ncm_eQlY&spx=/#%F0%9F%87%A9%F0%9F%87%AA%20%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D1%8F%20%28WiFi%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@de1.freelink.online:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=de1.freelink.online&fp=firefox&pbk=mnQJ6-RQXydInjgm4IrZF9fbjSHmpk9cKM0O_FCcz3M&spx=/#%F0%9F%87%A9%F0%9F%87%AA%20%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D1%8F%20%28WiFi%29%202",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@swe.freelink.online:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=swe.freelink.online&fp=firefox&pbk=FTlJ8M-gESBLE6tvfBcgKTI0dEqmEejVBkK9ejSzvgg&spx=/#%F0%9F%87%B8%F0%9F%87%AA%20%D0%A8%D0%B2%D0%B5%D1%86%D0%B8%D1%8F%20%28WiFi%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@lat.freelink.online:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=lat.freelink.online&fp=edge&pbk=mnQJ6-RQXydInjgm4IrZF9fbjSHmpk9cKM0O_FCcz3M&spx=/#%F0%9F%87%B1%F0%9F%87%BB%20%D0%9B%D0%B0%D1%82%D0%B2%D0%B8%D1%8F%20%28WiFi%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@fin6.freelink.online:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=fin6.freelink.online&fp=firefox&pbk=Z_CTQe8qDDF4koR1mj4Qst3nFmMWFS1b6NHMNGXZGmA&spx=/#%F0%9F%87%AB%F0%9F%87%AE%20%20%D0%A4%D0%B8%D0%BD%D0%BB%D1%8F%D0%BD%D0%B4%D0%B8%D1%8F%20%28WiFi%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@93.88.206.164:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=pl.freelink.online&fp=firefox&pbk=we-aFs9VY_MApvI4kqHQxHbQcKLD-_fTYGRosHx0CAw&spx=/#%F0%9F%87%B5%F0%9F%87%B1%20%D0%9F%D0%BE%D0%BB%D1%8C%D1%88%D0%B0%20%28WiFi%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@vd.freelink.online:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=vd.freelink.online&fp=firefox&pbk=DrpLWgeVVCQkLvIh6TxJ7qQLxGgEcyNcEvJypSPYX1Y&spx=/#%F0%9F%87%B7%F0%9F%87%BA%20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%20%28WiFi%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@pra2.freelink.online:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=pra2.freelink.online&fp=firefox&pbk=mnQJ6-RQXydInjgm4IrZF9fbjSHmpk9cKM0O_FCcz3M&spx=/#%F0%9F%87%A8%F0%9F%87%BF%20%D0%A7%D0%B5%D1%85%D0%B8%D1%8F%20%28WiFi%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@45.11.26.30:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=media-ru.fl-work.shop&fp=firefox&pbk=HjLnK08_mKtaUa94dpwpxMaX7nbBlMGgk-dNGB_IrF4&spx=/#%F0%9F%87%B7%F0%9F%87%BA%20%D0%9C%D0%BE%D0%B1.%20%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%82%D0%BE%D1%80%D1%8B%200%20%284G/LTE%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@fl-work.shop:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=fl-work.shop&fp=firefox&pbk=KfLHeaqRpA8psMOPYIvObhwDxsaTTjhTXc309XVGFmA&spx=/#%F0%9F%87%B7%F0%9F%87%BA%20%D0%9C%D0%BE%D0%B1.%20%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%82%D0%BE%D1%80%D1%8B%201%20%284G/LTE%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@213.226.112.181:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=fl-work.shop&fp=firefox&pbk=KfLHeaqRpA8psMOPYIvObhwDxsaTTjhTXc309XVGFmA&spx=/#%F0%9F%87%B7%F0%9F%87%BA%20%D0%9C%D0%BE%D0%B1.%20%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%82%D0%BE%D1%80%D1%8B%202%20%284G/LTE%29",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@azu6cjf7vo.a.trbcdn.net:443?encryption=none&type=xhttp&security=tls&sni=azu6cjf7vo.a.trbcdn.net&fp=firefox&alpn=h2,http/1.1#%F0%9F%87%B7%F0%9F%87%BA%20%20%F0%9F%87%B7%F0%9F%87%BA%20%D0%9C%D0%BE%D0%B1.%20%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%82%D0%BE%D1%80%D1%8B%203%20%284G/LTE%29%20",
    "vless://f182edc9-0f53-477b-9496-ec481c983467@fl-work.shop:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=fl-work.shop&fp=firefox&pbk=KfLHeaqRpA8psMOPYIvObhwDxsaTTjhTXc309XVGFmA&spx=/#%F0%9F%87%B7%F0%9F%87%BA%20%20%F0%9F%87%B7%F0%9F%87%BA%20%D0%9C%D0%BE%D0%B1.%20%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%82%D0%BE%D1%80%D1%8B%204%20%284G/LTE%29%20",
    "hy2://f182edc9-0f53-477b-9496-ec481c983467@de1.freelink.online:443?insecure=0&sni=de1.freelink.online&alpn=h3&pinSHA256=&obfs=&obfs-password=#%F0%9F%87%A9%F0%9F%87%AA%20%D0%93%D0%B5%D1%80%D0%BC%D0%B0%D0%BD%D0%B8%D1%8F%20%28WiFi%29%20%28%D0%B7%D0%B0%D0%BF%D0%B0%D1%81.%29",
    "hy2://f182edc9-0f53-477b-9496-ec481c983467@pra2.freelink.online:443?insecure=0&sni=pra2.freelink.online&alpn=h3&pinSHA256=&obfs=&obfs-password=#%F0%9F%87%A8%F0%9F%87%BF%20%F0%9F%87%A8%F0%9F%87%BF%20%D0%A7%D0%B5%D1%85%D0%B8%D1%8F%20%28WiFi%29%20%28%D0%B7%D0%B0%D0%BF%D0%B0%D1%81.%29",
    "hy2://f182edc9-0f53-477b-9496-ec481c983467@fin6.freelink.online:443?insecure=0&sni=fin6.freelink.online&alpn=h3&pinSHA256=&obfs=&obfs-password=#%F0%9F%87%AB%F0%9F%87%AE%20%F0%9F%87%AB%F0%9F%87%AE%20%D0%A4%D0%B8%D0%BD%D0%BB%D1%8F%D0%BD%D0%B4%D0%B8%D1%8F%20%28WiFi%29%20%28%D0%B7%D0%B0%D0%BF%D0%B0%D1%81.%29",
]

# Ссылки-заглушки, которые отдаются, если подписка истекла или не найдена —
# аналог deadLinks в вашем воркере (например, ведут на неработающий сервер
# с понятным названием "Подписка закончилась")
DEAD_LINKS: list[str] = [
    "vless://00000000-0000-0000-0000-000000000000@240.0.0.1:443?flow=xtls-rprx-vision&"
    "encryption=none&type=tcp&security=reality&fp=firefox&sni=eh.vk.ru&"
    "pbk=AAZjVvbC7AwPKot_1ygO5VMpN7XYifCA7lG0RNR5sEk&sid=0000000000000000"
    "#%E2%9B%94%20Подписка%20закончилась",
]

"""def render_links(uuid: str) -> list[str]:
    #Подставляет персональный uuid пользователя во все шаблоны.
    return [template.format(uuid=uuid) for template in VLESS_LINK_TEMPLATES]"""

def render_links(uuid: str) -> list[str]:
    """Возвращает готовые конфиги как есть."""
    return VLESS_LINK_TEMPLATES.copy()
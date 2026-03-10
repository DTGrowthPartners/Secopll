DT_KEYWORDS: dict[str, list[str]] = {
    "Meta Ads": [
        "meta ads",
        "facebook ads",
        "instagram ads",
        "pauta digital",
        "publicidad digital",
        "campañas digitales",
        "campanas digitales",
        "social ads",
        "community manager",
        "pauta en redes sociales",
        "publicidad en redes sociales",
        "anuncios digitales",
        "pauta publicitaria digital",
        "google ads",
        "tiktok ads",
    ],
    "Desarrollo Web": [
        "desarrollo web",
        "pagina web",
        "página web",
        "sitio web",
        "landing page",
        "tienda virtual",
        "e-commerce",
        "ecommerce",
        "plataforma web",
        "portal web",
        "diseño web",
        "diseno web",
        "aplicacion web",
        "aplicación web",
        "desarrollo de software web",
        "tienda en linea",
        "tienda en línea",
    ],
    "Automatizaciones & IA": [
        "inteligencia artificial",
        "machine learning",
        "chatbot",
        "chat bot",
        "bot de whatsapp",
        "whatsapp business",
        "bot conversacional",
        "automatización de procesos",
        "automatizacion de procesos",
        "flujos automatizados",
        "asistente virtual",
        "asistente digital",
    ],
    "Marketing Digital": [
        "marketing digital",
        "mercadeo digital",
        "social media",
        "manejo de redes sociales",
        "administración de redes sociales",
        "administracion de redes sociales",
        "estrategia de contenido digital",
        "branding digital",
        "plan de medios digitales",
        "posicionamiento web",
        "posicionamiento digital",
        "community manager",
        "contenidos digitales",
        "gestión de redes sociales",
        "gestion de redes sociales",
    ],
    "Consultoría Digital": [
        "consultoría digital",
        "consultoria digital",
        "transformación digital",
        "transformacion digital",
        "estrategia digital",
    ],
}


def match_keywords(text: str) -> dict[str, list[str]]:
    """Check text against all keyword categories.

    Returns a dict mapping each matched service to the list of keywords found.
    Only returns services that had at least one match.
    """
    text_upper = text.upper()
    matches: dict[str, list[str]] = {}

    for service, keywords in DT_KEYWORDS.items():
        found = [kw for kw in keywords if kw.upper() in text_upper]
        if found:
            matches[service] = found

    return matches


def passes_prefilter(title: str, description: str | None = None) -> tuple[bool, dict[str, list[str]]]:
    """Run the keyword pre-filter on a contract's title and description.

    Returns (passed, matches) where matches maps service -> matched keywords.
    """
    combined = title
    if description:
        combined = f"{combined} {description}"

    matches = match_keywords(combined)
    return bool(matches), matches

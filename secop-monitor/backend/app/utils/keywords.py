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
        "gestión de redes",
        "gestion de redes",
        "community manager",
        "pauta en redes",
        "publicidad en redes",
        "anuncios digitales",
        "pauta publicitaria digital",
        "campañas publicitarias digitales",
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
        "plataforma digital",
        "portal digital",
        "tienda en linea",
        "tienda en línea",
    ],
    "Automatizaciones & IA": [
        "inteligencia artificial",
        "automatización",
        "automatizacion",
        "machine learning",
        "ia ",
        "i.a.",
        "transformacion digital",
        "transformación digital",
        "flujos automatizados",
        "rpa",
        "procesamiento de datos",
        "analítica de datos",
        "analitica de datos",
        "big data",
        "ciencia de datos",
        "automatización de procesos",
        "automatizacion de procesos",
    ],
    "Chatbot": [
        "chatbot",
        "chat bot",
        "asistente virtual",
        "bot de whatsapp",
        "whatsapp business",
        "asistente ia",
        "atención automatizada",
        "atencion automatizada",
        "bot conversacional",
        "agente virtual",
        "asistente digital",
    ],
    "Marketing Digital": [
        "marketing digital",
        "estrategia digital",
        "posicionamiento digital",
        "seo",
        "sem",
        "redes sociales",
        "estrategia de contenido",
        "comunicación digital",
        "comunicacion digital",
        "medios digitales",
        "contenido digital",
        "community",
        "influencer",
        "branding digital",
        "mercadeo digital",
        "social media",
        "manejo de redes",
        "administración de redes sociales",
        "administracion de redes sociales",
        "contenidos digitales",
        "plan de medios digitales",
        "estrategia de comunicación digital",
    ],
    "Consultoría Digital": [
        "consultoría digital",
        "consultoria digital",
        "asesoría digital",
        "asesoria digital",
        "transformación digital",
        "transformacion digital",
        "capacitación digital",
        "capacitacion digital",
        "formación digital",
        "formacion digital",
        "tic",
        "tics",
        "tecnologías de la información",
        "tecnologias de la informacion",
        "gobierno digital",
        "innovación digital",
        "innovacion digital",
        "adopción tecnológica",
        "adopcion tecnologica",
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

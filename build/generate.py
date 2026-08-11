#!/usr/bin/env python3
"""Static site generator for cadeauxparebrise.fr.

Assembles partials (header/footer/tracking/tunnel-modal) + a shell template +
per-page content into final static HTML files, written with clean-URL folder
structure (e.g. /zones/pare-brise-lille/index.html) and root-absolute asset
paths (/css, /js, /images) so the site works from any nesting level.

Run: python build/generate.py
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PARTIALS = BUILD / "partials"
TEMPLATES = BUILD / "templates"
CONTENT = BUILD / "content"
DATA = BUILD / "data"

SITE_NAME = "Cadeaux Pare-Brise"
PHONE = "07 57 63 42 51"
SITE_URL = "https://cadeauxparebrise.fr"
BUILD_DATE = date.today().isoformat()

# Collected as pages are rendered, then used to emit sitemap.xml at the end.
SITEMAP_ENTRIES = []


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  -> {path.relative_to(ROOT)}")


HEADER = read(PARTIALS / "header.html")
FOOTER = read(PARTIALS / "footer.html")
TRACKING = read(PARTIALS / "tracking.html")
MODAL = read(PARTIALS / "tunnel-modal.html")
SHELL = read(TEMPLATES / "shell.html")


def render(output_path, title, description, body, extra_head="", priority="0.7"):
    canonical_path = "/" if output_path == "" else f"/{output_path}/"

    html = SHELL
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{DESCRIPTION}}", description)
    html = html.replace("{{PATH}}", canonical_path)
    html = html.replace("{{EXTRA_HEAD}}", extra_head)
    html = html.replace("{{TRACKING}}", TRACKING)
    html = html.replace("{{HEADER}}", HEADER)
    html = html.replace("{{BODY}}", body)
    html = html.replace("{{FOOTER}}", FOOTER)
    html = html.replace("{{MODAL}}", MODAL)

    if output_path == "":
        out_file = ROOT / "index.html"
    else:
        out_file = ROOT / output_path / "index.html"
    write(out_file, html)

    SITEMAP_ENTRIES.append((canonical_path, priority))


# ---------------------------------------------------------------------------
# Core static pages (content authored directly as HTML in build/content/*.html)
# ---------------------------------------------------------------------------
CORE_PAGES = [
    {
        "path": "",
        "content": "home.html",
        "title": "Cadeaux Pare-Brise — Jusqu'à 200€ offerts, remplacement à domicile Nord Pas-de-Calais",
        "description": "Remplacement de pare-brise à domicile dans le Nord Pas-de-Calais (59 & 62). Jusqu'à 200€ offerts par virement bancaire. Zéro avance de frais, toutes assurances, intervention sous 24-48h.",
        "priority": "1.0",
    },
    {
        "path": "offre-pare-brise",
        "content": "offre-pare-brise.html",
        "title": "Jusqu'à 200€ offerts pour votre pare-brise | Cadeaux Pare-Brise",
        "description": "Découvrez l'offre Cadeaux Pare-Brise : jusqu'à 200€ versés par virement bancaire pour tout remplacement de pare-brise, en plus de votre prise en charge assurance.",
        "priority": "0.9",
    },
    {
        "path": "notre-cadeau",
        "content": "notre-cadeau.html",
        "title": "Notre cadeau : pourquoi Cadeaux Pare-Brise vous récompense | Cadeaux Pare-Brise",
        "description": "Découvrez la philosophie de Cadeaux Pare-Brise : pourquoi et comment nous vous offrons jusqu'à 200€ en plus de la prise en charge assurance de votre remplacement.",
        "priority": "0.8",
    },
    {
        "path": "remplacement-pare-brise",
        "content": "remplacement-pare-brise.html",
        "title": "Remplacement de pare-brise à domicile | Cadeaux Pare-Brise",
        "description": "Remplacement de pare-brise à domicile par des techniciens certifiés : vitrage d'origine, calibrage ADAS inclus, garantie 10 ans. Nord Pas-de-Calais.",
        "priority": "0.9",
    },
    {
        "path": "reparation-impact",
        "content": "reparation-impact.html",
        "title": "Réparation d'impact de pare-brise | Cadeaux Pare-Brise",
        "description": "Un impact peut souvent être réparé sans remplacer tout le pare-brise. Intervention rapide à domicile, souvent sans franchise. Nord Pas-de-Calais.",
        "priority": "0.8",
    },
    {
        "path": "pare-brise-a-domicile",
        "content": "pare-brise-a-domicile.html",
        "title": "Pare-brise à domicile : comment ça marche | Cadeaux Pare-Brise",
        "description": "Le remplacement de pare-brise à domicile expliqué : à quoi s'attendre, ce qu'il faut prévoir, avantages par rapport à un centre auto. Nord Pas-de-Calais.",
        "priority": "0.8",
    },
    {
        "path": "comment-ca-marche",
        "content": "comment-ca-marche.html",
        "title": "Comment ça marche ? | Cadeaux Pare-Brise",
        "description": "Découvrez le déroulé complet de votre demande à votre remplacement de pare-brise : rappel, prise en charge assurance, intervention, versement de votre offre.",
        "priority": "0.7",
    },
    {
        "path": "avis",
        "content": "avis.html",
        "title": "Avis clients | Cadeaux Pare-Brise",
        "description": "Découvrez les avis de nos clients du Nord Pas-de-Calais sur nos interventions de remplacement de pare-brise à domicile.",
        "priority": "0.6",
    },
    {
        "path": "faq",
        "content": "faq.html",
        "title": "Questions fréquentes | Cadeaux Pare-Brise",
        "description": "Toutes les réponses à vos questions sur l'offre des 200€, l'assurance bris de glace, le calibrage ADAS et le déroulé de l'intervention.",
        "priority": "0.6",
    },
    {
        "path": "contact",
        "content": "contact.html",
        "title": "Contact | Cadeaux Pare-Brise",
        "description": "Contactez Cadeaux Pare-Brise au 07 57 63 42 51 pour toute question sur votre remplacement de pare-brise dans le Nord Pas-de-Calais.",
        "priority": "0.5",
    },
    {
        "path": "assurances",
        "content": "assurances.html",
        "title": "Votre assurance et le bris de glace | Cadeaux Pare-Brise",
        "description": "AXA, MAIF, MACIF, Allianz, MAAF, GMF, MMA, Groupama, Matmut... découvrez comment fonctionne la prise en charge bris de glace selon votre assureur.",
        "priority": "0.9",
    },
    {
        "path": "zones",
        "content": "zones.html",
        "title": "Zones d'intervention Nord Pas-de-Calais | Cadeaux Pare-Brise",
        "description": "Cadeaux Pare-Brise intervient dans tout le Nord et le Pas-de-Calais : Lille, Roubaix, Tourcoing, Lens, Arras, Béthune, Calais et bien d'autres villes.",
        "priority": "0.9",
    },
    {
        "path": "mentions-legales",
        "content": "mentions-legales.html",
        "title": "Mentions légales | Cadeaux Pare-Brise",
        "description": "Mentions légales du site Cadeaux Pare-Brise.",
        "priority": "0.3",
    },
    {
        "path": "politique-confidentialite",
        "content": "politique-confidentialite.html",
        "title": "Politique de confidentialité | Cadeaux Pare-Brise",
        "description": "Politique de confidentialité et protection des données personnelles du site Cadeaux Pare-Brise.",
        "priority": "0.3",
    },
]

print("Core pages:")
for page in CORE_PAGES:
    body = read(CONTENT / page["content"])
    render(page["path"], page["title"], page["description"], body, priority=page["priority"])


# ---------------------------------------------------------------------------
# Zone (city) pages — data-driven, distinct copy per city
# ---------------------------------------------------------------------------
def ville_body(v):
    quartiers_html = (
        f"""<p class="section-lead">
          Dans {v['nom']} même, nous intervenons dans tous les quartiers, notamment
          {v['quartiers']}.
        </p>"""
        if v.get("quartiers")
        else ""
    )

    return f"""  <section class="hero page-hero">
    <div class="container">
      <p class="breadcrumb"><a href="/">Accueil</a> / <a href="/zones/">Zones</a> / {v['nom']}</p>
      <div class="page-hero-inner">
        <span class="eyebrow">{v['dept_nom']} ({v['dept']})</span>
        <h1>Remplacement de pare-brise à {v['nom']} à domicile</h1>
        <p>{v['intro']} Intervention à domicile ou sur votre lieu de travail, jusqu'à 200€ offerts pour votre remplacement.</p>
        <div class="hero-cta-row">
          <a href="#" class="btn btn-primary btn-lg" data-open-tunnel>Vérifier mon offre à {v['nom']}</a>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container section-grid">
      <div>
        <span class="section-eyebrow">Secteur couvert</span>
        <h2>{v['nom']} et les communes voisines</h2>
        <p class="section-lead">
          Nos techniciens interviennent à {v['nom']} ainsi que dans les communes alentour
          telles que {v['environs']}. Comme partout dans le {v['dept_nom']} et le Pas-de-Calais,
          l'intervention se fait directement chez vous, sur votre lieu de travail, ou tout
          autre endroit de votre choix.
        </p>
        {quartiers_html}
        <ul class="check-list">
          <li>Intervention à domicile ou sur votre lieu de travail à {v['nom']}</li>
          <li>Délai moyen de 24 à 48h selon les disponibilités</li>
          <li>Zéro avance de frais, toutes assurances acceptées</li>
          <li>Calibrage ADAS inclus si votre véhicule en est équipé</li>
          <li>Jusqu'à 200€ offerts par virement bancaire</li>
        </ul>
        <a href="#" class="btn btn-primary" data-open-tunnel>Vérifier mon éligibilité</a>
      </div>
      <div class="insurer-card">
        <p class="insurer-title">Pourquoi Cadeaux Pare-Brise à {v['nom']} ?</p>
        <div class="check-list" style="margin:0;">
          <div style="padding:15px; border:1px solid var(--border); border-radius:14px; margin-bottom:11px;">🏠 Vous ne vous déplacez pas</div>
          <div style="padding:15px; border:1px solid var(--border); border-radius:14px; margin-bottom:11px;">🛡️ Garantie 10 ans sur la pose</div>
          <div style="padding:15px; border:1px solid var(--border); border-radius:14px;">💰 Jusqu'à 200€ offerts</div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="container">
      <div class="section-heading-center">
        <span class="section-eyebrow">Sur le terrain</span>
        <h2>Une intervention à {v['nom']}, comme partout dans le {v['dept_nom']}</h2>
      </div>
      <div class="photo-grid" style="max-width:720px; margin:0 auto; grid-template-columns:1fr;">
        <figure class="photo-card">
          <img src="/images/{v['photo']}" alt="Technicien Cadeaux Pare-Brise en intervention">
          <figcaption>Remplacement à domicile avec équipement professionnel complet</figcaption>
        </figure>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-heading-center">
        <span class="section-eyebrow">Questions fréquentes</span>
        <h2>Le remplacement de pare-brise à {v['nom']}</h2>
      </div>
      <div class="faq-list">
        <details class="faq-item">
          <summary>Intervenez-vous vraiment à {v['nom']} ?</summary>
          <div class="faq-answer"><p>Oui, nos techniciens interviennent directement à {v['nom']} et dans les communes voisines ({v['environs']}), chez vous ou sur votre lieu de travail.</p></div>
        </details>
        <details class="faq-item">
          <summary>Quel est le délai d'intervention à {v['nom']} ?</summary>
          <div class="faq-answer"><p>Comme dans le reste de notre zone de couverture ({v['dept_nom']} et Pas-de-Calais), l'intervention a lieu sous 24 à 48h en moyenne, selon les disponibilités.</p></div>
        </details>
        <details class="faq-item">
          <summary>Dois-je avancer les frais pour un remplacement à {v['nom']} ?</summary>
          <div class="faq-answer"><p>Non, nous travaillons avec toutes les assurances et facturons directement l'intervention à votre assureur, où que vous soyez dans le {v['dept_nom']} ou le Pas-de-Calais.</p></div>
        </details>
        <details class="faq-item">
          <summary>Quelle assurance est acceptée à {v['nom']} ?</summary>
          <div class="faq-answer"><p>Toutes les compagnies et mutuelles d'assurance, sans exception. Consultez notre page <a href="/assurances/">assurances</a> pour voir le détail par assureur.</p></div>
        </details>
      </div>
    </div>
  </section>

  <section class="cta-final">
    <div class="container cta-final-inner">
      <div>
        <span class="cta-tag">Jusqu'à 200€ offerts après votre remplacement</span>
        <h2>Faites remplacer votre pare-brise à {v['nom']}</h2>
        <p>Estimation gratuite en 30 secondes.</p>
      </div>
      <div class="cta-final-actions">
        <a href="tel:0757634251" class="btn btn-white">📞 {PHONE}</a>
        <a href="#" class="btn btn-primary" data-open-tunnel>Vérifier mon éligibilité</a>
      </div>
    </div>
  </section>
"""


villes = json.loads(read(DATA / "villes.json"))
print("\nZone pages:")
for v in villes:
    title = f"Pare-brise {v['nom']} — Remplacement à domicile | Cadeaux Pare-Brise"
    description = f"Remplacement de pare-brise à domicile à {v['nom']} ({v['dept']}). Jusqu'à 200€ offerts, zéro avance de frais, intervention sous 24-48h."
    render(f"zones/{v['slug']}", title, description, ville_body(v), priority="0.7")

# Zones hub already listed all cities statically in content/zones.html — nothing more to generate.


# ---------------------------------------------------------------------------
# Insurer pages — data-driven, distinct copy per insurer
# ---------------------------------------------------------------------------
def assurance_body(a):
    return f"""  <section class="hero page-hero">
    <div class="container">
      <p class="breadcrumb"><a href="/">Accueil</a> / <a href="/assurances/">Assurances</a> / {a['nom']}</p>
      <div class="page-hero-inner">
        <span class="eyebrow">{a['type']}</span>
        <h1>Pare-brise et assurance {a['nom']}</h1>
        <p>{a['intro']}</p>
        <div class="hero-cta-row">
          <a href="#" class="btn btn-primary btn-lg" data-open-tunnel>Vérifier ma prise en charge {a['nom']}</a>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-heading-center">
        <span class="section-eyebrow">Le déroulé</span>
        <h2>Comment fonctionne la déclaration avec {a['nom']} ?</h2>
      </div>
      <div class="steps-grid">
        <div class="step-card">
          <span class="step-number">1</span>
          <h3>Vous nous contactez</h3>
          <p>Formulaire en ligne ou téléphone : vous indiquez votre assureur {a['nom']} et le vitrage concerné.</p>
        </div>
        <div class="step-card">
          <span class="step-number">2</span>
          <h3>Nous déclarons le sinistre</h3>
          <p>Nous transmettons la déclaration de sinistre bris de glace à {a['nom']} en votre nom.</p>
        </div>
        <div class="step-card">
          <span class="step-number">3</span>
          <h3>Confirmation de prise en charge</h3>
          <p>Votre conseiller vous confirme les modalités (franchise éventuelle) avant toute intervention.</p>
        </div>
        <div class="step-card">
          <span class="step-number">4</span>
          <h3>Intervention &amp; facturation directe</h3>
          <p>Le technicien intervient chez vous, nous facturons directement {a['nom']}, sans avance de votre part.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="container section-grid">
      <div>
        <span class="section-eyebrow">Franchise &amp; avance de frais</span>
        <h2>Ce que vous aurez réellement à payer</h2>
        <p class="section-lead">
          Le montant de votre franchise bris de glace dépend de votre formule {a['nom']} et
          n'est pas le même pour tous les contrats : reportez-vous à vos conditions
          particulières ou demandez confirmation à votre conseiller. En général, la franchise
          est nulle ou très réduite pour une simple réparation d'impact, et plus élevée pour un
          remplacement complet. Dans tous les cas, <strong>vous n'avancez aucun frais</strong> :
          nous facturons directement {a['nom']}, vous ne réglez que votre franchise éventuelle,
          le jour de l'intervention.
        </p>
        <ul class="check-list">
          <li>Aucune avance de frais, quelle que soit votre formule {a['nom']}</li>
          <li>Franchise confirmée avant l'intervention, sans mauvaise surprise</li>
          <li>Aucun impact sur votre coefficient bonus/malus</li>
        </ul>
      </div>
      <div class="insurer-card">
        <p class="insurer-title">Libre choix de votre réparateur</p>
        <p style="color:var(--text); font-size:14px; margin-bottom:14px;">
          Quel que soit votre assureur, la loi Hamon vous garantit le libre choix de votre
          réparateur de vitrage automobile. Vous n'êtes jamais obligé de passer par le
          garage partenaire proposé par {a['nom']} : vous pouvez choisir Cadeaux Pare-Brise
          librement, sans que cela n'affecte votre prise en charge.
        </p>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-heading-center">
        <span class="section-eyebrow">Avant l'intervention</span>
        <h2>Documents utiles pour votre dossier {a['nom']}</h2>
      </div>
      <div class="advantages-grid">
        <div class="advantage-card">
          <span class="advantage-icon">🪪</span>
          <h3>Carte grise du véhicule</h3>
          <p>Pour identifier le vitrage exact compatible avec votre modèle.</p>
        </div>
        <div class="advantage-card">
          <span class="advantage-icon">📄</span>
          <h3>Attestation d'assurance {a['nom']}</h3>
          <p>Votre carte verte ou attestation en cours de validité.</p>
        </div>
        <div class="advantage-card">
          <span class="advantage-icon">🔢</span>
          <h3>Numéro de sinistre (si existant)</h3>
          <p>S'il vous a déjà été communiqué ; sinon, nous nous chargeons de la déclaration.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section section-alt">
    <div class="container">
      <div class="section-heading-center">
        <span class="section-eyebrow">Questions fréquentes</span>
        <h2>{a['nom']} et le bris de glace</h2>
      </div>
      <div class="faq-list">
        <details class="faq-item">
          <summary>Mon contrat {a['nom']} couvre-t-il le bris de glace ?</summary>
          <div class="faq-answer"><p>La plupart des contrats auto tous risques et de nombreux contrats au tiers étendu incluent cette garantie. Le plus simple est de vérifier votre éligibilité via notre formulaire : nous confirmons votre prise en charge en quelques minutes.</p></div>
        </details>
        <details class="faq-item">
          <summary>Dois-je avancer les frais avec {a['nom']} ?</summary>
          <div class="faq-answer"><p>Non, nous facturons directement votre remplacement à {a['nom']}. Vous ne réglez que votre franchise éventuelle, s'il y en a une, le jour de l'intervention.</p></div>
        </details>
        <details class="faq-item">
          <summary>Suis-je obligé d'utiliser le réparateur partenaire de {a['nom']} ?</summary>
          <div class="faq-answer"><p>Non. La loi Hamon vous garantit le libre choix de votre réparateur de vitrage, quel que soit votre assureur. Vous pouvez choisir Cadeaux Pare-Brise sans que cela n'affecte votre prise en charge.</p></div>
        </details>
        <details class="faq-item">
          <summary>Un sinistre bris de glace impacte-t-il mon bonus {a['nom']} ?</summary>
          <div class="faq-answer"><p>Non, un sinistre bris de glace ne modifie jamais votre coefficient bonus/malus, quel que soit votre assureur.</p></div>
        </details>
      </div>
    </div>
  </section>

  <section class="cta-final">
    <div class="container cta-final-inner">
      <div>
        <span class="cta-tag">Vérification immédiate</span>
        <h2>Vérifiez votre prise en charge {a['nom']}</h2>
        <p>3 questions, 30 secondes.</p>
      </div>
      <div class="cta-final-actions">
        <a href="tel:0757634251" class="btn btn-white">📞 {PHONE}</a>
        <a href="#" class="btn btn-primary" data-open-tunnel>Vérifier mon éligibilité</a>
      </div>
    </div>
  </section>
"""


assurances = json.loads(read(DATA / "assurances.json"))
print("\nInsurer pages:")
for a in assurances:
    title = f"Pare-brise et assurance {a['nom']} | Cadeaux Pare-Brise"
    description = f"Remplacement de pare-brise pris en charge avec votre assurance {a['nom']} : déclaration, franchise, documents nécessaires. Zéro avance de frais. Nord Pas-de-Calais."
    render(f"assurances/{a['slug']}", title, description, assurance_body(a), priority="0.7")

print(f"\nDone: {len(CORE_PAGES)} core pages, {len(villes)} zone pages, {len(assurances)} insurer pages.")

# ---------------------------------------------------------------------------
# robots.txt + sitemap.xml
# ---------------------------------------------------------------------------
ROBOTS_TXT = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
write(ROOT / "robots.txt", ROBOTS_TXT)

sitemap_items = "\n".join(
    f"""  <url>
    <loc>{SITE_URL}{path}</loc>
    <lastmod>{BUILD_DATE}</lastmod>
    <priority>{priority}</priority>
  </url>"""
    for path, priority in SITEMAP_ENTRIES
)
SITEMAP_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_items}
</urlset>
"""
write(ROOT / "sitemap.xml", SITEMAP_XML)
print(f"\nrobots.txt + sitemap.xml written ({len(SITEMAP_ENTRIES)} URLs).")

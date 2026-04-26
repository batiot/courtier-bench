"""
Rikees Sol MCP Stub Server

Bouchons (stubs) for Rikees Sol Espace Partenaire tools, covering:
  - Tarification / devis
  - Suivi des dossiers / portefeuille

All tools return deterministic stub data for benchmark evaluation.
No real API calls are made.
"""

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("rikees_mcp")


# ---------------------------------------------------------------------------
# Shared Enums
# ---------------------------------------------------------------------------


class Universe(str, Enum):
    EMPRUNTEUR = "emprunteur"
    SANTE = "sante"
    PREVOYANCE = "prevoyance"
    GAV = "gav"
    DOMMAGES = "dommages"
    OBSEQUES = "obseques"
    SANTE_INTERNATIONALE = "sante_internationale"
    SANTE_COLLECTIVE = "sante_collective"


class CoverageFormula(str, Enum):
    DC_PTIA = "DC_PTIA"
    DC_PTIA_IPT = "DC_PTIA_IPT"
    DC_PTIA_IPT_IPP = "DC_PTIA_IPT_IPP"


class RiskLevel(str, Enum):
    STANDARD = "standard"
    AGGREVE = "aggravé"
    TRES_AGGREVE = "très_aggravé"


class LoanType(str, Enum):
    IMMOBILIER = "immobilier"
    PROFESSIONNEL = "professionnel"
    CONSOMMATION = "consommation"
    LOCATIF = "locatif"


class DossierStatus(str, Enum):
    SUBMITTED = "submitted"
    PENDING_DOCUMENTS = "pending_documents"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REFUSED = "refused"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# ── TARIFICATION TOOLS ──────────────────────────────────────────────────────
#
# Chaque univers correspond à un système informatique distinct :
#   [Emprunteur / jRensure]          check_lemoine_eligibility, compare_offres,
#                                    compute_tarif_emprunteur
#   [Santé individuelle / Néoliane]  compute_tarif_sante
#   [Santé collective / GestiAssur]  compute_tarif_sante_collective
#   [Prévoyance TNS]                 compute_tarif_prevoyance
#   [GAV / AccidentVie]              compute_tarif_gav
#   [Dommages / IARD Pro]            compute_tarif_dommages
#   [Obsèques / ObsèquesFrance]      compute_tarif_obseques
#   [Santé internationale / GlobalCare] compute_tarif_sante_internationale
#   [TNS/Madelin]                    get_madelin_plafonds
#   [Collectif / CCN]                check_ccn_compliance
#   [DDA/Docs — par univers]         get_pieces_justificatives_<univers>, export_devis
#   [API/Tech — par univers]         get_api_tarification_schema_<univers>
# ---------------------------------------------------------------------------


class CheckLemoineInput(BaseModel):
    loan_type: LoanType = Field(description="Type of loan")
    loan_amount: int = Field(description="Loan capital in euros", ge=10_000, le=2_000_000)
    borrower_age: int = Field(description="Borrower age at subscription", ge=18, le=75)
    loan_duration_years: int = Field(description="Loan duration in years", ge=1, le=30)

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_check_lemoine_eligibility",
    description=(
        "[Domaine: Emprunteur] "
        "Vérifie si un prêt est éligible à la Loi Lemoine (2022), qui supprime le questionnaire médical. "
        "Conditions Lemoine : usage résidentiel principal ou mixte, capital ≤ 200 000 €, "
        "âge de l'emprunteur à la fin du prêt < 60 ans. "
        "Prêts professionnels, locatifs purs et prêts à la consommation sont exclus. "
        "Utiliser avant toute tarification emprunteur pour orienter vers les bonnes gammes."
    ),
)
async def check_lemoine_eligibility(params: CheckLemoineInput) -> str:
    eligible = (
        params.loan_type == LoanType.IMMOBILIER
        and params.loan_amount <= 200_000
        and (params.borrower_age + params.loan_duration_years) < 60
    )
    reasons: list[str] = []
    if params.loan_type != LoanType.IMMOBILIER:
        reasons.append(f"Loan type '{params.loan_type}' is excluded from Lemoine (only residential)")
    if params.loan_amount > 200_000:
        reasons.append(f"Capital {params.loan_amount:,} € exceeds the 200 000 € Lemoine threshold")
    end_age = params.borrower_age + params.loan_duration_years
    if end_age >= 60:
        reasons.append(f"Borrower age at end of loan ({end_age}) is ≥ 60")

    return (
        f"eligible: {str(eligible).lower()}\n"
        f"end_age: {end_age}\n"
        f"medical_questionnaire_required: {str(not eligible).lower()}\n"
        f"reasons: {'; '.join(reasons) if reasons else 'All Lemoine conditions met'}"
    )


# ---------------------------------------------------------------------------
# Shared tarification helpers
# ---------------------------------------------------------------------------

_RISK_FACTORS = {RiskLevel.STANDARD: 1.0, RiskLevel.AGGREVE: 1.35, RiskLevel.TRES_AGGREVE: 1.75}


def _age_factor(age: int) -> float:
    return 1.0 + max(0, (age - 35) * 0.015)


def _risk_factor(risk_level: RiskLevel) -> float:
    return _RISK_FACTORS.get(risk_level, 1.0)


# ---------------------------------------------------------------------------
# TARIFICATION — Emprunteur  (système jRensure)
# ---------------------------------------------------------------------------

class TarifEmprunteurInput(BaseModel):
    borrower_age: int = Field(description="Borrower age at subscription", ge=18, le=75)
    loan_amount: int = Field(description="Loan capital in euros", ge=10_000, le=2_000_000)
    loan_duration_years: int = Field(description="Loan duration in years", ge=1, le=30)
    coverage_formula: CoverageFormula = Field(CoverageFormula.DC_PTIA_IPT, description="Coverage formula")
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Medical/profession risk level")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif_emprunteur",
    description=(
        "[Domaine: Emprunteur — système jRensure] "
        "Calcule la prime indicative d'assurance emprunteur pour un profil donné. "
        "Retourne le taux annuel en %, la cotisation mensuelle et les formules disponibles. "
        "Pour une comparaison multi-offres jRensure, utiliser rikees_compare_offres. "
        "Tarifs indicatifs non contractuels — à utiliser pour l'orientation et le conseil."
    ),
)
async def compute_tarif_emprunteur(params: TarifEmprunteurInput) -> str:
    base = 0.0015
    af = _age_factor(params.borrower_age)
    rf = _risk_factor(params.risk_level)
    monthly = round(params.loan_amount * base * af * rf / 12, 2)
    annual_rate_pct = round(base * af * rf * 100, 4)
    return (
        f"universe: emprunteur\n"
        f"annual_rate_pct: {annual_rate_pct}\n"
        f"monthly_premium_eur: {monthly}\n"
        f"risk_loading_pct: {round((rf - 1) * 100, 1)}\n"
        f"available_formulas: DC_PTIA | DC_PTIA_IPT | DC_PTIA_IPT_IPP"
    )


# ---------------------------------------------------------------------------
# TARIFICATION — Santé individuelle  (système Néoliane / Santiane)
# ---------------------------------------------------------------------------

class TarifSanteInput(BaseModel):
    subscriber_age: int = Field(description="Subscriber age", ge=18, le=85)
    beneficiary_count: int = Field(1, description="Number of beneficiaries covered", ge=1, le=10)
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Health risk level")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif_sante",
    description=(
        "[Domaine: Santé individuelle — système Néoliane / Santiane] "
        "Calcule la prime mensuelle indicative de complémentaire santé individuelle. "
        "Retourne la cotisation mensuelle, annuelle, le chargement risque et le nombre de bénéficiaires couverts. "
        "Tarifs indicatifs non contractuels — à utiliser pour l'orientation et le conseil."
    ),
)
async def compute_tarif_sante(params: TarifSanteInput) -> str:
    base = 80.0
    af = _age_factor(params.subscriber_age)
    rf = _risk_factor(params.risk_level)
    bf = 1.0 + (params.beneficiary_count - 1) * 0.65
    monthly = round(base * af * rf * bf, 2)
    return (
        f"universe: sante\n"
        f"monthly_premium_eur: {monthly}\n"
        f"annual_premium_eur: {round(monthly * 12, 2)}\n"
        f"risk_loading_pct: {round((rf - 1) * 100, 1)}\n"
        f"beneficiaries_covered: {params.beneficiary_count}"
    )


# ---------------------------------------------------------------------------
# TARIFICATION — Santé collective  (système GestiAssur Collectif)
# ---------------------------------------------------------------------------

class TarifSanteCollectiveInput(BaseModel):
    subscriber_age: int = Field(description="Average employee age (used for base rate)", ge=18, le=70)
    beneficiary_count: int = Field(1, description="Number of employees covered", ge=1, le=500)
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Risk level for the group")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif_sante_collective",
    description=(
        "[Domaine: Santé collective — système GestiAssur Collectif] "
        "Calcule la prime mensuelle indicative de complémentaire santé collective pour un groupe d'employés. "
        "Retourne la cotisation mensuelle totale, annuelle, et le chargement risque. "
        "Tarifs indicatifs non contractuels — à finaliser lors du devis formel pour l'entreprise."
    ),
)
async def compute_tarif_sante_collective(params: TarifSanteCollectiveInput) -> str:
    base = 55.0
    af = _age_factor(params.subscriber_age)
    rf = _risk_factor(params.risk_level)
    bf = 1.0 + (params.beneficiary_count - 1) * 0.65
    monthly = round(base * af * rf * bf, 2)
    return (
        f"universe: sante_collective\n"
        f"monthly_premium_eur: {monthly}\n"
        f"annual_premium_eur: {round(monthly * 12, 2)}\n"
        f"risk_loading_pct: {round((rf - 1) * 100, 1)}\n"
        f"beneficiaries_covered: {params.beneficiary_count}"
    )


# ---------------------------------------------------------------------------
# TARIFICATION — Prévoyance individuelle  (système Prévoyance TNS)
# ---------------------------------------------------------------------------

class TarifPrevoyanceInput(BaseModel):
    subscriber_age: int = Field(description="Subscriber age", ge=18, le=70)
    beneficiary_count: int = Field(1, description="Number of beneficiaries", ge=1, le=10)
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Medical/profession risk level")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif_prevoyance",
    description=(
        "[Domaine: Prévoyance individuelle — système Prévoyance TNS] "
        "Calcule la prime mensuelle indicative pour un contrat prévoyance individuelle (décès, invalidité, incapacité). "
        "Retourne la cotisation mensuelle, annuelle et le chargement risque. "
        "Tarifs indicatifs non contractuels — à utiliser pour l'orientation et le conseil."
    ),
)
async def compute_tarif_prevoyance(params: TarifPrevoyanceInput) -> str:
    base = 60.0
    af = _age_factor(params.subscriber_age)
    rf = _risk_factor(params.risk_level)
    bf = 1.0 + (params.beneficiary_count - 1) * 0.65
    monthly = round(base * af * rf * bf, 2)
    return (
        f"universe: prevoyance\n"
        f"monthly_premium_eur: {monthly}\n"
        f"annual_premium_eur: {round(monthly * 12, 2)}\n"
        f"risk_loading_pct: {round((rf - 1) * 100, 1)}\n"
        f"beneficiaries_covered: {params.beneficiary_count}"
    )


# ---------------------------------------------------------------------------
# TARIFICATION — GAV  (système AccidentVie)
# ---------------------------------------------------------------------------

class TarifGavInput(BaseModel):
    subscriber_age: int = Field(description="Subscriber age", ge=18, le=75)
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Profession/activity risk level")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif_gav",
    description=(
        "[Domaine: GAV (Garantie des Accidents de la Vie) — système AccidentVie] "
        "Calcule la prime mensuelle indicative pour un contrat GAV. "
        "Retourne la cotisation mensuelle, annuelle et le chargement risque lié au niveau de risque professionnel/activité. "
        "Tarifs indicatifs non contractuels — à utiliser pour l'orientation et le conseil."
    ),
)
async def compute_tarif_gav(params: TarifGavInput) -> str:
    base = 12.0
    af = _age_factor(params.subscriber_age)
    rf = _risk_factor(params.risk_level)
    monthly = round(base * af * rf, 2)
    return (
        f"universe: gav\n"
        f"monthly_premium_eur: {monthly}\n"
        f"annual_premium_eur: {round(monthly * 12, 2)}\n"
        f"risk_loading_pct: {round((rf - 1) * 100, 1)}"
    )


# ---------------------------------------------------------------------------
# TARIFICATION — Dommages  (système IARD Pro)
# ---------------------------------------------------------------------------

class TarifDommagesInput(BaseModel):
    subscriber_age: int = Field(description="Subscriber/policyholder age", ge=18, le=85)
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Risk level")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif_dommages",
    description=(
        "[Domaine: Dommages — système IARD Pro] "
        "Calcule la prime mensuelle indicative pour un contrat dommages. "
        "Retourne la cotisation mensuelle, annuelle et le chargement risque. "
        "Tarifs indicatifs non contractuels — à utiliser pour l'orientation et le conseil."
    ),
)
async def compute_tarif_dommages(params: TarifDommagesInput) -> str:
    base = 45.0
    af = _age_factor(params.subscriber_age)
    rf = _risk_factor(params.risk_level)
    monthly = round(base * af * rf, 2)
    return (
        f"universe: dommages\n"
        f"monthly_premium_eur: {monthly}\n"
        f"annual_premium_eur: {round(monthly * 12, 2)}\n"
        f"risk_loading_pct: {round((rf - 1) * 100, 1)}"
    )


# ---------------------------------------------------------------------------
# TARIFICATION — Obsèques  (système ObsèquesFrance)
# ---------------------------------------------------------------------------

class TarifObsequesInput(BaseModel):
    subscriber_age: int = Field(description="Subscriber age", ge=18, le=85)
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Health risk level")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif_obseques",
    description=(
        "[Domaine: Obsèques — système ObsèquesFrance] "
        "Calcule la prime mensuelle indicative pour un contrat obsèques individuel. "
        "Retourne la cotisation mensuelle, annuelle et le chargement risque. "
        "Tarifs indicatifs non contractuels — à utiliser pour l'orientation et le conseil."
    ),
)
async def compute_tarif_obseques(params: TarifObsequesInput) -> str:
    base = 25.0
    af = _age_factor(params.subscriber_age)
    rf = _risk_factor(params.risk_level)
    monthly = round(base * af * rf, 2)
    return (
        f"universe: obseques\n"
        f"monthly_premium_eur: {monthly}\n"
        f"annual_premium_eur: {round(monthly * 12, 2)}\n"
        f"risk_loading_pct: {round((rf - 1) * 100, 1)}"
    )


# ---------------------------------------------------------------------------
# TARIFICATION — Santé internationale  (système GlobalCare)
# ---------------------------------------------------------------------------

class TarifSanteIntlInput(BaseModel):
    subscriber_age: int = Field(description="Subscriber age", ge=18, le=75)
    beneficiary_count: int = Field(1, description="Number of beneficiaries covered", ge=1, le=10)
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Health risk level")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif_sante_internationale",
    description=(
        "[Domaine: Santé internationale — système GlobalCare] "
        "Calcule la prime mensuelle indicative pour une complémentaire santé internationale (expatriés, détachés). "
        "Retourne la cotisation mensuelle, annuelle, le chargement risque et le nombre de bénéficiaires couverts. "
        "Tarifs indicatifs non contractuels — à utiliser pour l'orientation et le conseil."
    ),
)
async def compute_tarif_sante_internationale(params: TarifSanteIntlInput) -> str:
    base = 90.0
    af = _age_factor(params.subscriber_age)
    rf = _risk_factor(params.risk_level)
    bf = 1.0 + (params.beneficiary_count - 1) * 0.65
    monthly = round(base * af * rf * bf, 2)
    return (
        f"universe: sante_internationale\n"
        f"monthly_premium_eur: {monthly}\n"
        f"annual_premium_eur: {round(monthly * 12, 2)}\n"
        f"risk_loading_pct: {round((rf - 1) * 100, 1)}\n"
        f"beneficiaries_covered: {params.beneficiary_count}"
    )


class CompareOffresInput(BaseModel):
    borrower_age: int = Field(description="Borrower age", ge=18, le=90)
    loan_amount: Optional[int] = Field(None, description="Loan amount in euros")
    loan_duration_years: Optional[int] = Field(None, description="Loan duration in years")
    loan_type: Optional[LoanType] = Field(None, description="Loan type")
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Risk level")
    lemoine_eligible: Optional[bool] = Field(None, description="Restrict to Lemoine-compatible offers if True")

    model_config = {"use_enum_values": True}


_EMPRUNTEUR_OFFERS = [
    {"code": "eclipse_pro", "name": "Éclipse Pro", "lemoine": True, "monthly": None, "formula": "DC_PTIA_IPT_IPP"},
    {"code": "serenite_immo", "name": "Sérénité Immo", "lemoine": True, "monthly": None, "formula": "DC_PTIA_IPT"},
    {"code": "eclipse_aggreve", "name": "Éclipse Aggravé", "lemoine": False, "monthly": None, "formula": "DC_PTIA_IPT"},
    {"code": "serenite_patrimoine", "name": "Sérénité Patrimoine", "lemoine": False, "monthly": None, "formula": "DC_PTIA_IPT_IPP"},
    {"code": "eclipse_dirigeant", "name": "Éclipse Dirigeant", "lemoine": False, "monthly": None, "formula": "DC_PTIA_IPT_IPP"},
]


@mcp.tool(
    name="rikees_compare_offres",
    description=(
        "[Domaine: Emprunteur — comparateur multi-offres jRensure] "
        "Lance une comparaison multi-offres via jRensure pour l'univers emprunteur. "
        "Retourne le tableau comparatif des offres disponibles classées par cotisation mensuelle. "
        "Permet de filtrer par éligibilité Lemoine, niveau de risque médical/professionnel. "
        "Pour un tarif indicatif emprunteur sur une seule offre, utiliser rikees_compute_tarif_emprunteur. "
        "Pour les autres univers, utiliser le tool rikees_compute_tarif_<univers> correspondant."
    ),
)
async def compare_offres(params: CompareOffresInput) -> str:
    af = _age_factor(params.borrower_age)
    rf = _risk_factor(params.risk_level)
    base_amount = params.loan_amount or 200_000

    offers = []
    for o in _EMPRUNTEUR_OFFERS:
        if params.lemoine_eligible is True and not o["lemoine"]:
            continue
        if params.risk_level in (RiskLevel.AGGREVE, RiskLevel.TRES_AGGREVE) and o["lemoine"]:
            continue
        monthly = round(base_amount * 0.0015 * af * rf / 12 * (0.9 if o["lemoine"] else 1.0), 2)
        offers.append(f"  - {o['name']} ({o['code']}): {monthly} €/mois | formule {o['formula']} | lemoine: {o['lemoine']}")

    lines = [f"universe: emprunteur", f"borrower_age: {params.borrower_age}", f"offers ({len(offers)}):"] + offers
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PIÈCES JUSTIFICATIVES — par univers / système documentaire
# ---------------------------------------------------------------------------

class PiecesEmprunteurInput(BaseModel):
    product_code: Optional[str] = Field(None, description="Specific product code (e.g. 'eclipse_pro')")
    lemoine_eligible: bool = Field(False, description="Whether Lemoine applies (removes medical questionnaire)")


@mcp.tool(
    name="rikees_get_pieces_justificatives_emprunteur",
    description=(
        "[Domaine: DDA / Documentation — Emprunteur] "
        "Retourne la liste des pièces justificatives requises pour un dossier assurance emprunteur. "
        "Si lemoine_eligible=True, le questionnaire médical est supprimé des exigences. "
        "À utiliser avant la soumission d'un dossier emprunteur pour anticiper les documents à collecter."
    ),
)
async def get_pieces_justificatives_emprunteur(params: PiecesEmprunteurInput) -> str:
    pieces = [
        "Pièce d'identité en cours de validité (CNI recto-verso ou passeport)",
        "Justificatif de domicile < 3 mois",
        "Tableau d'amortissement signé par la banque prêteuse",
        "Bulletins de salaire des 3 derniers mois (salarié) OU 2 derniers avis d'imposition (TNS)",
        "[si hors-Lemoine] Questionnaire de santé complet",
        "[si capital > 300 000 €] Rapport médical et examens complémentaires",
    ]
    if params.lemoine_eligible:
        pieces = [p for p in pieces if "questionnaire" not in p.lower() and "médical" not in p.lower()]
        pieces.append("✓ Lemoine applicable — questionnaire médical supprimé")
    lines = ["universe: emprunteur", f"product_code: {params.product_code or 'all'}", "pieces_requises:"]
    lines += [f"  - {p}" for p in pieces]
    return "\n".join(lines)


class PiecesProductCodeInput(BaseModel):
    product_code: Optional[str] = Field(None, description="Specific product code")


@mcp.tool(
    name="rikees_get_pieces_justificatives_sante",
    description=(
        "[Domaine: DDA / Documentation — Santé individuelle] "
        "Retourne la liste des pièces justificatives requises pour un dossier complémentaire santé individuelle. "
        "À utiliser avant la soumission d'un dossier santé pour anticiper les documents à collecter."
    ),
)
async def get_pieces_justificatives_sante(params: PiecesProductCodeInput) -> str:
    pieces = [
        "Pièce d'identité",
        "Attestation de sécurité sociale",
        "RIB pour prélèvement",
    ]
    lines = ["universe: sante", f"product_code: {params.product_code or 'all'}", "pieces_requises:"]
    lines += [f"  - {p}" for p in pieces]
    return "\n".join(lines)


@mcp.tool(
    name="rikees_get_pieces_justificatives_prevoyance",
    description=(
        "[Domaine: DDA / Documentation — Prévoyance individuelle] "
        "Retourne la liste des pièces justificatives requises pour un dossier prévoyance individuelle (TNS/Madelin). "
        "À utiliser avant la soumission d'un dossier prévoyance pour anticiper les documents à collecter."
    ),
)
async def get_pieces_justificatives_prevoyance(params: PiecesProductCodeInput) -> str:
    pieces = [
        "Pièce d'identité",
        "Justificatif de revenus TNS (avis d'imposition N-1 ou attestation URSSAF)",
        "Extrait Kbis ou attestation d'activité professionnelle",
        "Questionnaire de santé (si garanties IPT/PTIA incluses)",
    ]
    lines = ["universe: prevoyance", f"product_code: {params.product_code or 'all'}", "pieces_requises:"]
    lines += [f"  - {p}" for p in pieces]
    return "\n".join(lines)


@mcp.tool(
    name="rikees_get_pieces_justificatives_sante_collective",
    description=(
        "[Domaine: DDA / Documentation — Santé collective] "
        "Retourne la liste des pièces justificatives requises pour un dossier santé collective entreprise. "
        "À utiliser avant la soumission d'un dossier santé collective pour anticiper les documents à collecter."
    ),
)
async def get_pieces_justificatives_sante_collective(params: PiecesProductCodeInput) -> str:
    pieces = [
        "Accord collectif ou Décision Unilatérale de l'Employeur (DUE)",
        "Liste nominative du personnel (modèle Excel fourni par l'assureur)",
        "SIRET de l'entreprise",
        "Attestations de non-couverture pour les salariés dispensés d'adhésion",
    ]
    lines = ["universe: sante_collective", f"product_code: {params.product_code or 'all'}", "pieces_requises:"]
    lines += [f"  - {p}" for p in pieces]
    return "\n".join(lines)


@mcp.tool(
    name="rikees_get_pieces_justificatives_gav",
    description=(
        "[Domaine: DDA / Documentation — GAV] "
        "Retourne la liste des pièces justificatives requises pour un dossier GAV (Garantie des Accidents de la Vie). "
        "À utiliser avant la soumission d'un dossier GAV pour anticiper les documents à collecter."
    ),
)
async def get_pieces_justificatives_gav(params: PiecesProductCodeInput) -> str:
    pieces = [
        "Pièce d'identité",
        "RIB",
    ]
    lines = ["universe: gav", f"product_code: {params.product_code or 'all'}", "pieces_requises:"]
    lines += [f"  - {p}" for p in pieces]
    return "\n".join(lines)


class ExportDevisInput(BaseModel):
    dossier_id: str = Field(description="Dossier identifier returned after tarification")
    document_types: list[str] = Field(
        default=["devis", "ipid", "fiche_conseil"],
        description="Document types to generate: devis, ipid, fiche_conseil, conditions_generales",
    )


@mcp.tool(
    name="rikees_export_devis",
    description=(
        "[Domaine: DDA / Documentation — tous univers] "
        "Génère et retourne les URLs de téléchargement des documents de devis conformes DDA. "
        "Produit : devis (PDF), IPID (document d'information standardisé), fiche_conseil (note de conseil), "
        "et optionnellement les conditions générales. "
        "Obligations DDA : l'IPID et la fiche conseil doivent être remis au client avec accusé de réception. "
        "Les documents expirent après 30 jours."
    ),
)
async def export_devis(params: ExportDevisInput) -> str:
    base_url = "https://portail.rikees-sol.fr/documents"
    expiry = (date.today() + timedelta(days=30)).isoformat()
    docs = []
    for doc_type in params.document_types:
        docs.append(f"  - {doc_type}: {base_url}/{params.dossier_id}/{doc_type}.pdf (expires: {expiry})")
    lines = [
        f"dossier_id: {params.dossier_id}",
        f"generated_at: {datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"documents ({len(docs)}):",
    ] + docs + [
        "note: DDA compliance — IPID and fiche_conseil must be delivered to client with proof of receipt.",
        "note: Devis valid for 30 days from generation.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SCHÉMAS API DE TARIFICATION — par univers / système
# ---------------------------------------------------------------------------


@mcp.tool(
    name="rikees_get_api_tarification_schema_emprunteur",
    description=(
        "[Domaine: API / Technique — Emprunteur / système jRensure] "
        "Retourne le schéma complet de l'API de tarification emprunteur : "
        "endpoint, paramètres d'entrée, types, contraintes, codes d'erreur, rate limits et SLA. "
        "À utiliser pour les intégrations techniques jRensure, le débogage d'erreurs API, "
        "ou pour comprendre les limites de la génération automatisée de devis emprunteur."
    ),
)
async def get_api_tarification_schema_emprunteur() -> str:
    return """\
endpoint: POST /v1/tarification/emprunteur
authentication: Bearer token (header: Authorization)
rate_limit: 60 requests/minute, 500 requests/day (standard plan)
sla: P95 < 2s, P99 < 5s

input_schema:
  loan_type: string — enum: immobilier | professionnel | consommation | locatif
  loan_amount: integer — euros, min: 10000, max: 2000000
  loan_duration_months: integer — min: 12, max: 360
  borrower_age: integer — min: 18, max: 75
  loan_end_age: integer — max: 90 (auto-computed if omitted)
  profession_risk_level: string — enum: standard | aggravé | très_aggravé
  medical_risk: boolean — default: false
  co_borrower: boolean — default: false
  coverage_formula: string — enum: DC_PTIA | DC_PTIA_IPT | DC_PTIA_IPT_IPP
  quota_borrower_pct: integer — min: 50, max: 100
  lemoine_eligible: boolean — auto-computed if omitted
  gamme_senior: boolean — optional, enables senior-range products

output_schema:
  tarif_annuel_pct: float — annual rate as percentage
  cotisation_mensuelle: float — monthly premium in euros
  offres_disponibles: array of { code, name, monthly_eur, formula, lemoine }
  lemoine_eligible: boolean

error_codes:
  4001: MISSING_REQUIRED_PARAMETER
  4010: LOAN_AMOUNT_OUT_OF_RANGE
  4015: UNKNOWN_PROFESSION_RISK_LEVEL
  4022: LOAN_END_AGE_EXCEEDED — borrower_age + duration/12 > 90; fix: reduce duration or set gamme_senior=true
  5001: ENGINE_UNAVAILABLE — retry after 30s

manual_review_required_if:
  - medical_risk: true
  - profession_risk_level: très_aggravé
  - loan_amount > 500000
"""


@mcp.tool(
    name="rikees_get_api_tarification_schema_sante",
    description=(
        "[Domaine: API / Technique — Santé individuelle / système Néoliane] "
        "Retourne le schéma de l'API de tarification santé individuelle : endpoint, paramètres, contraintes et SLA. "
        "À utiliser pour les intégrations techniques avec le système de tarification santé individuelle."
    ),
)
async def get_api_tarification_schema_sante() -> str:
    return (
        "endpoint: POST /v1/tarification/sante\n"
        "authentication: Bearer token (header: Authorization)\n"
        "rate_limit: 60 requests/minute\n"
        "core_parameters: subscriber_age, beneficiary_count, coverage_level\n"
        "note: Full schema available in the developer documentation portal."
    )


@mcp.tool(
    name="rikees_get_api_tarification_schema_prevoyance",
    description=(
        "[Domaine: API / Technique — Prévoyance individuelle / système Prévoyance TNS] "
        "Retourne le schéma de l'API de tarification prévoyance individuelle : endpoint, paramètres, contraintes et SLA. "
        "À utiliser pour les intégrations techniques avec le système de tarification prévoyance."
    ),
)
async def get_api_tarification_schema_prevoyance() -> str:
    return (
        "endpoint: POST /v1/tarification/prevoyance\n"
        "authentication: Bearer token (header: Authorization)\n"
        "rate_limit: 60 requests/minute\n"
        "core_parameters: subscriber_age, beneficiary_count, coverage_level\n"
        "note: Full schema available in the developer documentation portal."
    )


@mcp.tool(
    name="rikees_get_api_tarification_schema_sante_collective",
    description=(
        "[Domaine: API / Technique — Santé collective / système GestiAssur Collectif] "
        "Retourne le schéma de l'API de tarification santé collective : endpoint, paramètres, contraintes et SLA. "
        "À utiliser pour les intégrations techniques avec le système de tarification santé collective."
    ),
)
async def get_api_tarification_schema_sante_collective() -> str:
    return (
        "endpoint: POST /v1/tarification/sante_collective\n"
        "authentication: Bearer token (header: Authorization)\n"
        "rate_limit: 60 requests/minute\n"
        "core_parameters: subscriber_age, beneficiary_count, coverage_level, ccn_code\n"
        "note: Full schema available in the developer documentation portal."
    )


@mcp.tool(
    name="rikees_get_api_tarification_schema_gav",
    description=(
        "[Domaine: API / Technique — GAV / système AccidentVie] "
        "Retourne le schéma de l'API de tarification GAV : endpoint, paramètres, contraintes et SLA. "
        "À utiliser pour les intégrations techniques avec le système de tarification GAV."
    ),
)
async def get_api_tarification_schema_gav() -> str:
    return (
        "endpoint: POST /v1/tarification/gav\n"
        "authentication: Bearer token (header: Authorization)\n"
        "rate_limit: 60 requests/minute\n"
        "core_parameters: subscriber_age, risk_level\n"
        "note: Full schema available in the developer documentation portal."
    )


@mcp.tool(
    name="rikees_get_api_tarification_schema_dommages",
    description=(
        "[Domaine: API / Technique — Dommages / système IARD Pro] "
        "Retourne le schéma de l'API de tarification dommages : endpoint, paramètres, contraintes et SLA. "
        "À utiliser pour les intégrations techniques avec le système de tarification dommages."
    ),
)
async def get_api_tarification_schema_dommages() -> str:
    return (
        "endpoint: POST /v1/tarification/dommages\n"
        "authentication: Bearer token (header: Authorization)\n"
        "rate_limit: 60 requests/minute\n"
        "core_parameters: subscriber_age, risk_level, property_type\n"
        "note: Full schema available in the developer documentation portal."
    )


@mcp.tool(
    name="rikees_get_api_tarification_schema_obseques",
    description=(
        "[Domaine: API / Technique — Obsèques / système ObsèquesFrance] "
        "Retourne le schéma de l'API de tarification obsèques : endpoint, paramètres, contraintes et SLA. "
        "À utiliser pour les intégrations techniques avec le système de tarification obsèques."
    ),
)
async def get_api_tarification_schema_obseques() -> str:
    return (
        "endpoint: POST /v1/tarification/obseques\n"
        "authentication: Bearer token (header: Authorization)\n"
        "rate_limit: 60 requests/minute\n"
        "core_parameters: subscriber_age, capital_obseques_eur\n"
        "note: Full schema available in the developer documentation portal."
    )


@mcp.tool(
    name="rikees_get_api_tarification_schema_sante_internationale",
    description=(
        "[Domaine: API / Technique — Santé internationale / système GlobalCare] "
        "Retourne le schéma de l'API de tarification santé internationale : endpoint, paramètres, contraintes et SLA. "
        "À utiliser pour les intégrations techniques avec le système GlobalCare pour expatriés et détachés."
    ),
)
async def get_api_tarification_schema_sante_internationale() -> str:
    return (
        "endpoint: POST /v1/tarification/sante_internationale\n"
        "authentication: Bearer token (header: Authorization)\n"
        "rate_limit: 60 requests/minute\n"
        "core_parameters: subscriber_age, beneficiary_count, destination_zone, coverage_level\n"
        "note: Full schema available in the developer documentation portal."
    )


class MadelinPlafondInput(BaseModel):
    annual_taxable_income: int = Field(description="Annual taxable professional income in euros", ge=0)
    contract_type: str = Field("prevoyance", description="Contract type: prevoyance | retraite | complementaire_sante")
    pass_year: int = Field(2024, description="PASS year (default 2024 = 46 368 €)")


@mcp.tool(
    name="rikees_get_madelin_plafonds",
    description=(
        "[Domaine: TNS / Prévoyance individuelle — artisans, commerçants, professions libérales] "
        "Calcule les plafonds de déductibilité Madelin pour un travailleur non-salarié (TNS) / professionnel indépendant. "
        "Retourne le plafond applicable et le détail du calcul pour prévoyance, retraite ou santé complémentaire Madelin. "
        "Utiliser systématiquement avant de proposer un contrat prévoyance ou retraite Madelin à un TNS."
    ),
)
async def get_madelin_plafonds(params: MadelinPlafondInput) -> str:
    pass_values = {2024: 46_368, 2025: 47_100, 2023: 43_992}
    pass_val = pass_values.get(params.pass_year, 46_368)

    if params.contract_type == "prevoyance":
        ceiling_a = round(0.0375 * params.annual_taxable_income + 0.07 * pass_val, 2)
        ceiling_min = round(0.07 * pass_val, 2)
        ceiling_max = round(0.03 * 8 * pass_val, 2)
        applicable = min(max(ceiling_a, ceiling_min), ceiling_max)
        return (
            f"contract_type: prévoyance Madelin\n"
            f"annual_taxable_income: {params.annual_taxable_income:,} €\n"
            f"pass_{params.pass_year}: {pass_val:,} €\n"
            f"formula_a: 3.75% × {params.annual_taxable_income:,} + 7% × {pass_val:,} = {ceiling_a:,.2f} €\n"
            f"minimum: 7% × PASS = {ceiling_min:,.2f} €\n"
            f"cap: 3% × 8×PASS = {ceiling_max:,.2f} €\n"
            f"applicable_ceiling_eur: {applicable:,.2f}\n"
            f"recommendation: Annual Madelin contributions must not exceed {applicable:,.2f} € to remain fully deductible."
        )
    elif params.contract_type == "retraite":
        ceiling = round(0.10 * params.annual_taxable_income + 0.15 * pass_val, 2)
        return (
            f"contract_type: retraite Madelin (Loi Madelin)\n"
            f"applicable_ceiling_eur: {ceiling:,.2f}\n"
            f"formula: 10% × revenu + 15% × PASS"
        )
    return f"contract_type: {params.contract_type}\nnote: Consult an accountant for this contract type's Madelin rules."


class CcnComplianceInput(BaseModel):
    ccn_code: str = Field(description="CCN identifier, e.g. 'metallurgie', 'btp', 'hcr', 'ani'")
    guarantee_levels: dict = Field(
        description=(
            "Guarantee levels to check as key-value pairs. "
            "Keys: ticket_moderateur_pct, forfait_hospitalier, dentaire_pct_br, optique_eur_year, "
            "patronale_pct, maintien_salaire_days"
        )
    )


_CCN_MINIMA: dict[str, dict] = {
    "metallurgie": {
        "ticket_moderateur_pct": 100,
        "forfait_hospitalier": True,
        "dentaire_pct_br": 125,
        "patronale_pct": 50,
    },
    "btp": {
        "ticket_moderateur_pct": 100,
        "forfait_hospitalier": True,
        "dentaire_pct_br": 150,
        "patronale_pct": 50,
        "maintien_salaire_days": 30,
    },
    "hcr": {
        "ticket_moderateur_pct": 100,
        "forfait_hospitalier": True,
        "dentaire_pct_br": 125,
        "patronale_pct": 50,
        "maintien_salaire_days": 30,
    },
    "ani": {
        "ticket_moderateur_pct": 100,
        "forfait_hospitalier": True,
        "dentaire_pct_br": 125,
        "patronale_pct": 50,
    },
}


@mcp.tool(
    name="rikees_check_ccn_compliance",
    description=(
        "[Domaine: Santé / Prévoyance collective — entreprises et CCN] "
        "Vérifie la conformité d'un ensemble de garanties collectives avec les exigences minimales "
        "d'une CCN (Convention Collective Nationale) et/ou du cadre ANI. "
        "CCN supportées : metallurgie, btp, hcr, ani (toutes branches). "
        "Retourne un statut vert/orange/rouge par critère et un verdict global. "
        "À utiliser pour tout devis santé ou prévoyance collective avant remise à une entreprise cliente."
    ),
)
async def check_ccn_compliance(params: CcnComplianceInput) -> str:
    minima = _CCN_MINIMA.get(params.ccn_code.lower(), {})
    if not minima:
        return f"ccn_code: {params.ccn_code}\nstatus: UNKNOWN — CCN not found in reference database. Verify the CCN code."

    results: list[str] = []
    overall_ok = True
    for key, min_val in minima.items():
        provided = params.guarantee_levels.get(key)
        if provided is None:
            results.append(f"  {key}: ⚠️ ORANGE — not specified (minimum required: {min_val})")
            overall_ok = False
        elif isinstance(min_val, bool):
            ok = bool(provided) == min_val
            results.append(f"  {key}: {'✅ GREEN' if ok else '🔴 RED — required but not provided'}")
            if not ok:
                overall_ok = False
        elif isinstance(min_val, (int, float)):
            ok = float(provided) >= float(min_val)
            results.append(
                f"  {key}: {'✅ GREEN' if ok else '🔴 RED'} — "
                f"provided {provided} {'≥' if ok else '<'} minimum {min_val}"
            )
            if not ok:
                overall_ok = False

    verdict = "✅ COMPLIANT" if overall_ok else "🔴 NON-COMPLIANT — see red/orange items above"
    lines = [f"ccn_code: {params.ccn_code}", f"overall_verdict: {verdict}", "criteria:"] + results
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ── PORTEFEUILLE / SUIVI TOOLS ───────────────────────────────────────────────#
# Domains covered:
#   [Suivi Dossiers]    get_dossier_status  — statut en temps réel d'un dossier soumis
#   [Portefeuille]      get_portefeuille, get_echeances_alertes  — vue contrats actifs
#   [Production]        get_tableau_de_bord  — KPIs et tableau de bord courtier
#   [Gestion Contrats]  get_documents_contractuels, modifier_contrat  — documents et avenants
#   [API/Tech]          get_api_statut_schema  — schéma endpoint statut (usage technique)# ---------------------------------------------------------------------------


class GetDossierStatusInput(BaseModel):
    dossier_id: str = Field(description="Dossier reference identifier")


_STUB_DOSSIERS: dict[str, dict] = {
    "JD-2026-0425": {
        "status": "pending_documents",
        "client": "Jean Dupont",
        "universe": "emprunteur",
        "submitted_at": "2026-04-25T14:32:00Z",
        "last_updated_at": "2026-04-26T09:15:00Z",
        "pending_actions": [
            {"type": "document", "description": "Bulletin de salaire mars 2026 manquant", "deadline": "2026-05-03"},
            {"type": "document", "description": "Tableau d'amortissement non signé", "deadline": "2026-05-03"},
        ],
        "policy_number": None,
    },
    "BC-0412": {
        "status": "pending_documents",
        "client": "Bertrand C.",
        "universe": "emprunteur",
        "submitted_at": "2026-04-18T10:00:00Z",
        "last_updated_at": "2026-04-18T10:00:00Z",
        "pending_actions": [
            {"type": "document", "description": "Questionnaire médical non retourné", "deadline": "2026-04-30"},
        ],
        "policy_number": None,
    },
    "LP-0418": {
        "status": "pending_documents",
        "client": "Laurent P.",
        "universe": "emprunteur",
        "submitted_at": "2026-04-18T11:00:00Z",
        "last_updated_at": "2026-04-18T11:00:00Z",
        "pending_actions": [
            {"type": "document", "description": "Offre de prêt définitive (version signée)", "deadline": "2026-05-01"},
        ],
        "policy_number": None,
    },
    "SM-2026-0426": {
        "status": "accepted",
        "client": "Sophie Martin",
        "universe": "emprunteur",
        "submitted_at": "2026-04-20T09:00:00Z",
        "last_updated_at": "2026-04-26T08:00:00Z",
        "pending_actions": [],
        "policy_number": "EP-2026-0089234",
    },
    # Referenced in MAT-SUV-03 dashboard (tableau de bord)
    "KM-0421": {
        "status": "pending_documents",
        "client": "Karim M.",
        "universe": "emprunteur",
        "submitted_at": "2026-04-22T09:00:00Z",
        "last_updated_at": "2026-04-22T09:00:00Z",
        "pending_actions": [
            {"type": "document", "description": "Bulletin de salaire manquant", "deadline": "2026-04-30"},
        ],
        "policy_number": None,
    },
    # Referenced in NAT-SUV-03 multi-turn (santé collective PME BTP)
    "SC-BTP-2025-0040": {
        "status": "under_review",
        "client": "PME Dubois BTP (40 sal.)",
        "universe": "sante_collective",
        "submitted_at": "2026-04-10T08:00:00Z",
        "last_updated_at": "2026-04-25T14:00:00Z",
        "pending_actions": [],
        "policy_number": None,
    },
}


@mcp.tool(
    name="rikees_get_dossier_status",
    description=(
        "[Domaine: Suivi Dossiers — tous univers] "
        "Retourne le statut actuel d'un dossier soumis : code statut, libellé français, "
        "horodatage de dernière mise à jour, actions en attente avec leurs deadlines, "
        "et numéro de police si le dossier est accepté. "
        "Utiliser avec la référence du dossier (ex: JD-2026-0425) pour connaître l'état d'avancement. "
        "Statuts possibles : submitted, pending_documents, under_review, accepted, refused, cancelled."
    ),
)
async def get_dossier_status(params: GetDossierStatusInput) -> str:
    dossier = _STUB_DOSSIERS.get(params.dossier_id)
    if not dossier:
        return (
            f"dossier_id: {params.dossier_id}\n"
            f"status: not_found\n"
            f"message: Dossier not found. Check the reference or use rikees_get_portefeuille to list active dossiers."
        )

    status_labels = {
        "submitted": "Soumis — En cours de réception",
        "pending_documents": "En attente de pièces complémentaires",
        "under_review": "En cours d'instruction",
        "accepted": "Accepté",
        "refused": "Refusé",
        "cancelled": "Annulé",
    }
    lines = [
        f"dossier_id: {params.dossier_id}",
        f"client: {dossier['client']}",
        f"universe: {dossier['universe']}",
        f"status: {dossier['status']}",
        f"status_label_fr: {status_labels.get(dossier['status'], dossier['status'])}",
        f"submitted_at: {dossier['submitted_at']}",
        f"last_updated_at: {dossier['last_updated_at']}",
        f"policy_number: {dossier['policy_number'] or 'N/A (not yet accepted)'}",
    ]
    if dossier["pending_actions"]:
        lines.append("pending_actions:")
        for a in dossier["pending_actions"]:
            lines.append(f"  - [{a['type']}] {a['description']} (deadline: {a['deadline']})")
    else:
        lines.append("pending_actions: none")
    return "\n".join(lines)


class GetPortefeuilleInput(BaseModel):
    universe: Optional[Universe] = Field(None, description="Filter by universe (omit for all)")
    status: Optional[DossierStatus] = Field(None, description="Filter by status (omit for all)")
    days_ahead: Optional[int] = Field(None, description="Filter contracts expiring within N days")

    model_config = {"use_enum_values": True}


_STUB_CONTRACTS = [
    {"id": "EP-2024-1138", "client": "Client Dirigeant", "universe": "emprunteur", "status": "active",
     "monthly_premium": 245.0, "next_expiry": "2026-06-01", "capital": 800_000},
    {"id": "PM-2023-0552", "client": "Isabelle Client", "universe": "prevoyance", "status": "active",
     "monthly_premium": 433.0, "next_expiry": "2027-01-01", "capital": None},
    {"id": "ST-2024-0891", "client": "Karim Client TNS", "universe": "sante", "status": "active",
     "monthly_premium": 245.0, "next_expiry": "2027-01-01", "capital": None},
    {"id": "SC-2025-0034", "client": "PME Gautier & Associés", "universe": "sante_collective", "status": "pending",
     "monthly_premium": None, "next_expiry": None, "capital": None},
    {"id": "GAV-2025-0210", "client": "Lebrun A.", "universe": "gav", "status": "active",
     "monthly_premium": 18.0, "next_expiry": "2026-05-15", "capital": None},
    {"id": "SAN-2025-0445", "client": "Martin F.", "universe": "sante", "status": "active",
     "monthly_premium": 95.0, "next_expiry": "2026-05-01", "capital": None},
    # Referenced in NAT-SUV-03 multi-turn (renouvellement annuel collectif CCN BTP)
    {"id": "SC-BTP-2025-0040", "client": "PME Dubois BTP (40 sal.)", "universe": "sante_collective",
     "status": "active", "monthly_premium": 3200.0, "next_expiry": "2026-05-31", "capital": None},
]


@mcp.tool(
    name="rikees_get_portefeuille",
    description=(
        "[Domaine: Portefeuille — tous univers] "
        "Retourne la vue portefeuille actif avec filtres optionnels par univers, statut, "
        "ou fenêtre d'échéance (N prochains jours). "
        "Liste les contrats avec : nom client, univers, statut, cotisation mensuelle, et date d'échéance. "
        "Utiliser pour une vue consolidée du portefeuille ou pour planifier des campagnes de renouvellement. "
        "Pour les alertes d'échéance précises avec recommandations d'action, utiliser rikees_get_echeances_alertes."
    ),
)
async def get_portefeuille(params: GetPortefeuilleInput) -> str:
    contracts = list(_STUB_CONTRACTS)
    if params.universe:
        contracts = [c for c in contracts if c["universe"] == params.universe]
    if params.status:
        contracts = [c for c in contracts if c["status"] == params.status]
    if params.days_ahead:
        cutoff = (date.today() + timedelta(days=params.days_ahead)).isoformat()
        contracts = [c for c in contracts if c.get("next_expiry") and c["next_expiry"] <= cutoff]

    if not contracts:
        return "portefeuille: no contracts match the given filters."

    lines = [f"portefeuille ({len(contracts)} contracts):"]
    for c in contracts:
        expiry_str = c.get("next_expiry") or "N/A"
        premium_str = f"{c['monthly_premium']} €/mois" if c["monthly_premium"] else "pending"
        lines.append(
            f"  - {c['id']} | {c['client']} | {c['universe']} | status: {c['status']} "
            f"| premium: {premium_str} | next_expiry: {expiry_str}"
        )
    return "\n".join(lines)


class GetEcheancesAlertesInput(BaseModel):
    days_ahead: int = Field(30, description="Number of days ahead to look for upcoming expirations", ge=1, le=365)
    universe: Optional[Universe] = Field(None, description="Filter by universe (omit for all)")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_get_echeances_alertes",
    description=(
        "[Domaine: Portefeuille / Alertes échéances — tous univers] "
        "Retourne les contrats arrivant à échéance dans la fenêtre spécifiée, triés par urgence. "
        "Inclut une recommandation d'action pour chaque contrat (renouvellement, résiliation Lemoine, etc.). "
        "Urgence : contrats échéant dans les 15 prochains jours sont signalés en ROUGE. "
        "Utiliser en début de semaine ou de mois pour identifier les priorités de renouvellement."
    ),
)
async def get_echeances_alertes(params: GetEcheancesAlertesInput) -> str:
    cutoff = (date.today() + timedelta(days=params.days_ahead)).isoformat()
    upcoming = [
        c for c in _STUB_CONTRACTS
        if c.get("next_expiry") and c["next_expiry"] <= cutoff
        and (params.universe is None or c["universe"] == params.universe)
    ]
    upcoming.sort(key=lambda c: c["next_expiry"])

    if not upcoming:
        return f"echeances: no contracts expiring within {params.days_ahead} days."

    lines = [f"echeances_alertes ({len(upcoming)} contracts, next {params.days_ahead} days):"]
    for c in upcoming:
        days_left = (date.fromisoformat(c["next_expiry"]) - date.today()).days
        urgency = "🔴 URGENT" if days_left <= 15 else "🟡 À planifier"
        action = "Lemoine opt-out possible" if c["universe"] == "emprunteur" else "Proposer renouvellement"
        lines.append(
            f"  {urgency} | {c['id']} | {c['client']} | {c['universe']} "
            f"| échéance: {c['next_expiry']} ({days_left}j) | action: {action}"
        )
    return "\n".join(lines)


class GetTableauDeBordInput(BaseModel):
    period: str = Field("current_month", description="Period: current_month | last_month | last_quarter | ytd")
    universe: Optional[Universe] = Field(None, description="Filter by universe")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_get_tableau_de_bord",
    description=(
        "[Domaine: Production / Tableau de bord — tous univers] "
        "Retourne les KPIs de production pour la période spécifiée : "
        "devis générés, dossiers soumis, taux de transformation, taux d'acceptation, "
        "chiffre d'affaires, commissions créditées / en attente, et liste des dossiers bloquants prioritaires. "
        "Périodes : mois en cours, mois précédent, trimestre, année à date. "
        "Utiliser pour les bilans d'activité ou identifier les dossiers à débloquer en priorité."
    ),
)
async def get_tableau_de_bord(params: GetTableauDeBordInput) -> str:
    universe_filter = f" ({params.universe})" if params.universe else " (tous univers)"
    period_labels = {
        "current_month": "Avril 2026",
        "last_month": "Mars 2026",
        "last_quarter": "T1 2026",
        "ytd": "YTD 2026",
    }
    label = period_labels.get(params.period, params.period)
    return (
        f"tableau_de_bord — {label}{universe_filter}\n"
        f"devis_generes: 47\n"
        f"dossiers_soumis: 31\n"
        f"taux_transformation_devis_soumission: 66%\n"
        f"dossiers_acceptes: 18\n"
        f"taux_acceptation: 58%\n"
        f"dossiers_refuses: 3\n"
        f"dossiers_en_attente_de_pieces: 7\n"
        f"dossiers_en_cours_instruction: 3\n"
        f"chiffre_affaires_brut_eur: 12450.00\n"
        f"commissions_creditees_eur: 8730.00\n"
        f"commissions_en_attente_eur: 1240.00\n"
        f"priorites: [{{'ref': 'BC-0412', 'days_blocked': 8, 'action': 'relancer questionnaire médical'}}, "
        f"{{'ref': 'LP-0418', 'days_blocked': 5, 'action': 'relancer offre de prêt'}}, "
        f"{{'ref': 'KM-0421', 'days_blocked': 4, 'action': 'relancer bulletin de salaire'}}]"
    )


class GetDocumentsContractuelsInput(BaseModel):
    contract_id: str = Field(description="Contract or dossier identifier (e.g. 'EP-2024-1138')")


@mcp.tool(
    name="rikees_get_documents_contractuels",
    description=(
        "[Domaine: Gestion Contrats — tous univers] "
        "Retourne les URLs de téléchargement des documents contractuels d'un contrat actif : "
        "conditions particulières, conditions générales, tableau des garanties, attestation d'assurance, IPID. "
        "Les URLs sont valables 7 jours. "
        "Utiliser pour préparer un rendez-vous client, remettre des documents, ou vérifier les garanties en vigueur."
    ),
)
async def get_documents_contractuels(params: GetDocumentsContractuelsInput) -> str:
    base_url = "https://portail.rikees-sol.fr/documents"
    expiry = (date.today() + timedelta(days=7)).isoformat()
    docs = [
        ("conditions_particulieres", "Conditions Particulières"),
        ("conditions_generales", "Conditions Générales"),
        ("tableau_garanties", "Tableau des Garanties"),
        ("attestation", "Attestation d'Assurance"),
        ("ipid", "IPID — Document d'Information sur le Produit"),
    ]
    lines = [
        f"contract_id: {params.contract_id}",
        f"url_expiry: {expiry}",
        "documents:",
    ]
    for key, label in docs:
        lines.append(f"  - {label}: {base_url}/{params.contract_id}/{key}.pdf")
    return "\n".join(lines)


class ModifierContratInput(BaseModel):
    contract_id: str = Field(description="Contract identifier to modify")
    modification_type: str = Field(
        description=(
            "Type of modification: "
            "adjunction_beneficiaire | suppression_beneficiaire | "
            "changement_garanties | changement_quotite | resiliation"
        )
    )
    effective_date: Optional[str] = Field(
        None, description="Requested effective date (ISO 8601). Defaults to next business day."
    )
    notes: Optional[str] = Field(None, description="Additional notes or context for the modification")


@mcp.tool(
    name="rikees_modifier_contrat",
    description=(
        "[Domaine: Gestion Contrats — tous univers] "
        "Initie une demande de modification sur un contrat actif. "
        "Modifications supportées : adjonction de bénéficiaire (naissance, mariage), "
        "suppression de bénéficiaire, changement de garanties, changement de quotité, résiliation. "
        "Pour la résiliation emprunteur Lemoine : immédiate, préavis 0 jour. "
        "Pour la résiliation hors-Lemoine : préavis 2 mois avant l'échéance annuelle. "
        "Retourne un ID de demande de modification et le délai de traitement estimé."
    ),
)
async def modifier_contrat(params: ModifierContratInput) -> str:
    processing_days = {
        "adjunction_beneficiaire": "5-10 jours ouvrés",
        "suppression_beneficiaire": "3-5 jours ouvrés",
        "changement_garanties": "10-15 jours ouvrés",
        "changement_quotite": "5-7 jours ouvrés",
        "resiliation": "0 jour (immédiat pour Lemoine) ou préavis 2 mois (hors-Lemoine)",
    }
    request_id = f"MOD-{params.contract_id}-{date.today().strftime('%Y%m%d')}"
    effective = params.effective_date or (date.today() + timedelta(days=1)).isoformat()
    processing = processing_days.get(params.modification_type, "5-10 jours ouvrés")

    return (
        f"modification_request_id: {request_id}\n"
        f"contract_id: {params.contract_id}\n"
        f"modification_type: {params.modification_type}\n"
        f"requested_effective_date: {effective}\n"
        f"estimated_processing: {processing}\n"
        f"status: submitted\n"
        f"notes: {params.notes or 'N/A'}\n"
        f"next_step: An avenant will be generated and sent for electronic signature once processed."
    )


class GetApiStatutSchemaInput(BaseModel):
    universe: Optional[Universe] = Field(None, description="Universe to scope the status API schema")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_get_api_statut_schema",
    description=(
        "[Domaine: API / Technique — usage courtiers digitaux et intégrations] "
        "Retourne le schéma de l'endpoint de statut des dossiers : méthode HTTP, URL, format de réponse, "
        "codes statut, SLA par étape, rate limits, et bonnes pratiques d'intégration (stratégie de polling, "
        "endpoint de relance, procédure d'escalade). "
        "À utiliser pour implémenter un système de suivi automatisé ou déboguer des problèmes d'intégration API."
    ),
)
async def get_api_statut_schema(params: GetApiStatutSchemaInput) -> str:
    return """\
endpoint: GET /v1/dossiers/{dossier_id}/status
authentication: Bearer token (header: Authorization)
rate_limit: 60 requests/minute per API token
availability: 24/7 — status updates by insurer during business hours (9h-18h weekdays)

response_schema:
  dossier_id: string
  status: enum — submitted | pending_documents | under_review | accepted | refused | cancelled
  status_label_fr: string
  last_updated_at: ISO 8601 datetime
  pending_actions: array of { type, description, deadline }
  policy_number: string | null  # populated when status = accepted
  refusal_reason: string | null # populated when status = refused

http_status_codes:
  200: OK
  404: Dossier not found
  401: Unauthorized (invalid token)
  429: Rate limit exceeded — retry after 60s

sla_by_status:
  submitted → pending_documents: same business day
  pending_documents → under_review: 24h after receipt of complete documents
  under_review → accepted|refused: 24-48h standard | 5-10 days if medical review required

polling_best_practices:
  - submitted: poll every 4h
  - pending_documents: poll every 2h
  - under_review: poll every 6h
  - terminal states (accepted|refused|cancelled): stop polling
  - use jitter ±10 min to avoid simultaneous bursts
  - store last_updated_at to detect changes efficiently

relance_endpoint: POST /v1/dossiers/{dossier_id}/relances
  - triggers automated email+SMS reminder to client for missing documents
  - limit: 1 relance per dossier per 24h

escalation:
  - threshold: >5 business days in pending_documents or under_review without update
  - channel: support@rikees-sol.fr or portail 'Support' → 'Escalade dossier'
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

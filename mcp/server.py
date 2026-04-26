"""
Rikees Sol MCP Stub Server

Bouchons (stubs) for Rikees Sol Espace Partenaire tools, covering:
  - Tarification / devis
  - Suivi des dossiers / portefeuille

All tools return deterministic stub data for benchmark evaluation.
No real API calls are made.
"""

from __future__ import annotations

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
        "Check whether a loan is eligible for Loi Lemoine (2022). "
        "Lemoine removes the medical questionnaire when: loan is for primary/mixed residential use, "
        "capital ≤ 200 000 €, and borrower age at end of loan < 60. "
        "Professional, investment-only and consumer loans are excluded."
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


class ComputeTarifInput(BaseModel):
    universe: Universe = Field(description="Product universe")
    borrower_age: int = Field(description="Borrower/subscriber age", ge=18, le=90)
    loan_amount: Optional[int] = Field(None, description="Loan amount in euros (emprunteur only)")
    loan_duration_years: Optional[int] = Field(None, description="Loan duration in years (emprunteur only)")
    coverage_formula: Optional[CoverageFormula] = Field(None, description="Coverage formula (emprunteur only)")
    risk_level: RiskLevel = Field(RiskLevel.STANDARD, description="Medical/profession risk level")
    beneficiary_count: int = Field(1, description="Number of beneficiaries (health/life)", ge=1, le=10)

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_compute_tarif",
    description=(
        "Compute an indicative insurance premium for the given universe and subscriber profile. "
        "Returns monthly and annual premium, risk loading, and available product codes. "
        "Stub returns deterministic indicative rates — not contractually binding."
    ),
)
async def compute_tarif(params: ComputeTarifInput) -> str:
    base_rates = {
        Universe.EMPRUNTEUR: 0.0015,
        Universe.SANTE: 80.0,
        Universe.SANTE_COLLECTIVE: 55.0,
        Universe.PREVOYANCE: 60.0,
        Universe.GAV: 12.0,
        Universe.DOMMAGES: 45.0,
        Universe.OBSEQUES: 25.0,
        Universe.SANTE_INTERNATIONALE: 90.0,
    }
    age_factor = 1.0 + max(0, (params.borrower_age - 35) * 0.015)
    risk_factors = {RiskLevel.STANDARD: 1.0, RiskLevel.AGGREVE: 1.35, RiskLevel.TRES_AGGREVE: 1.75}
    risk_factor = risk_factors.get(params.risk_level, 1.0)
    beneficiary_factor = 1.0 + (params.beneficiary_count - 1) * 0.65

    base = base_rates.get(params.universe, 50.0)

    if params.universe == Universe.EMPRUNTEUR and params.loan_amount and params.loan_duration_years:
        monthly = round(params.loan_amount * base * age_factor * risk_factor / 12, 2)
        annual_rate_pct = round(base * age_factor * risk_factor * 100, 4)
        return (
            f"universe: {params.universe}\n"
            f"annual_rate_pct: {annual_rate_pct}\n"
            f"monthly_premium_eur: {monthly}\n"
            f"risk_loading_pct: {round((risk_factor - 1) * 100, 1)}\n"
            f"available_formulas: DC_PTIA | DC_PTIA_IPT | DC_PTIA_IPT_IPP"
        )
    else:
        monthly = round(base * age_factor * risk_factor * beneficiary_factor, 2)
        return (
            f"universe: {params.universe}\n"
            f"monthly_premium_eur: {monthly}\n"
            f"annual_premium_eur: {round(monthly * 12, 2)}\n"
            f"risk_loading_pct: {round((risk_factor - 1) * 100, 1)}\n"
            f"beneficiaries_covered: {params.beneficiary_count}"
        )


class CompareOffresInput(BaseModel):
    universe: Universe = Field(description="Product universe for comparison")
    borrower_age: int = Field(description="Borrower/subscriber age", ge=18, le=90)
    loan_amount: Optional[int] = Field(None, description="Loan amount in euros (emprunteur)")
    loan_duration_years: Optional[int] = Field(None, description="Loan duration in years (emprunteur)")
    loan_type: Optional[LoanType] = Field(None, description="Loan type (emprunteur)")
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
        "Launch a multi-offer comparison on jRensure for the given universe and profile. "
        "Returns ranked list of available offers with indicative monthly premiums. "
        "For emprunteur, can filter by Lemoine eligibility."
    ),
)
async def compare_offres(params: CompareOffresInput) -> str:
    if params.universe != Universe.EMPRUNTEUR:
        return (
            f"universe: {params.universe}\n"
            f"message: Multi-offer comparison available only for emprunteur universe via jRensure. "
            f"For {params.universe}, use rikees_compute_tarif to get indicative pricing."
        )

    age_factor = 1.0 + max(0, (params.borrower_age - 35) * 0.015)
    risk_factors = {RiskLevel.STANDARD: 1.0, RiskLevel.AGGREVE: 1.35, RiskLevel.TRES_AGGREVE: 1.75}
    rf = risk_factors.get(params.risk_level, 1.0)
    base_amount = params.loan_amount or 200_000

    offers = []
    for o in _EMPRUNTEUR_OFFERS:
        if params.lemoine_eligible is True and not o["lemoine"]:
            continue
        if params.risk_level in (RiskLevel.AGGREVE, RiskLevel.TRES_AGGREVE) and o["lemoine"]:
            continue
        monthly = round(base_amount * 0.0015 * age_factor * rf / 12 * (0.9 if o["lemoine"] else 1.0), 2)
        offers.append(f"  - {o['name']} ({o['code']}): {monthly} €/mois | formule {o['formula']} | lemoine: {o['lemoine']}")

    lines = [f"universe: emprunteur", f"borrower_age: {params.borrower_age}", f"offers ({len(offers)}):"] + offers
    return "\n".join(lines)


class PiecesJustificativesInput(BaseModel):
    universe: Universe = Field(description="Product universe")
    product_code: Optional[str] = Field(None, description="Specific product code (e.g. 'eclipse_pro')")
    lemoine_eligible: bool = Field(False, description="Whether Lemoine applies (removes medical questionnaire)")

    model_config = {"use_enum_values": True}


_PIECES: dict[str, list[str]] = {
    "emprunteur": [
        "Pièce d'identité en cours de validité (CNI recto-verso ou passeport)",
        "Justificatif de domicile < 3 mois",
        "Tableau d'amortissement signé par la banque prêteuse",
        "Bulletins de salaire des 3 derniers mois (salarié) OU 2 derniers avis d'imposition (TNS)",
        "[si hors-Lemoine] Questionnaire de santé complet",
        "[si capital > 300 000 €] Rapport médical et examens complémentaires",
    ],
    "sante": [
        "Pièce d'identité",
        "Attestation de sécurité sociale",
        "RIB pour prélèvement",
    ],
    "prevoyance": [
        "Pièce d'identité",
        "Justificatif de revenus TNS (avis d'imposition N-1 ou attestation URSSAF)",
        "Extrait Kbis ou attestation d'activité professionnelle",
        "Questionnaire de santé (si garanties IPT/PTIA incluses)",
    ],
    "sante_collective": [
        "Accord collectif ou Décision Unilatérale de l'Employeur (DUE)",
        "Liste nominative du personnel (modèle Excel fourni par l'assureur)",
        "SIRET de l'entreprise",
        "Attestations de non-couverture pour les salariés dispensés d'adhésion",
    ],
    "gav": [
        "Pièce d'identité",
        "RIB",
    ],
}


@mcp.tool(
    name="rikees_get_pieces_justificatives",
    description=(
        "Return the list of required supporting documents for a given product universe and optional product code. "
        "If lemoine_eligible is True, the medical questionnaire is removed from emprunteur requirements."
    ),
)
async def get_pieces_justificatives(params: PiecesJustificativesInput) -> str:
    pieces = list(_PIECES.get(params.universe, ["Pièce d'identité", "RIB"]))
    if params.lemoine_eligible and params.universe == Universe.EMPRUNTEUR:
        pieces = [p for p in pieces if "questionnaire" not in p.lower() and "médical" not in p.lower()]
        pieces.append("✓ Lemoine applicable — questionnaire médical supprimé")
    lines = [f"universe: {params.universe}", f"product_code: {params.product_code or 'all'}", "pieces_requises:"]
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
        "Generate and return download URLs for DDA-compliant quote documents. "
        "Produces: devis (quote PDF), IPID, fiche_conseil (advice note), and optionally conditions générales. "
        "Documents expire after 30 days."
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


class ApiTarificationSchemaInput(BaseModel):
    universe: Universe = Field(Universe.EMPRUNTEUR, description="Universe to get API schema for")

    model_config = {"use_enum_values": True}


@mcp.tool(
    name="rikees_get_api_tarification_schema",
    description=(
        "Return the API schema for the tarification endpoint of the given universe, "
        "including input parameters, types, constraints, error codes, and rate limits."
    ),
)
async def get_api_tarification_schema(params: ApiTarificationSchemaInput) -> str:
    if params.universe == Universe.EMPRUNTEUR:
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
    return (
        f"endpoint: POST /v1/tarification/{params.universe}\n"
        f"note: Full schema available in the developer documentation portal. "
        f"Core parameters: universe, subscriber_age, beneficiary_count, coverage_level."
    )


class MadelinPlafondInput(BaseModel):
    annual_taxable_income: int = Field(description="Annual taxable professional income in euros", ge=0)
    contract_type: str = Field("prevoyance", description="Contract type: prevoyance | retraite | complementaire_sante")
    pass_year: int = Field(2024, description="PASS year (default 2024 = 46 368 €)")


@mcp.tool(
    name="rikees_get_madelin_plafonds",
    description=(
        "Calculate Madelin deductibility limits for a TNS/independent professional. "
        "Returns applicable ceiling and calculation breakdown for the given income and contract type."
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
        "Verify that a set of collective guarantee levels meets the minimum requirements of a given CCN "
        "(Convention Collective Nationale) and/or the ANI framework. "
        "Returns a compliance status (green/orange/red) per criterion and overall verdict."
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
# ── PORTEFEUILLE / SUIVI TOOLS ───────────────────────────────────────────────
# ---------------------------------------------------------------------------


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
}


@mcp.tool(
    name="rikees_get_dossier_status",
    description=(
        "Return the current status of a submitted dossier: status code, French label, "
        "last update timestamp, pending actions with deadlines, and policy number if accepted."
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
]


@mcp.tool(
    name="rikees_get_portefeuille",
    description=(
        "Return the active portfolio view with optional filters by universe, status, or upcoming expiry window. "
        "Lists contracts with client name, universe, status, monthly premium, and next expiry date."
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
        "Return contracts expiring within the specified number of days, ordered by urgency. "
        "Includes recommended action for each contract (renewal, Lemoine opt-out, etc.)."
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
        "Return the production dashboard KPIs for the specified period: "
        "quotes generated, dossiers submitted, acceptance rate, revenue, and status breakdown."
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
        "Return downloadable contractual documents for an active contract: "
        "conditions particulières, conditions générales, tableau des garanties, attestation. "
        "Returns PDF download URLs valid for 7 days."
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
        "Initiate a modification request on an active contract. "
        "Supported modifications: adjunction/removal of beneficiary, guarantee level change, "
        "quota change, cancellation. Returns a modification request ID and estimated processing time."
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
        "Return the API schema for the dossier status endpoint: HTTP method, URL, response format, "
        "status codes, SLA, rate limits, and integration best practices (polling strategy)."
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

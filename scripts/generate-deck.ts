/**
 * generate-deck.ts
 *
 * Generates the Autonomize AI PA Solution Architecture slide deck (PPTX + DOCX)
 * from structured slide data using the deck-builder package.
 *
 * SSOT chain:
 *   solution-architecture.md  (ground truth)
 *     → presentation.md       (narrative SSOT — full slide content)
 *       → this file            (slide-optimized — concise text sized for PPTX)
 *         → PPTX + DOCX        (rendered output)
 *
 * When editing: update presentation.md first, then sync changes here.
 * Text is intentionally shorter than presentation.md to fit slide constraints.
 *
 * Usage:   npx tsx scripts/generate-deck.ts
 * Shortcut: make deck
 *
 * Output files include date and HHMM timestamp for iteration tracking.
 */

import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { renderPptx, renderDocx } from '../../scripts/deck-builder/index.ts';
import type { BrandTheme, Slide } from '../../scripts/deck-builder/index.ts';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, '..');
const DIAGRAMS = resolve(PROJECT_ROOT, 'docs/architecture/diagrams');
const OUTPUT_DIR = resolve(PROJECT_ROOT, 'docs/presentation');

// Image height constant — used for slides with image + table/callout below
const IMG_WITH_TABLE = 2.8; // inches — leaves room for table + callout

// ---------------------------------------------------------------------------
// Brand theme — extracted from autonomize.ai CSS
// ---------------------------------------------------------------------------
const brand: BrandTheme = {
  colors: {
    primary: '29065A',   // deep purple (hero backgrounds, nav)
    accent:  '731EE3',   // bright purple (CTAs, highlights)
    light:   'F8F4FE',   // pale lavender (callout backgrounds)
    text:    '1A1A1A',   // near-black
    white:   'FFFFFF',
  },
  fonts: {
    heading: 'Calibri',
    body:    'Calibri',
  },
  logoPath: null,
};

// ---------------------------------------------------------------------------
// Slide data — maps 1:1 to presentation.md
// ---------------------------------------------------------------------------
const slides: Slide[] = [
  // ── Slide 1: Title ──────────────────────────────────────────────────────
  {
    id: 'title',
    title: 'AI-Driven Prior Authorization',
    body: [
      { type: 'heading', content: 'Solution Architecture for a Large US Health Plan' },
      { type: 'text', content: '' },
      { type: 'text', content: 'Paul Prae  |  Principal AI Engineer & Architect' },
      { type: 'text', content: 'www.paulprae.com' },
    ],
  },

  // ── Slide 2: The Problem & Opportunity ──────────────────────────────────
  {
    id: 'problem',
    title: 'The Problem & Opportunity',
    body: [
      { type: 'heading', content: 'The Problem' },
      { type: 'text', content: 'Manual PA costs $10.97/transaction provider-side (CAQH 2024), $3.52 payer-side vs $0.05 electronic. 93% of physicians say PA delays care (AMA 2024).' },
      { type: 'heading', content: 'The Opportunity — Altais + Autonomize AI (Feb 2026)' },
      { type: 'table', headers: ['Metric', 'Result'], rows: [
        ['PA review time reduction', '45%'],
        ['Manual error reduction', '54%'],
        ['Auto-determination rate', '50%'],
      ]},
      { type: 'heading', content: 'Why Autonomize AI' },
      { type: 'text', content: '• Live at 3 of the 5 largest US health plans\n• PA Copilot on Azure Marketplace — Microsoft Pegasus Program member\n• ServiceNow partnership extends reach into payer workflows\n• CMS-0057-F deadline (Jan 2027) creates urgency' },
    ],
  },

  // ── Slide 3: PA Request Lifecycle ───────────────────────────────────────
  {
    id: 'lifecycle',
    title: 'PA Request Lifecycle',
    body: [
      { type: 'image', path: resolve(DIAGRAMS, '03-pa-request-flow.png'), alt: 'PA Request Lifecycle Flow', maxH: 4.0 },
      { type: 'callout', content: 'Submit → Intake (OCR) → Validate (eligibility) → AI Review (coverage matching + confidence) → Route (auto-approve / human review / pend) → Respond (payer core + provider notification)' },
    ],
  },

  // ── Slide 4: Demo — Proof of Concept ────────────────────────────────────
  {
    id: 'demo',
    title: 'Demo — Proof of Concept',
    body: [
      { type: 'callout', label: 'LIVE DEMO', content: 'Working proof of concept — demonstrates core clinical review (steps 4-5 of the lifecycle).' },
      { type: 'image', path: resolve(DIAGRAMS, '07-demo-architecture.png'), alt: 'Demo Architecture', maxH: IMG_WITH_TABLE },
      { type: 'table', fontSize: 9, headers: ['Demo Scope (Phase 0)', 'Production Differences'], rows: [
        ['5 PA cases with real ICD-10/CPT codes', 'Mock eligibility → Payer Core integration'],
        ['AI reviews in ~30s via Claude tool use', 'Local criteria → CMS Coverage Database API'],
        ['FHIR R4 data models (fhir.resources R4B)', 'Synthetic data → real clinical records via FHIR'],
        ['CLI, REST API + Swagger, Web Dashboard', 'Single-user → Azure Container Apps + auto-scale'],
      ]},
    ],
  },

  // ── Slide 5: System Context ─────────────────────────────────────────────
  {
    id: 'context',
    title: 'System Context',
    body: [
      { type: 'image', path: resolve(DIAGRAMS, '01-system-context.png'), alt: 'System Context Diagram', maxH: 3.2 },
      { type: 'table', headers: ['Actor', 'Role', 'Integration'], rows: [
        ['Healthcare Providers', 'Submit PA requests', 'Fax, Portal, X12 278'],
        ['Autonomize AI Platform', 'AI-driven clinical review', 'PA Copilot on Genesis'],
        ['Health Plan Systems', 'Eligibility, benefits, clinical data', 'REST API, FHIR R4'],
        ['Regulators (CMS)', 'Compliance reporting', 'CMS-0057-F metrics'],
      ]},
    ],
  },

  // ── Slide 6: Solution Architecture ──────────────────────────────────────
  {
    id: 'architecture',
    title: 'Solution Architecture',
    body: [
      { type: 'image', path: resolve(DIAGRAMS, '02-component-architecture.png'), alt: 'Component Architecture', maxH: 3.0 },
      { type: 'table', fontSize: 9, headers: ['Component', 'Azure Service', 'Purpose'], rows: [
        ['Ingestion Gateway', 'API Mgmt + Functions', 'Receives all PA channels'],
        ['Document Processing', 'AI Document Intelligence', 'OCR for faxes'],
        ['Eligibility Service', 'Payer Core REST API', 'Member validation'],
        ['Clinical Data Aggregation', 'Health Data Services (FHIR R4)', 'Unified clinical context'],
        ['PA Copilot', 'Genesis Platform + Claude', 'AI clinical review'],
        ['Determination Router', 'Functions + Rules', 'Confidence-based routing'],
        ['Clinical Review Dashboard', 'Autonomize AI Studio', 'Human reviewer interface'],
        ['Determination Response', 'Azure Functions', 'Payer Core writeback'],
        ['LLMOps Pipeline', 'Azure Monitor + Evals', 'Performance monitoring'],
        ['Audit & Compliance', 'Immutable Blob Storage', 'Tamper-proof audit trail'],
      ]},
    ],
  },

  // ── Slide 7: Why This Architecture ──────────────────────────────────────
  {
    id: 'why',
    title: 'Why This Architecture',
    body: [
      { type: 'text', content: '• Safety-first routing — confidence thresholds route low-certainty cases to human reviewers; no auto-deny without clinical review' },
      { type: 'text', content: '• Configurable thresholds — start conservative, tune with real performance data' },
      { type: 'text', content: '• CMS-0057-F compliance — FHIR R4 foundation meets Jan 2027 API deadline without re-architecture' },
      { type: 'text', content: '• Azure-native — leverages Autonomize\'s Azure ecosystem, Pegasus Program, and Marketplace presence' },
      { type: 'text', content: '• Full audit trail — every determination records model version, input hash, reasoning, evidence, and confidence for 7-year retention' },
    ],
  },

  // ── Slide 8: Security Risks & Mitigations ───────────────────────────────
  {
    id: 'security',
    title: 'Top 3 Security Risks & Mitigations',
    body: [
      { type: 'table', fontSize: 9, headers: ['#', 'Risk', 'Architectural Mitigation', 'Operational Mitigation'], rows: [
        ['1', 'PHI exposure through AI pipeline', 'PHI tokenization before LLM — AI sees clinical facts without patient identity', 'Zero data retention for model training (enterprise terms)'],
        ['2', 'Prompt injection via clinical docs', 'Document sanitization + system prompt isolation', 'Output validation requires evidence citations'],
        ['3', 'Untraceable AI decisions', 'Tamper-proof audit: model version, input hash, reasoning, confidence', 'Immutable 7-year retention, append-only writes'],
      ]},
      { type: 'callout', label: 'Additional controls', content: 'Entra ID RBAC, AES-256 at rest, TLS 1.2+ in transit, private endpoints, no auto-deny without human review.' },
    ],
  },

  // ── Slide 9: Progressive Delivery ───────────────────────────────────────
  {
    id: 'delivery',
    title: 'Progressive Delivery',
    body: [
      { type: 'table', headers: ['Phase', 'Focus', 'Key Deliverable'], rows: [
        ['Phase 0: Demo', 'Prove the concept', 'Working AI PA review with mock data'],
        ['Phase 1: MVP', 'Single LOB, single channel', 'Production PA processing with human review'],
        ['Phase 2: Scale', 'Multi-channel, multi-LOB', 'Fax OCR, legacy data, LOB configuration'],
        ['Phase 3: Enterprise', 'Full scale, compliance', 'All channels, 20 LOBs, CMS reporting'],
      ]},
      { type: 'callout', label: 'Design principle', content: 'Each phase produces a deployable, demonstrable system. Decision gates between phases use real performance data to scope the next phase.' },
    ],
  },

  // ── Slide 10: Discussion Starters ───────────────────────────────────────
  {
    id: 'discussion',
    title: 'Discussion Starters',
    body: [
      { type: 'heading', content: 'Business Strategy' },
      { type: 'text', content: '• How does the ServiceNow partnership change payer integration strategy?\n• What is the target auto-determination rate for Phase 1?' },
      { type: 'heading', content: 'Technical Depth' },
      { type: 'text', content: '• How does the Genesis Platform handle coverage criteria updates?\n• What\'s the Azure AI Foundry Agent Service integration status?' },
      { type: 'heading', content: 'Implementation' },
      { type: 'text', content: '• Which LOB is the ideal Phase 1 candidate?\n• What\'s been the biggest integration challenge with existing payer deployments?' },
    ],
  },

  // ── Appendix A: Clinical Data Integration ───────────────────────────────
  {
    id: 'appendix-a',
    title: 'Appendix A: Clinical Data Integration',
    body: [
      { type: 'image', path: resolve(DIAGRAMS, '04-clinical-data-access.png'), alt: 'Clinical Data Access', maxH: IMG_WITH_TABLE },
      { type: 'table', headers: ['Source', 'Protocol', 'Auth'], rows: [
        ['Modern EMRs', 'FHIR R4 REST API', 'OAuth 2.0 / SMART on FHIR'],
        ['Legacy DB Connector', 'DB connector / HL7 v2', 'Service account + VNet'],
      ]},
      { type: 'callout', label: 'FHIR R4', content: 'Interoperability standard for clinical data. Modern sources expose natively; legacy data normalized before AI processing.' },
      { type: 'callout', label: 'Security', content: 'All clinical data passes through PHI tokenization before reaching the AI engine.' },
    ],
  },

  // ── Appendix B: AI Model Monitoring ─────────────────────────────────────
  {
    id: 'appendix-b',
    title: 'Appendix B: AI Model Monitoring & Feedback',
    body: [
      { type: 'image', path: resolve(DIAGRAMS, '06-llmops-pipeline.png'), alt: 'LLMOps Pipeline', maxH: IMG_WITH_TABLE },
      { type: 'heading', content: 'Detect drift' },
      { type: 'text', content: '• Overturn rate monitoring (human overrides AI), appeal rate, accuracy trends\n• Automated evals — golden test cases benchmarked on schedule\n• Confidence distribution shifts signal model or data changes' },
      { type: 'heading', content: 'Feedback loop' },
      { type: 'text', content: '1. Reviewer corrections → updated eval dataset  2. Benchmark new vs current  3. Staged blue-green rollout  4. Guardrails always active' },
    ],
  },

  // ── Appendix C: Scaling to 20 LOBs ──────────────────────────────────────
  {
    id: 'appendix-c',
    title: 'Appendix C: Scaling to 20 LOBs',
    body: [
      { type: 'table', headers: ['Approach', 'Cost', 'Isolation', 'Complexity'], rows: [
        ['Multi-tenant', 'Lower', 'Logical', 'Lower'],
        ['Multi-instance', 'Higher', 'Physical', 'Higher'],
      ]},
      { type: 'callout', label: 'Recommendation', content: 'Start multi-tenant with per-LOB config. Genesis Platform supports it. Separate instances only where regulation requires physical isolation.' },
      { type: 'callout', label: 'Honest unknowns', content: 'The right answer depends on actual LOB rule complexity and regulatory requirements — both are discovery questions.' },
    ],
  },

  // ── Sources ─────────────────────────────────────────────────────────────
  {
    id: 'sources',
    title: 'Sources & References',
    body: [
      { type: 'table', fontSize: 8, headers: ['#', 'Claim', 'Source'], rows: [
        ['1', '$10.97 manual PA labor cost (provider)', 'CAQH 2024 Index, p. 9'],
        ['2', '$3.52 manual PA labor cost (payer)', 'CAQH 2024 Index, p. 9'],
        ['3', '~$0.05 electronic PA cost (payer)', 'CAQH 2024 Index, p. 9'],
        ['4', '45% PA review time reduction', 'Altais + Autonomize AI (BusinessWire Feb 2026)'],
        ['5', '54% manual error reduction', 'Altais + Autonomize AI (BusinessWire Feb 2026)'],
        ['6', '50% auto-determination rate', 'Altais + Autonomize AI (BusinessWire Feb 2026)'],
        ['7', '93% physicians say PA delays care', 'AMA 2024 Prior Auth Survey, p. 5'],
        ['8', 'CMS-0057-F Phase 1 Jan 2026', 'CMS Interoperability Final Rule Fact Sheet'],
        ['9', 'CMS-0057-F Phase 2 Jan 2027', 'CMS Interoperability Final Rule Fact Sheet'],
        ['10', 'Live at 3 of 5 largest US plans', 'Autonomize AI (BusinessWire Feb 2026)'],
        ['11', 'PA Copilot on Azure Marketplace', 'Azure Marketplace listing'],
        ['12', 'ServiceNow partnership', 'BusinessWire Mar 2026'],
        ['13', 'Claude in Azure AI Foundry', 'Microsoft Learn'],
        ['14', 'Genesis Platform', 'GlobeNewsWire Apr 2025'],
        ['15', 'Microsoft Pegasus Program', 'BusinessWire Nov 2025'],
      ]},
    ],
  },
];

// ---------------------------------------------------------------------------
// Generate
// ---------------------------------------------------------------------------
async function main(): Promise<void> {
  const now = new Date();
  const date = now.toISOString().slice(0, 10); // YYYY-MM-DD
  const hhmm = now.toTimeString().slice(0, 5).replace(':', ''); // HHMM
  const baseName = `autonomize-ai-pa-solution-architecture-paul-prae-${date}-${hhmm}`;

  console.log(`\nGenerating ${slides.length} slides → ${baseName}\n`);

  await renderPptx(slides, brand, resolve(OUTPUT_DIR, `${baseName}.pptx`), PROJECT_ROOT);
  await renderDocx(slides, brand, resolve(OUTPUT_DIR, `${baseName}.docx`), PROJECT_ROOT);

  console.log('\nDone.\n');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

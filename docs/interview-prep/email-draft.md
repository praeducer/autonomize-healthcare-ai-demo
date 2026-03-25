# Email Draft — Pre-Interview Materials
## Send evening of March 24 for the March 25 afternoon presentation

---

**To:** Kris Nair, Suresh Gopalakrishnan, Ujjwal Rajbhandari
**From:** Paul Prae
**Subject:** Prior Authorization Solution Architecture — Materials for Tomorrow's Discussion

---

Copy the plain text below into Outlook:

---

Hi Kris, Suresh, and Ujjwal,

Thank you for the opportunity to work through this assignment. I've enjoyed diving into the PA automation space -- it's a domain where AI can genuinely reduce clinical burden and improve patient access to care, and Autonomize is clearly well-positioned to lead here.

I'm sharing my materials ahead of our conversation tomorrow so you can review at your convenience:


ATTACHED:

- autonomize-ai-pa-solution-architecture-paul-prae-2026-03-24.docx -- Latest draft of my solution architecture presentation (10 slides + appendix with 4 architecture diagrams). I'll polish it up and export it to PowerPoint tomorrow before our discussion.


ON GITHUB:

- Presentation source (live updates):
  https://github.com/praeducer/autonomize-healthcare-ai-demo/blob/main/docs/presentation/presentation.md

- Full repository (architecture docs, solution design, and demo source code):
  https://github.com/praeducer/autonomize-healthcare-ai-demo

I'm also in the middle of developing a demo that implements the core AI-driven clinical review flow from the architecture -- a proof of concept using Claude, FHIR R4 data models, and real ICD-10/CPT codes across 5 realistic PA cases. I'm hoping to have it ready to present tomorrow as well. I'd encourage you to check out the repo if you're curious.


A few highlights from the architecture:

- Azure-native design aligned with Autonomize's Pegasus Program membership and Azure Marketplace presence -- the architecture is built to deploy into the ecosystem you already operate in.

- Safety-first determination routing -- confidence-based scoring routes every case: high-confidence auto-approves, low-confidence goes to human reviewers, and no case is ever auto-denied without clinical review.

- AI-specific security controls designed for healthcare -- PHI tokenization before the LLM so the AI reasons over clinical facts without ever seeing patient identity, prompt injection defense on clinical documents, and output validation requiring evidence citations.


I'm excited to share this solution with you and looking forward to talking shop tomorrow afternoon.

All the best,

Paul Prae
www.paulprae.com

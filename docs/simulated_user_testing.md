# Simulated Usability Dry Run

> **Important:** This document is an internal simulated usability exercise only. It does **not** satisfy the capstone requirement for testing with three real users. The official real-user record remains in `docs/user_testing.md`.

**Project:** Football Laws Referee RAG  
**Live demo:** https://football-laws-rag-production.up.railway.app  
**Purpose:** Identify likely usability issues before the required real-user sessions.

## Test protocol

Each simulated tester follows the same intended real-user flow:

1. Sign in.
2. Ask at least three football-law questions.
3. Inspect at least one retrieved IFAB evidence item.
4. Rate answer clarity from 1–5.
5. Rate trust/citation usefulness from 1–5.
6. Note one strength and one possible usability issue.

---

## Simulated Tester 1 — Mohammed

**Profile used for simulation:** Football fan with general knowledge of the Laws of the Game but no specialist refereeing background.

**Questions used:**

1. Is being in an offside position itself an offence?
2. Can a goal be scored directly from a throw-in?
3. When can the referee apply advantage?

**Expected interaction observations:**

- The example-question selector makes it easy to understand the system's scope.
- The answer structure is concise and suitable for quick rule clarification.
- Expandable retrieved evidence helps verify that the answer is grounded in IFAB material.
- Official source links increase confidence in the response.

**Potential issue identified:**

A non-specialist may not immediately understand why multiple evidence chunks are displayed for a short question. A one-line explanation such as “These are the IFAB passages used to produce the answer” would make the evidence section clearer.

**Simulated clarity rating:** 5/5  
**Simulated trust/citation rating:** 5/5

**Suggested improvement from this dry run:** Add a short helper caption above the evidence section explaining why the retrieved passages are shown.

---

## Simulated Tester 2 — Osamah

**Profile used for simulation:** User familiar with football terminology and interested in refereeing decisions.

**Questions used:**

1. What are the four VAR review categories?
2. What is the sanction for DOGSO handball?
3. How far must attackers stay from a wall of three or more defenders at a free kick?

**Expected interaction observations:**

- Exact football terminology such as VAR and DOGSO is handled well by the hybrid retrieval pipeline.
- The answer is more useful when conditions and exceptions are stated immediately after the main rule.
- Source titles and IFAB URLs make the application feel more reliable than a generic chatbot.

**Potential issue identified:**

Technical terms such as DOGSO can be clear to referees but less clear to casual users. The interface could improve accessibility by expanding an abbreviation the first time it appears, while preserving the official term.

**Simulated clarity rating:** 4/5  
**Simulated trust/citation rating:** 5/5

**Suggested improvement from this dry run:** Expand common abbreviations on first use, for example “Denying an Obvious Goal-Scoring Opportunity (DOGSO).”

---

## Simulated Tester 3 — Nabeel

**Profile used for simulation:** User focused on practical match situations and referee decision-making.

**Questions used:**

1. What happens if an opponent remains in the penalty area at a goal kick because there was not enough time to leave?
2. Where must the goalkeeper have part of one foot when a penalty kick is taken?
3. Who has the final decision when other match officials assist?

**Expected interaction observations:**

- Practical scenario questions are answered with the relevant rule conditions rather than only a yes/no response.
- The evidence expanders allow a user to inspect the exact retrieved context.
- The interface remains simple enough for repeated questioning without needing to learn a complex workflow.

**Potential issue identified:**

For scenario-based questions, users may benefit from a clearer visual distinction between the direct answer and exceptions/conditions.

**Simulated clarity rating:** 4/5  
**Simulated trust/citation rating:** 5/5

**Suggested improvement from this dry run:** Format answers with a short “Answer” statement followed by a compact “Conditions / Exceptions” section when the rule has important qualifications.

---

## Simulated Usability Summary

### Strengths identified

- Simple authentication and focused single-purpose interface.
- Clear English-only football-law scope.
- Strong provenance through official IFAB evidence and source links.
- Concise answers suitable for refereeing questions.
- Hybrid retrieval is appropriate for both exact football terminology and paraphrased questions.

### Likely usability improvements

1. Add a one-line explanation above the retrieved evidence section.
2. Expand specialist abbreviations on first use.
3. Separate the direct answer visually from conditions and exceptions.
4. Keep evidence collapsed by default so the interface remains uncluttered.

## Real-user requirement

These simulated observations are useful for internal QA only. The capstone requirement still requires three actual people to use the deployed application and provide genuine feedback. Record those sessions in `docs/user_testing.md`.

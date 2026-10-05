# Corpus Collection and Audit Report

**Audit date:** 5 October 2026  
**Reference workflow:** GitHub Actions — Corpus validation, run #20  
**Corpus language:** English  
**Primary authority:** The International Football Association Board (IFAB)

## Result

The reproducible collection pipeline successfully validated, downloaded, extracted, and audited all source records in `data/sources_manifest.csv`.

| Metric | Result |
|---|---:|
| Manifest source records | 31 |
| Successfully downloaded | 31 / 31 |
| Successfully extracted | 31 / 31 |
| English documents | 31 |
| HTML documents | 29 |
| PDF documents | 2 |
| Extracted words | 71,191 |
| Extracted characters | 414,538 |
| Exact normalized full-document duplicate groups | 0 |
| Documents under 100 extracted words | 0 |

## Source composition

The corpus includes:

- the 17 Laws of the Game topic pages;
- VAR protocol;
- substitution and concussion protocols;
- captain-only communication guidance;
- temporary dismissal and return-substitute guidance;
- practical guidance for match officials;
- official 2026/27 law-change material;
- official IFAB circular material.

All source records point to the official `theifab.com` domain.

## Collection method

The pipeline performs the following checks before the corpus enters retrieval:

1. The source manifest must contain between 20 and 50 records.
2. Source IDs and URLs must be unique.
3. Every source must be English.
4. Every URL must belong to the official IFAB domain.
5. HTML responses must contain substantive IFAB content.
6. PDF responses must contain a valid PDF signature and a non-trivial file size.
7. SHA-256 checksums are recorded for downloaded snapshots.
8. Text extraction must yield substantive content.
9. The extracted corpus is checked for exact normalized full-document duplicates.
10. Suspiciously short documents are rejected.

## Reproducibility

Run locally:

```bash
python scripts/check_sources.py
python scripts/collect_sources.py
python scripts/extract_sources.py
python scripts/audit_corpus.py
```

Raw snapshots and processed source text are intentionally excluded from the public Git repository. They are reproducibly downloaded from the official URLs and can be retained as CI artifacts or local build artifacts. This keeps the repository focused on code, provenance metadata, evaluation data, and reproducible processing rather than republishing third-party source material.

## Interpretation

The corpus satisfies the capstone requirement for **20–50 high-quality documents** using 31 independently identified official IFAB source records. Retrieval evaluation is performed on a separate fixed 30-question golden set; corpus collection success is not treated as retrieval-quality evidence.

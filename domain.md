# Domain — Football Laws Referee RAG

## Project name

**Football Laws Referee RAG**

## Domain

Association football refereeing and the **Laws of the Game**.

## Problem

Football-law questions are often answered from memory, social media clips, outdated interpretations, or competition-specific rules. This project builds a Retrieval-Augmented Generation system that answers in English from a curated corpus of official IFAB material and shows the evidence used.

## Target users

- Referees and referee trainees
- Coaches and players
- Football analysts
- Fans studying the Laws of the Game
- Students preparing for referee-law examinations

## In scope

The first version covers:

- Laws 1–17
- Referee powers and duties
- Assistant referees and other match officials
- Offside
- Fouls and misconduct
- Handball
- Advantage
- Disciplinary sanctions
- Free kicks
- Penalty kicks
- Restarts
- Goalkeeper restrictions
- VAR protocol
- Temporary dismissals
- Return substitutes
- Permanent concussion substitutions
- Captain-only communication guidance
- Match-official positioning, movement, teamwork, body language, and whistle use
- Current 2026/27 changes and official IFAB circular material included in the source manifest

## Out of scope

- Futsal
- Beach soccer
- Competition-specific regulations unless explicitly added as a separate source set
- Match results, news, transfers, or statistics
- Making an official decision for a real match incident
- Replacing the authority of the referee, competition organiser, IFAB, or a national association

## Language

The application, prompts, documentation, evaluation questions, and user-facing answers are **English only**.

## Source policy

The corpus is built only from official IFAB sources in the first version. Every source must have:

- a stable source ID
- title
- official URL
- language
- season/version where applicable
- source type
- retrieval status
- retrieval date
- local snapshot path after collection
- checksum after download

The collector must not silently replace a failed official source with an unofficial mirror.

## Reference season

The target season is **2026/27**. The pipeline must preserve season/version metadata so older and newer editions are not mixed silently.

## Answering policy

The assistant must:

1. answer only from retrieved evidence;
2. cite the source title and URL;
3. mention the relevant Law or protocol when available;
4. clearly say when the evidence is insufficient;
5. avoid presenting educational explanations as official match decisions.

## Success criteria

The project is complete only when it satisfies the capstone requirements:

- 20–50 high-quality sources
- documented ingestion decisions
- hybrid retrieval
- reranking
- 30 golden questions
- Recall@5 >= 80%
- Streamlit or Gradio interface
- simple authentication
- three real-user tests
- public deployment
- RAGAS report on 20 questions
- cost analysis for 1K, 10K, and 100K users
- one-page ADR

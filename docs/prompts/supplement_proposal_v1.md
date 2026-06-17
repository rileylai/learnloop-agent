---
prompt_id: supplement_proposal
version: supplement_proposal_v1
---

## System
You are LearnLoop Agent.
Return one strict JSON object for a supplement proposal.
Do not return markdown.
Do not return extra keys.
Use only facts grounded in the source text.

## User
Create a supplement proposal JSON with fields:
- title
- target_path
- source
- summary
- concepts
- notes

Field requirements:
- title: concise supplement title
- target_path: Notion path where supplement should be appended later
- source: object with source_type and source_display_name
- summary: concise grounded summary
- concepts: non-empty array of key concepts
- notes: array of practical notes

source_type=${source_type}
source_display_name=${source_display_name}
source_text:
${source_text}

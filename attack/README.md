# Attack Statistics Example Doc

This document will serve as an example for how we are planning on formatting our statisitics/log document. In here we will have generalized prompt success stats that will then refernce the specific prompts in their separate attack outline docs. Each prompt that was used will be classified as context, recon, or RCE prompts. 

## Defense Version Definitions

Throughout this notebook, each attack prompt is tested against three different versions of the DocTalk system, each representing a different level of security hardening. Success rates are recorded separately for each version to demonstrate the effectiveness of various defense strategies. Hardening against these two specific attacks were prioritized, and the differences in protection against the attacks are listed below

### Version 0 (v0): Baseline/Control
This is the first iteration of the DocTalk system we created with no protection against attack vectors. This includes:
- agents having basic system prompts with little security
- no input validation
- no code execution restrictions with pyTool/statAgent
- no proper verification of user ID's
- no control of database queries

### Version 1 (v1): Over-Restrictive Prompt Hardening
The first defensive iteration using aggressive system prompt modifications. This includes:
- strict prohibitions against cross-user data access
- user spoofing detection
- verification requirements to call tools
- upgraded/hardened system prompts for orchestrator, database agent and stats agent

### Version 2 (v2): Guardrails + Code-Level Enforcement
- explanation of v2 modifications (unsure)

### Success Rate Interpretation
| Rate | Meaning |
| ---- | ------- |
| 0/5 | Attack failed in all 5 attempts |
| 1/5 - 2/5 | Attack occasionally succeeds (inconsistent) |
| 3/5 - 4/5 | Attack frequently succeeds (vulnerable) |
| 5/5 | Attack succeeds consistently (critical vulnerability) |



## Control prompts
success rate of these control prompts

## Recon prompts

| Total attack attempts | Sucessful Attempts | Success Rate |
| --------------------- | ------------------ | ----- |
| 10 | 8 | 80% |

Note: we can further classify these recon prompts into if they target certain agents, tools, features etc.

Refer to specific examples and their success rates in the section called 'Phase 1' [here](./doc.ipynb)

## RCE attack prompts

| Total attack attempts | Sucessful Attempts | Success Rate |
| --------------------- | ------------------ | ----- |
| 10 | 6 | 60% |
|    |   |  neijvrnienrinrgnrugnergn <br>rjnrignrijrnbirbnribnetibntuibnrijbnrbijrnbijnrb   |

Note: we can further classify these recon prompts into if they target certain agents, tools, features etc.

Refer to specific examples and their success rates in the section called 'Phase 3' [here](./doc.ipynb)
## Context Prompts

| Total attack attempts | Sucessful Attempts | Success Rate |
| --------------------- | ------------------ | ----- |
| 10 | 9 | 90% |

Note: we can further classify these recon prompts into if they target certain agents, tools, features etc.

## Most secure agents
talk about which agents we built that were extremely secure vs those that werent

## Common blockers

Talk here about things that commonly went wrong in unsucessful attacks. max responses, Thai!, code generation errors, etc

## Workarounds

Ways we mitigated failure. New chat, uppercase commands, word changes, encoding, etc 

# Attack Statistics Example Doc

This document will serve as an example for how we are planning on formatting our statisitics/log document. In here we will have generalized prompt success stats that will then refernce the specific prompts in their separate attack outline docs. Each prompt that was used will be classified as context, recon, or RCE prompts. 

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

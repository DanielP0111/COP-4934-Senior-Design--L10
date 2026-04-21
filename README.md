# Security Concerns in Agentic AI
This repository is for UCF Senior Design team L19. We are researching security concerns in agentic AI systems in conjunction with the Georgia Tech Research Institute (GTRI).

<img src="./themes/favicon.png" alt="DocTalk Logo" width="150" height="150">

## DocTalk - An Agentic AI Security Sandbox
To evaluate the security posture of agentic AI systems, we developed our own platform, DocTalk. DocTalk is an agentic AI system designed for Bill’s Clinic (a fictional clinic named after GTRI’s research server) that assists patients with common healthcare questions and administrative tasks through a multi-agent architecture. This repository includes three variations of DocTalk (provided as separate branches), each implementing different levels of defensive measures. Additionally, the main branch contains a suite of complex cyberattacks that have been tested against each version to highlight key security concerns in agentic AI systems. The project is open source, allowing others to explore, test, and better understand vulnerabilities in agentic AI.  

## How can I run DocTalk?
Choose which version of DocTalk you want to run by navigating to the specific branch on GitHub. Copy the clone link and specify the branch you want to clone, as shown in the example below:
```
git clone --branch <BRANCH VERSION> --single-branch https://github.gatech.edu/GTRI-UCF-Senior-Design/agentic-ai-security.git
```

Once the repository is cloned locally, navigate to the Jupyter Notebook labeled `run_system.ipynb` for step-by-step instructions and commands to deploy DocTalk.

## DocTalk Version 0 (V0)
Our V0 branch hosts all of the code and documentation for DocTalk V0. V0 is a variation that lacks security beyond what the underlying LLM has already been trained to provide. There is no prompt hardening or technical guardrails. Feel free to try your own attacks and defenses against DocTalk V0!

## Our team
Each member of our team is driven to learn, build, and secure agentic AI systems through direct implementation and testing, while sharing their knowledge with others. 
- Jack - Project Manager and Eavesdropping Engineer
- Liam - AI Lead Developer and Prompt Injection Engineer
- Imani - AI Developer and Remote Code Execution Engineer
- Bobby - AI Developer and Ransomware Engineer
- Daniel - Lead Infrastructure Developer and Remote Code Execution Engineer
- Carson - Infrastructure Developer and Ransomware Engineer
- Colin - Infrastructure Developer and Prompt Injection Engineer

## Disclaimer
The information, techniques, tools, and examples that are depicted in this paper are displayed solely for educational purposes. No material in this paper encourages or supports illegal or unethical activity on any computing systems. Any and all cyber operations should be conducted in a legal manner on systems that the user either owns or has permission to use. The procedures described above were carried out solely on systems that either owned or were given consent to test on. The L19 Senior Design team is not liable for any consequences resulting from the use of the techniques described above on other computing systems. 

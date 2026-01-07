# templates.py

SECTION_TEMPLATES = {
    "idea_problem": [
        r"problem statement",
        r"problem we solve",
        r"your idea",
        r"our idea",
        r"idea\s*[:\-]",
        r"title\s*[:\-]"
    ],

    "solution_approach": [
        r"the mission",
        r"our solution",
        r"solution approach",
        r"we propose",
        r"how it works",
        r"implementation"
    ],

   
        "uniqueness_claim": [
        r"unique",
        r"why should we select you",
        r"what makes.*different",
        r"existing apps",
        r"existing systems",
        r"unlike.*apps",
        r"goes beyond",
        r"not just",
        r"different from"
    
    ],

    "tech_stack": [
        r"tech[\s\-]*stack",
        r"tech stack & platforms",
        r"frontend",
        r"backend",
        r"ai\s*&\s*ml stack",
        r"cloud\s*/\s*devops",
        r"blockchain"
    ],

    "team_capability": [
        r"by team",
        r"team\s*[:\-]",
        r"team members",
        r"we are a team",
        r"our team"
    ]
}

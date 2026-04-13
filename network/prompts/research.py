RESEARCH_PROMPT = """You are a research assistant. Given a person's name and company, research and return a JSON object with:
1. "role": Their current role/title
2. "recent_work": Recent projects, blog posts, talks, or news
3. "company_news": Recent company developments
4. "tech_stack": Technologies they work with
5. "mutual_interests": Overlaps with Paramjeet's background — AI/ML Engineer, RAG systems, LLM pipelines, CoachMe+ hackathon winner, Northeastern MS, boxing enthusiast
6. "best_angle": The single best reason to reach out now
7. "conversation_starters": 2-3 specific things to mention

Person: {name}
Company: {company}

Return ONLY valid JSON. No markdown, no explanation."""

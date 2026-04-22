prompts = [
    # 1. Balanced baseline → good overall summary with depth + structure
    """
    Summarize the following academic paper clearly and in detail.

    Focus on:
    - Main ideas and contributions
    - Methodology (including assumptions and setup)
    - Key results (with important quantitative findings)

    Do not oversimplify. Preserve important technical details.
    Explain not only what was done, but why it matters.
    """,

    # 2. Technical depth → emphasizes methodology, tools, and precise results
    """
    Provide a detailed and technically accurate summary of the following academic paper.

    Emphasize:
    - Methodology in depth (models, assumptions, simulation setup)
    - Exact results and quantitative findings
    - Any technical frameworks or tools used

    Avoid general statements. Be precise and specific.
    """,

    # 3. Teaching clarity → easier to understand, more intuitive explanations
    """
    Summarize the following academic paper in a clear and easy-to-understand way.

    Explain concepts as if teaching someone with basic background knowledge.
    Maintain accuracy, but prioritize clarity and intuition.

    Highlight the most important ideas and avoid unnecessary complexity.
    """,

    # 4. Critical analysis → includes evaluation of strengths, weaknesses, reliability
    """
    Summarize and critically analyze the following academic paper.

    In addition to summarizing:
    - Evaluate the methodology
    - Discuss strengths and weaknesses
    - Comment on the reliability of results

    Focus on both what the paper does and how well it does it.
    """,

    # 5. Concise dense → shorter summary but still includes key information
    """
    Provide a concise but information-dense summary of the following academic paper.

    Include all critical information:
    - Main idea
    - Methodology
    - Key results

    Avoid unnecessary words, but do not omit important details.
    """
]

template = """
Structure your answer as:
- Introduction
- Key Concepts
- Methodology
- Results
- Conclusion
"""
evaluation_prompt_beginning = """
You are evaluating summaries of the same academic paper.

Summaries:\n
"""
evaluation_prompt_ending = """
Task:
Choose the best summary based on clarity, accuracy, completeness,
and usefulness.
Return ONLY the number of the best summary (for example: 3).
"""
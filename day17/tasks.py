from crewai import Task


def create_research_task(researcher):
    return Task(
        description="""Conduct comprehensive research on the following topic: {topic}
        
        Your research must include:
        1. A clear definition and overview of the topic
        2. At least 5 specific, verifiable facts
        3. Current state and recent developments (last 1-2 years if possible)
        4. Key players, organizations, or figures involved
        5. Different perspectives or ongoing debates
        6. Potential future implications
        
        Structure your findings clearly so the writer can use them directly.
        Do NOT write the article — just compile the research notes.""",
        
        expected_output="""Research Report structured as:
        
        OVERVIEW: 2-3 sentence definition
        
        KEY FACTS:
        - Fact 1 (with context)
        - Fact 2 (with context)
        ... (minimum 5 facts)
        
        CURRENT DEVELOPMENTS:
        What is happening right now in this space
        
        KEY PLAYERS:
        Organizations/people/places relevant to the topic
        
        PERSPECTIVES:
        Different viewpoints or debates
        
        WRITER NOTES:
        Any additional context the writer should know""",
        
        agent=researcher,
    )


def create_write_task(writer, research_task):
    return Task(
        description="""Using the research provided, write a compelling article about {topic}.
        
        Requirements:
        - Length: 600-800 words
        - Structure: Hook → Introduction → 3-4 body sections with subheadings → Conclusion
        - Tone: Informative but engaging, accessible to general readers
        - Use the research facts — do not invent information
        - Start with a strong hook that grabs attention
        - End with a memorable conclusion that gives the reader something to think about
        
        The research notes from the Researcher are your source material.""",
        
        expected_output="""A complete article (600-800 words) with:
        - Catchy title
        - Engaging opening hook (2-3 sentences)
        - Clear introduction paragraph
        - 3-4 body sections with ## subheadings
        - Smooth transitions between sections
        - Strong conclusion paragraph
        
        Formatted in Markdown.""",
        
        agent=writer,
        context=[research_task],      
    )


def create_edit_task(editor, write_task):
    return Task(
        description="""Edit and polish the article about {topic} to publication quality.
        
        Your editing checklist:
        1. Fix any grammatical or spelling errors
        2. Improve sentence flow and readability
        3. Ensure the hook is truly engaging
        4. Verify the article uses research facts correctly (no hallucinations)
        5. Make sure subheadings are descriptive and interesting
        6. Strengthen weak transitions
        7. Ensure the conclusion is memorable
        8. Check that the tone is consistent throughout
        
        Return the COMPLETE edited article — not just your comments.""",
        
        expected_output="""The final, publication-ready article in Markdown format.
        
        Include at the end:
        
        ---
        EDITOR NOTES:
        - List of key changes made
        - Overall quality assessment (1-10)
        - Any remaining concerns""",
        
        agent=editor,
        context=[write_task],
        
    )
# main.py
import os
from crewai import Crew, Process
from agents import create_researcher, create_writer, create_editor
from tasks import create_research_task, create_write_task, create_edit_task


def run_pipeline(topic: str) -> str:
    print(f"\n{'='*60}")
    print(f"Starting CrewAI pipeline for topic: {topic}")
    print(f"{'='*60}\n")

    # Create agents
    researcher = create_researcher()
    writer = create_writer()
    editor = create_editor()

    # Create tasks — order matters for sequential process
    research_task = create_research_task(researcher)
    write_task = create_write_task(writer, research_task)
    edit_task = create_edit_task(editor, write_task)

    # Assemble crew
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, write_task, edit_task],
        process=Process.sequential,
        verbose=True,
    )

    # Kickoff
    result = crew.kickoff(inputs={"topic": topic})

    # Save output
    output_file = f"output_{topic[:30].replace(' ', '_')}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(str(result))

    print(f"\n{'='*60}")
    print(f"Pipeline complete! Article saved to: {output_file}")
    print(f"{'='*60}\n")

    return str(result)


if __name__ == "__main__":
    topic = input("Enter article topic: ").strip()
    if not topic:
        topic = "The Impact of Artificial Intelligence on Healthcare"

    article = run_pipeline(topic)
    print("\n=== FINAL ARTICLE ===\n")
    print(article)
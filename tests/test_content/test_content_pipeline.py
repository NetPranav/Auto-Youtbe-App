import pytest
from database.models import Topic
from content_engine.research_context.builder import ResearchContextBuilder
from content_engine.hook_generator.generator import HookGenerator
from content_engine.models import ContentStrategy

def test_research_context_builder():
    builder = ResearchContextBuilder()
    topic = Topic(
        title="Test Topic",
        main_technology="Python",
        secondary_technologies=["AI", "ML"],
        industry="Tech",
        importance="Major",
        estimated_audience="Broad",
        description="A great topic."
    )
    
    context = builder.build_context(topic)
    assert "Test Topic" in context
    assert "Python" in context
    assert "AI, ML" in context
    assert "A great topic." in context

def test_hook_generator():
    generator = HookGenerator()
    strategy = ContentStrategy(
        target_audience="Devs", tone="Fun", video_length_minutes=5,
        objective="Teach", key_learning_outcomes=["Learn"], curiosity_level="High"
    )
    
    # We mocked the hooks in the class to return a 9.2 max score
    best_hook = generator.generate_hook("context", strategy)
    
    assert best_hook.score == 9.2
    assert "Stop writing code the old way" in best_hook.text

# Add more tests as needed for the other logic modules.

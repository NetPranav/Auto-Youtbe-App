import os
from providers.voice.bark import BarkProvider

def test_bark():
    print("Initializing Bark Provider...")
    provider = BarkProvider()
    
    print("Generating test voiceover...")
    output_path = provider.generate_voice(
        text="Hello world! This is a test of the new Bark voice generation engine running locally on the RTX 4060.",
        output_dir="assets/rendered/voice"
    )
    
    if output_path:
        print(f"Success! Voice saved to: {output_path}")
    else:
        print("Failed to generate voice.")

if __name__ == "__main__":
    test_bark()

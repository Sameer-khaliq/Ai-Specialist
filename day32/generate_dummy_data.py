import json

topics = ["machine learning", "web development", "databases", "cloud computing", 
          "cybersecurity", "mobile apps", "data science", "networking", "AI ethics", "DevOps"]

texts = []
for i in range(600):
    topic = topics[i % len(topics)]
    texts.append(f"This is a sample document number {i} about {topic}, covering key concepts and practical applications in the field.")

with open("day32/sample_texts.json", "w") as f:
    json.dump(texts, f)

print(f"Generated {len(texts)} sample texts.")
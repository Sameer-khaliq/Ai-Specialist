# tasks.py
TASKS = [
    {
        "id": "t1_classification",
        "prompt": "Classify this customer message as 'complaint', 'question', or 'praise': 'The product arrived broken and I want a refund.'",
        "difficulty": "easy"
    },
    {
        "id": "t2_extraction",
        "prompt": "Extract name, date, and amount from: 'Invoice paid by John Carter on March 5th, 2025 for $450.'",
        "difficulty": "easy"
    },
    {
        "id": "t3_summarization",
        "prompt": """Summarize in 2 sentences: [If you've ever wanted your ears to have eyes, then I've got great news. It seems Apple is gearing up to release AirPods with cameras in them as soon as next year.

                    Apparently, these cameras aren't for taking pictures. According to Bloomberg, they'll feed information about your surroundings to its virtual assistant Siri, unlocking a whole set of new possibilities for how you might interact with your devices without looking at them.

                    Apple hasn't confirmed or denied the news, but the Bloomberg report comes from a journalist with a stellar reputation for leaking the company's secrets. And it's part of a broader trend.

                    For the past 60 years or so, screens have been the predominant way we have interacted with computers. Now it's possible they could fade further into the background.]""",
        "difficulty": "medium"
    },
    {
        "id": "t4_reasoning",
        "prompt": "A store had 120 items. They sold 35% on Monday and 20% of the remainder on Tuesday. How many items are left?",
        "difficulty": "medium"
    },
    {
        "id": "t5_code_generation",
        "prompt": "Write a Python function that checks if a string is a palindrome, ignoring spaces and case.",
        "difficulty": "hard"
    },
]
import random

class CommentatorResponseGenerator:
    def __init__(self):
        self.commentators = [
            "Tony Romo", "Joe Buck", "Al Michaels", "Chris Berman", "John Madden", 
            "Pat McAfee", "Big Cat", "PFT Commenter", "Adam Schefter", "Ian Rapoport",
            # ... Add up to 100 names
        ]
        
        self.moods = [
            "enthusiastic", "cynical", "optimistic", "pessimistic", "sarcastic", 
            "analytical", "jubilant", "serious", "lighthearted", "grumpy", 
            # ... Add up to 20 moods
        ]
        
        self.response_structures = [
            "Start with a brief analysis, then give the grade.",
            "Open with the grade, followed by an explanation.",
            "Begin with a comparison to a well-known player, then give the grade.",
            "Lead with a statement of the player's strengths, followed by the grade.",
            "Start with a humorous comment, then the grade.",
            # ... Add additional structures
        ]

    def generate_parameters(self):
        """Generate and return random commentator, mood, and response structure."""
        commentator = random.choice(self.commentators)
        mood = random.choice(self.moods)
        structure = random.choice(self.response_structures)
        return commentator, mood, structure

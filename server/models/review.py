import random
import openai

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

    def generate_fantasy_review(self, player_name, player_position, player_grade, team_roster):
        """Generate a fantasy dynasty perspective review using OpenAI."""
        commentator, mood, structure = self.generate_parameters()

        # Construct a message content for OpenAI API
        messages = [
            {"role": "system", "content": f"You are {commentator}, known for your {mood} analysis."},
            {
                "role": "user", 
                "content": (
                    f"From a fantasy dynasty perspective, evaluate the football player {player_name}, who plays as a {player_position}. "
                    f"The player has received a grade of {player_grade:.2f}/10 based on the team's needs. "
                    f"Consider the rest of the team roster: {[player['player_name'] + ' (' + player['player_position'] + ')' for player in team_roster]}. "
                    f"Provide a review using the following structure: '{structure}'."
                )
            }
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=50  # Adjust as needed
            )
            review = response['choices'][0]['message']['content'].strip()
            return review
        except Exception as e:
            return f"Error generating review: {str(e)}"

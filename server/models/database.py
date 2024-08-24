from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    season = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'league_id': self.league_id,
            'name': self.name,
            'season': self.season
        }

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    league_id = db.Column(db.String(80), db.ForeignKey('league.league_id'))

    def to_dict(self):
        return {
            'team_id': self.team_id,
            'name': self.name,
            'league_id': self.league_id
        }

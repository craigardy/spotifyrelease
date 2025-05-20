from app import db

# Define users table model with email and Spotify refresh token
class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(255), primary_key=True)
    token = db.Column(db.Text, nullable=False)
    last_ran = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()

class Traveler(BASE):
    __tablename__ = "traveler"
    user = Column(String(64), primary_key=True)
    miles = Column(Integer)
    
    def __init__(self, user):
        self.user = user
        self.miles = 0
        
    def __repr__(self):
        return "USER %s HAS %i MILES" % (self.user, self.miles)
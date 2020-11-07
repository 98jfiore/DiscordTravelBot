from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()

class Traveler(BASE):
    __tablename__ = "traveler"
    userId = Column(String(50), primary_key=True)
    miles = Column(Integer)
    
    def __init__(self, userId):
        self.userId = str(userId
        self.miles = 0
        
    def __repr__(self):
        return "USER %s HAS %i MILES" % (self.userId, self.miles)
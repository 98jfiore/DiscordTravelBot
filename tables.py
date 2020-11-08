from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()

class Traveler(BASE):
    __tablename__ = "traveler"
    uid = Column(String(50), primary_key=True)
    miles = Column(Integer)
    location = Column(String(3), ForeignKey('country.ccode'))
    
    def __init__(self, userId, location):
        self.uid = userId
        self.miles = 0
        self.location = location
        
    def __repr__(self):
        return "USER %s HAS %i MILES" % (self.userId, self.miles)

class Country(BASE):
    __tablename__ = "country"
    ccode = Column(String(3), primary_key=True)
    name = Column(String(50))
    flag = Column(String(50))
    
    def __init__(self, ccode, name, flag):
        self.ccode = ccode
        self.name = name
        self.flag = flag
        
    def __repr__(self):
        return "COUNTRY %s IS %s" % (self.ccode, self.name)

class Border(BASE):
    __tablename__ = "border"
    ccodea = Column(String(3), ForeignKey('country.ccode'), primary_key=True)
    ccodeb = Column(String(3), primary_key=True)
    
    def __init__(self, ccodea, ccodeb):
        self.ccodea = ccodea
        self.ccodeb = ccodeb
        
    def __repr__(self):
        return "COUNTRY %s BORDERS %s" % (self.ccodea, self.ccodeb)

class Stamp(BASE):
    __tablename__ = "stamp"
    uid = Column('uid', String(50), ForeignKey('traveler.uid'), primary_key=True)
    code = Column('code', String(3), ForeignKey('country.ccode'), primary_key=True)
    
    def __init__(self, uid, ccode):
        self.uid = uid
        self.code = ccode
        
    def __repr__(self):
        return "%s STAMPED AT %s" % (self.uid, self.code)
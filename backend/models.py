from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class SentimentEnum(str, enum.Enum):
    positive = "Positive"
    neutral = "Neutral"
    negative = "Negative"


class InteractionTypeEnum(str, enum.Enum):
    meeting = "Meeting"
    call = "Call"
    email = "Email"
    conference = "Conference"
    virtual = "Virtual"


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    specialty = Column(String(100))
    hospital = Column(String(200))
    city = Column(String(100))
    email = Column(String(200))

    interactions = relationship("Interaction", back_populates="hcp")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "specialty": self.specialty,
            "hospital": self.hospital,
            "city": self.city,
            "email": self.email,
        }


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(100))  # Brochure, Sample, Leaflet, etc.
    product = Column(String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "product": self.product,
        }


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=True)
    hcp_name = Column(String(200))
    interaction_type = Column(String(50), default="Meeting")
    date = Column(String(20))
    time = Column(String(20))
    attendees = Column(Text)
    topics_discussed = Column(Text)
    sentiment = Column(String(50))
    materials_shared = Column(Text)  # JSON string of materials list
    samples_distributed = Column(Text)  # JSON string of samples list
    outcomes = Column(Text)
    follow_up_actions = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")

    def to_dict(self):
        return {
            "id": self.id,
            "hcp_name": self.hcp_name,
            "interaction_type": self.interaction_type,
            "date": self.date,
            "time": self.time,
            "attendees": self.attendees,
            "topics_discussed": self.topics_discussed,
            "sentiment": self.sentiment,
            "materials_shared": self.materials_shared,
            "samples_distributed": self.samples_distributed,
            "outcomes": self.outcomes,
            "follow_up_actions": self.follow_up_actions,
            "summary": self.summary,
        }

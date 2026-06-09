from sqlalchemy import Column, Integer, String, Float, Text, UniqueConstraint
from database import Base


class PlayerSeasonDB(Base):
    __tablename__ = "player_seasons"
    __table_args__ = (UniqueConstraint("year", "team", "pos", name="uq_player_year_team_pos"),)

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    age = Column(Integer, nullable=True)
    team = Column(String(50), nullable=True)
    league = Column(String(50), nullable=True)
    pos = Column(String(10), nullable=True)
    games = Column(Integer, nullable=True)
    games_started = Column(Integer, nullable=True)
    targets = Column(Integer, nullable=True)
    rec = Column(Integer, nullable=True)
    rec_yds = Column(Integer, nullable=True)
    rec_yds_per_rec = Column(Float, nullable=True)
    rec_td = Column(Integer, nullable=True)
    catch_pct = Column(Float, nullable=True)
    yds_from_scrimmage = Column(Integer, nullable=True)
    rush_att = Column(Integer, nullable=True)
    rush_yds = Column(Integer, nullable=True)
    fumbles = Column(Integer, nullable=True)
    av = Column(Integer, nullable=True)
    awards = Column(Text, nullable=True)

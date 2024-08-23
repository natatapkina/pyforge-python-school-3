from app.database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Molecule(Base):
    __tablename__ = 'molecule'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    smiles: Mapped[str]
    molecule_formula: Mapped[str]
    molecule_weight: Mapped[float]

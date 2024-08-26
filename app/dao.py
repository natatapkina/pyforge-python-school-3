from typing import Any

from sqlalchemy import delete, select, update

from database import Session
from models import Molecule


class MoleculeDAO:
    model = Molecule

    # Add molecule (smiles) and its identifier.
    @classmethod
    def create(cls, molecule: dict) -> int:
        with Session() as session:
            new_molecule = cls.model(**molecule)
            session.add(new_molecule)
            session.commit()
            return new_molecule.id

    # Get molecule by identifier.
    @classmethod
    def get_by_id(cls, molecule_id: int) -> Molecule | None:
        with Session() as session:
            query = select(cls.model).filter_by(id=molecule_id)
            result = session.execute(query)
            return result.scalar_one_or_none()

    # Updating a molecule by identifier.
    @classmethod
    def update(cls, molecule_id: int, updated_molecule: dict[str, Any]) -> int:
        with Session() as session:
            query = (
                update(cls.model)
                .where(cls.model.id == molecule_id)
                .values(**updated_molecule)
            )
            result = session.execute(query)
            session.commit()
            return result.rowcount

    # Delete a molecule by identifier.
    @classmethod
    def delete(cls, molecule_id: int) -> int:
        with Session() as session:
            query = delete(cls.model).where(cls.model.id == molecule_id)
            result = session.execute(query)
            session.commit()
            return result.rowcount

    # List all molecules.
    @classmethod
    def get_all(cls) -> list[Molecule]:
        with Session() as session:
            query = select(cls.model)
            result = session.execute(query)
            return result.scalars().all()

    # Substructure search for all added molecules.
    @classmethod
    def get_by_ids(cls, molecule_ids: list[int]) -> list[Molecule]:
        with Session() as session:
            query = select(cls.model).where(cls.model.id.in_(molecule_ids))
            result = session.execute(query)
            return result.scalars().all()

    # Create multiple molecules.
    @classmethod
    def bulk_create(cls, molecules: list[Molecule]) -> None:
        with Session() as session:
            session.add_all(molecules)
            session.commit()

from typing import Any
from sqlalchemy import delete, select, update
from database import Session
from models import Molecule


class MoleculeDAO:
    model = Molecule

    # Add molecule (smiles) and its identifier.
    @classmethod
    def create(cls, molecule: dict):
        with Session() as session:
            new_molecule = cls.model(**molecule)
            session.add(new_molecule)
            session.commit()
            return {
                'id': new_molecule.id,
                'name': new_molecule.name,
                'smiles': new_molecule.smiles,
                'molecule_formula': new_molecule.molecule_formula,
                'molecule_weight': new_molecule.molecule_weight,
            }

    # Get molecule by identifier.
    @classmethod
    def get_by_id(cls, molecule_id: int):
        with Session() as session:
            query = select(cls.model).filter_by(id=molecule_id)
            result = session.execute(query)
            return result.scalar_one_or_none()

    # Updating a molecule by identifier.
    @classmethod
    def update(cls, molecule_id: int, updated_molecule: dict[str, Any]):
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
    def delete(cls, molecule_id: int):
        with Session() as session:
            query = delete(cls.model).where(cls.model.id == molecule_id)
            result = session.execute(query)
            session.commit()
            return result.rowcount

    # List all molecules.
    @classmethod
    def get_all(cls):
        with Session() as session:
            query = select(cls.model)
            result = session.execute(query)
            return result.scalars().all()

    # Substructure search for all added molecules.
    @classmethod
    def get_by_ids(cls, molecule_ids: list[int]):
        with Session() as session:
            query = select(cls.model).where(cls.model.id.in_(molecule_ids))
            result = session.execute(query)
            return result.scalars().all()

    # Create multiple molecules.
    @classmethod
    def bulk_create(cls, molecules: list[Molecule]):
        with Session() as session:
            session.add_all(molecules)
            session.commit()

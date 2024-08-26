from pydantic import BaseModel


class MoleculeCreate(BaseModel):
    name: str
    smiles: str
    molecule_formula: str
    molecule_weight: float


class MoleculeUpdate(BaseModel):
    name: str | None = None
    smiles: str | None = None
    molecule_formula: str | None = None
    molecule_weight: float | None = None


class MoleculeOut(BaseModel):
    id: int
    name: str
    smiles: str
    molecule_formula: str
    molecule_weight: float

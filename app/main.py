import csv
import os
from io import StringIO
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from rdkit import Chem
import uuid

from dao import MoleculeDAO
from log import logger
from models import Molecule
from schemas import (
    MoleculeCreate,
    MoleculeOut,
    MoleculeUpdate,
    MoleculesResponse,
)


def substructure_search(
        structures_smiles: list[str],
        substructure_smiles: str,
) -> list[str]:
    search_result = []
    substructure_mol = Chem.MolFromSmiles(substructure_smiles)

    for structure_smiles in structures_smiles:
        structure_mol = Chem.MolFromSmiles(structure_smiles)

        if structure_mol.HasSubstructMatch(substructure_mol):
            search_result.append(structure_smiles)

    return search_result


def load_molecules_from_file(file) -> list[Molecule]:
    # read file as bytes and decode bytes into text stream
    buffer = StringIO(file.read().decode('utf-8'))
    reader = csv.DictReader(buffer)

    molecules = []

    for row in reader:
        molecule = Molecule(
            name=row['NAME'],
            smiles=row['SMILES'],
            molecule_formula=row['FORMULA'],
            molecule_weight=float(row['WEIGHT']),
        )

        molecules.append(molecule)

    return molecules


app = FastAPI()


# Add molecule (smiles) and its identifier.
@app.post('/add', status_code=201)
def add_molecule(molecule: MoleculeCreate) -> MoleculeOut:
    logger.info('A new request is received to create a new molecule.')
    molecule_id = MoleculeDAO.create(molecule.model_dump())
    molecule = MoleculeDAO.get_by_id(molecule_id)
    return MoleculeOut(
        id=molecule.id,
        name=molecule.name,
        smiles=molecule.smiles,
        molecule_formula=molecule.molecule_formula,
        molecule_weight=molecule.molecule_weight,
    )


# Get molecule by identifier.
@app.get('/molecules/{molecule_id}')
def retrieve_molecule(molecule_id: int) -> MoleculeOut:
    logger.info(
        f'A new request is received to get '
        f'a molecule with ID {molecule_id}.',
    )
    molecule = MoleculeDAO.get_by_id(molecule_id)
    if molecule is not None:
        return MoleculeOut(
            id=molecule.id,
            name=molecule.name,
            smiles=molecule.smiles,
            molecule_formula=molecule.molecule_formula,
            molecule_weight=molecule.molecule_weight,
        )
    else:
        logger.info(f'Molecule with ID {molecule_id} is not found.')
        raise HTTPException(status_code=404, detail='Molecule is not found.')


# Updating a molecule by identifier.
@app.put('/molecules/{molecule_id}')
def update_molecule(
        molecule_id: int,
        updated_molecule: MoleculeUpdate,
) -> MoleculeOut:
    logger.info(
        f'A new request is received to update '
        f'a molecule with ID {molecule_id}.',
    )
    n_updated = MoleculeDAO.update(
        molecule_id,
        updated_molecule.model_dump(exclude_none=True),
    )
    if n_updated != 0:
        molecule = MoleculeDAO.get_by_id(molecule_id)
        return MoleculeOut(
            id=molecule.id,
            name=molecule.name,
            smiles=molecule.smiles,
            molecule_formula=molecule.molecule_formula,
            molecule_weight=molecule.molecule_weight,
        )
    else:
        logger.info(f'Molecule with ID {molecule_id} is not found.')
        raise HTTPException(status_code=404, detail='Molecule is not found.')


# Delete a molecule by identifier.
@app.delete('/molecules/{molecule_id}')
def delete_molecule(molecule_id: int) -> None:
    logger.info(
        f'A new request is received to remove '
        f'a molecule with ID {molecule_id}.',
    )
    n_deleted = MoleculeDAO.delete(molecule_id)
    if n_deleted == 0:
        logger.info(f'Molecule with ID {molecule_id} is not found.')
        raise HTTPException(status_code=404, detail='Molecule is not found.')


# Stores cursor-molecule iterator key-value pairs.
class IteratorContainer:
    def __init__(self) -> None:
        self.container = {}

    def __call__(self):
        return self.container


# List all molecules.
@app.get('/molecules/')
def retrieve_all_molecules(
        iterator_container: Annotated[dict, Depends(IteratorContainer())],
        limit: int | None = None,
        cursor: str | None = None,
) -> MoleculesResponse:
    logger.info('A new request is received to get all molecules list.')

    # Check if cursor exists.
    if cursor is not None:
        molecules_iterator = iterator_container.get(cursor)
        if molecules_iterator is None:
            raise HTTPException(status_code=404, detail='Cursor is not found.')
    else:
        molecules = MoleculeDAO.get_all()
        all_molecules = []

        for molecule in molecules:
            mol = MoleculeOut(
                id=molecule.id,
                name=molecule.name,
                smiles=molecule.smiles,
                molecule_formula=molecule.molecule_formula,
                molecule_weight=molecule.molecule_weight,
            )
            all_molecules.append(mol)

        # Create a cursor as a hexadecimal UUID string.
        cursor = str(uuid.uuid4())
        molecules_iterator = iter(all_molecules)
        iterator_container[cursor] = molecules_iterator

    # Check if the limit variable has a value.
    # If no limit, then delete the cursor value and return all molecules.
    # if the limit is specified, then return the specified number of molecules.
    if limit is None:
        del iterator_container[cursor]
        return MoleculesResponse(molecules=list(molecules_iterator))
    else:
        limited_molecules = []
        for i in range(limit):
            try:
                limited_molecules.append(next(molecules_iterator))
            except StopIteration:
                del iterator_container[cursor]
                return MoleculesResponse(molecules=limited_molecules)
        return MoleculesResponse(cursor=cursor, molecules=limited_molecules)


# Substructure search for all added molecules.
@app.get('/substructure_search/{substructure_smiles}')
def substructure_search_molecules(
        substructure_smiles: str,
) -> list[MoleculeOut]:
    logger.info(f'Seatching for substructure {substructure_smiles}.')
    smiles_from_db = []
    smiles_x_db_id = {}

    # Collect all smiles from DB and create smiles-index mapping.
    molecules = MoleculeDAO.get_all()

    for molecule in molecules:
        if molecule.smiles not in smiles_from_db:
            smiles_x_db_id[molecule.smiles] = molecule.id
            smiles_from_db.append(molecule.smiles)

    found_structures = substructure_search(smiles_from_db, substructure_smiles)
    # Get indexes for interested structures.
    ids = [smiles_x_db_id[smiles] for smiles in found_structures]
    molecules = MoleculeDAO.get_by_ids(ids)
    all_molecules = []

    for molecule in molecules:
        mol = MoleculeOut(
            id=molecule.id,
            name=molecule.name,
            smiles=molecule.smiles,
            molecule_formula=molecule.molecule_formula,
            molecule_weight=molecule.molecule_weight,
        )
        all_molecules.append(mol)

    return all_molecules


# [Optional] Upload file with molecules (the choice of format is yours).
@app.post('/create_db/')
def upload_molecules_from_file(file: UploadFile) -> list[MoleculeOut]:
    logger.info('A new request is received to upload file with molecules.')
    load_molecules = load_molecules_from_file(file.file)
    MoleculeDAO.bulk_create(load_molecules)
    molecules = MoleculeDAO.get_all()
    all_molecules = []

    for molecule in molecules:
        mol = MoleculeOut(
            id=molecule.id,
            name=molecule.name,
            smiles=molecule.smiles,
            molecule_formula=molecule.molecule_formula,
            molecule_weight=molecule.molecule_weight,
        )
        all_molecules.append(mol)

    return all_molecules


# [Optional] Load balancer. Add method to check balancing.
@app.get('/check_balancing/')
def get_server():
    return {'server_id': os.getenv('SERVER_ID', 'UNKNOWN')}

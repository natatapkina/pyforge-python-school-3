import csv
import os
from io import StringIO
from fastapi import FastAPI, HTTPException, UploadFile
from typing import Any
from rdkit import Chem

from models import Molecule
from dao import MoleculeDAO


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


def load_molecules_from_file(file):
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
def add_molecule(molecule: dict):
    return MoleculeDAO.create(molecule)


# Get molecule by identifier.
@app.get('/molecules/{molecule_id}')
def retrieve_molecule(molecule_id: int):
    molecule = MoleculeDAO.get_by_id(molecule_id)
    if molecule is not None:
        return molecule
    else:
        raise HTTPException(status_code=404, detail='Molecule is not found.')


# Updating a molecule by identifier.
@app.put('/molecules/{molecule_id}')
def update_molecule(molecule_id: int, updated_molecule: dict[str, Any]):
    n_updated = MoleculeDAO.update(molecule_id, updated_molecule)
    if n_updated != 0:
        return MoleculeDAO.get_by_id(molecule_id)
    else:
        raise HTTPException(status_code=404, detail='Molecule is not found.')


# Delete a molecule by identifier.
@app.delete('/molecules/{molecule_id}')
def delete_molecule(molecule_id: int):
    n_deleted = MoleculeDAO.delete(molecule_id)
    if n_deleted == 0:
        raise HTTPException(status_code=404, detail='Molecule is not found.')


# List all molecules.
@app.get('/molecules/')
def retrieve_all_molecules():
    return MoleculeDAO.get_all()


# Substructure search for all added molecules.
@app.get('/substructure_search/{substructure_smiles}')
def substructure_search_molecules(substructure_smiles: str):
    smiles_from_db = []
    smiles_x_db_id = {}

    # Collect all smiles from DB and create smiles-index mapping.
    molecules = MoleculeDAO.get_all()

    for molecule in molecules:
        smiles_x_db_id[molecule.smiles] = molecule.id
        smiles_from_db.append(molecule.smiles)

    found_structures = substructure_search(smiles_from_db, substructure_smiles)
    # Get indexes for interested structures.
    ids = [smiles_x_db_id[smiles] for smiles in found_structures]
    return MoleculeDAO.get_by_ids(ids)


# [Optional] Upload file with molecules (the choice of format is yours).
@app.post('/create_db/')
def upload_molecules_from_file(file: UploadFile):
    molecules = load_molecules_from_file(file.file)
    MoleculeDAO.bulk_create(molecules)
    return MoleculeDAO.get_all()


# [Optional] Load balancer. Add method to check balancing.
@app.get('/check_balancing/')
def get_server():
    return {'server_id': os.getenv('SERVER_ID', 'UNKNOWN')}

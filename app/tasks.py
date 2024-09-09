from rdkit import Chem

from celery_worker import celery
from dao import MoleculeDAO
from log import logger


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


# Return a list of molecule dictionaries
# since the Celery works with json format.
@celery.task
def substructure_search_task(substructure_smiles: str):
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
        mol = {
            'id': molecule.id,
            'name': molecule.name,
            'smiles': molecule.smiles,
            'molecule_formula': molecule.molecule_formula,
            'molecule_weight': molecule.molecule_weight,
        }
        all_molecules.append(mol)

    return all_molecules

import os
from Bio.PDB import PDBParser, PPBuilder

def load_pdb(filepath):
    pdb_parser = PDBParser(QUIET=True)
    structure = pdb_parser.get_structure(os.path.splitext(os.path.basename(filepath))[0], filepath)
    return structure

def clean_pdb(structure, remove_waters=True, keep_hydrogens=False, handle_altloc=True, remove_insertions=True, report_gaps=False):
    model = structure[0]  # Keep first model
    cleaned_atoms = []
    sequence_gaps = []
    
    if report_gaps:
        sequence_gaps = check_sequence_gaps(model)
    
    for residue in model.get_residues():
        if residue.id[0] != " ":  # Skip HETATM records
            continue
        if remove_waters and residue.get_id()[0] == 'W':
            continue
        if residue.resname == 'MSE':  # Convert selenomethionine to methionine
            residue.resname = 'MET'
        if remove_insertions and residue.id[2] != ' ':  # Remove insertion codes
            continue
        for atom in residue:
            if atom.is_disordered():
                atom = atom.disordered_get()
                if handle_altloc and atom.get_occupancy() != max([a.get_occupancy() for a in atom.parent]):
                    continue  # Keep highest occupancy
            if atom.occupancy < 0:
                atom.set_occupancy(0.00)  # Set negative occupancy to 0.00
            else:
                atom.set_occupancy(1.00)  # Otherwise, set occupancy to 1.00
            if not keep_hydrogens and atom.element.strip() == 'H':
                continue
            cleaned_atoms.append(atom)
    return cleaned_atoms, sequence_gaps

def save_cleaned_pdb(output_folder, filename, atoms):
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"cleaned_{filename}")
    with open(output_file, "w") as fw:
        for i, atom in enumerate(atoms, 1):
            fw.write(f"ATOM  {i:5d} {atom.name:>4} {atom.parent.resname:>3} {atom.parent.parent.id} {atom.parent.id[1]:4d}   "
                     f"{atom.coord[0]:8.3f}{atom.coord[1]:8.3f}{atom.coord[2]:8.3f}  {atom.occupancy:6.2f} {atom.bfactor:6.2f}          {atom.element:>2}\n")
    return output_file

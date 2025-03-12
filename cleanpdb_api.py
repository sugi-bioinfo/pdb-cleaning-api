from fastapi import FastAPI, UploadFile, File
import shutil
import os
import zipfile
from pathlib import Path
from cleanpdb import load_pdb, clean_pdb, save_cleaned_pdb  # Import from your script
from fastapi.responses import FileResponse

app = FastAPI()

# Define output folder
DOWNLOADS_DIR = Path("./cleaned_pdb")
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

def process_pdb(file_path: Path):
    structure = load_pdb(file_path)
    cleaned_atoms, _ = clean_pdb(structure, remove_waters=True, keep_hydrogens=False, handle_altloc=True, remove_insertions=True, report_gaps=False)
    cleaned_path = DOWNLOADS_DIR / f"cleaned_{file_path.name}"
    save_cleaned_pdb(DOWNLOADS_DIR, file_path.name, cleaned_atoms)
    return cleaned_path

@app.post("/upload/")
async def upload_pdb(files: list[UploadFile] = File(...)):
    if len(files) == 1:
        # Process single file
        file = files[0]
        temp_path = DOWNLOADS_DIR / file.filename
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        cleaned_file = process_pdb(temp_path)
        return {"download_url": f"http://127.0.0.1:8000/download/{cleaned_file.name}"}
    
    else:
        # Process multiple files
        session_folder = DOWNLOADS_DIR / f"session_{len(os.listdir(DOWNLOADS_DIR))}"
        session_folder.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            temp_path = session_folder / file.filename
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            process_pdb(temp_path)
        
        # Zip the folder
        zip_path = session_folder.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for pdb_file in session_folder.glob("*"):
                zipf.write(pdb_file, pdb_file.name)
        
        return {"download_url": f"http://127.0.0.1:8000/download/{zip_path.name}"}

@app.get("/download/{file_name}")
def download_file(file_name: str):
    file_path = DOWNLOADS_DIR / file_name
    if file_path.exists():
        return FileResponse(path=file_path, filename=file_name, media_type="application/octet-stream")
    return {"error": "File not found"}
@app.get("/")
def home():
    return {"message": "PDB Cleaning API is running!"}
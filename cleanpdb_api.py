from fastapi import FastAPI, UploadFile, File
import shutil
import os
import zipfile
from pathlib import Path
from cleanpdb import load_pdb, clean_pdb, save_cleaned_pdb  # Import from your script
from fastapi.responses import FileResponse

app = FastAPI()

# Define the output folder inside the project directory
DOWNLOADS_DIR = Path("./cleaned_pdb")

# Ensure the folder exists and print confirmation
try:
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directory created or already exists: {DOWNLOADS_DIR}")
except Exception as e:
    print(f"❌ Error creating directory: {e}")

def process_pdb(file_path: Path):
    """Loads, cleans, and saves a cleaned PDB file."""
    try:
        structure = load_pdb(file_path)
        cleaned_atoms, _ = clean_pdb(structure, remove_waters=True, keep_hydrogens=False, handle_altloc=True, remove_insertions=True, report_gaps=False)
        
        cleaned_path = DOWNLOADS_DIR / f"cleaned_{file_path.name}"
        save_cleaned_pdb(DOWNLOADS_DIR, file_path.name, cleaned_atoms)
        
        print(f"✅ Successfully saved cleaned file at: {cleaned_path}")
        return cleaned_path
    except Exception as e:
        print(f"❌ Error processing PDB file: {e}")
        return None

@app.post("/upload/")
async def upload_pdb(files: list[UploadFile] = File(...)):
    """Handles single or multiple PDB file uploads and returns download links."""
    if len(files) == 1:
        # Process single file
        file = files[0]
        temp_path = DOWNLOADS_DIR / file.filename
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cleaned_file = process_pdb(temp_path)
        if cleaned_file:
            return {"download_url": f"https://pdb-cleaning-api.onrender.com/download/{cleaned_file.name}"}
        else:
            return {"error": "File processing failed."}
    
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
        
        return {"download_url": f"https://pdb-cleaning-api.onrender.com/download/{zip_path.name}"}

@app.get("/download/{file_name}")
def download_file(file_name: str):
    """Serves the cleaned PDB file for download."""
    file_path = DOWNLOADS_DIR / file_name
    if file_path.exists():
        print(f"✅ Serving file: {file_path}")  # Debugging
        return FileResponse(
            path=str(file_path), 
            filename=file_name, 
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    print(f"❌ File not found: {file_path}")  # Debugging
    return {"error": "File not found", "checked_path": str(file_path)}

@app.get("/list_files")
def list_files():
    """Lists all saved files in the cleaned_pdb directory."""
    files = [f.name for f in DOWNLOADS_DIR.iterdir()]
    return {"saved_files": files}

@app.get("/debug_paths")
def debug_paths():
    """Shows debug info: working directory and existing files."""
    return {
        "current_working_directory": str(Path.cwd()),
        "downloads_directory": str(DOWNLOADS_DIR),
        "existing_files": [f.name for f in DOWNLOADS_DIR.glob("*")]
    }

@app.get("/")
def home():
    """Homepage route."""
    return {"message": "PDB Cleaning API is running!"}

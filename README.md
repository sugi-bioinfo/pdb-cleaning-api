# 🧬 PDB Cleaning API

This API allows users to **upload PDB files, clean them**, and **download** the processed versions.  
It is built using **FastAPI** and deployed on **Render** for public access. 🚀  

## 🌍 **Live API URL**
**Base URL:** [`https://pdb-cleaning-api.onrender.com`](https://pdb-cleaning-api.onrender.com)  

You can access the API documentation here:  
📑 **Swagger UI:** [`https://pdb-cleaning-api.onrender.com/docs`](https://pdb-cleaning-api.onrender.com/docs)  

---

## **🚀 API Endpoints & Usage**
### 1️⃣ Upload a PDB File
**Uploads a PDB file and returns a cleaned version.**  
- **URL:** `/upload/`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Example cURL Request:**
  ```sh
  curl -X POST -F "files=@example.pdb" https://pdb-cleaning-api.onrender.com/upload/

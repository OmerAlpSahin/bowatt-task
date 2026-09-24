from fastapi import APIRouter, UploadFile
from fastapi import HTTPException


router = APIRouter(prefix="/api")



@router.post("/sources")
async def upload_sources(files: list[UploadFile]):
    names = []
    for f in files:
        if not (f.content_type or "").startswith("text/"):
            raise HTTPException(status_code=400, detail="Data type should be txt")
        
    for f in files:
        names.append({"name": f.filename, "size": f.size, "type": f.content_type})
        
    return {"uploaded": names}
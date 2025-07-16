from fastapi import APIRouter
router = APIRouter()

@router.get("/api/arcs")
def get_arcs():
    # TODO: Pull from identity_arc_tracker
    return [{"name": "Test Arc", "status": "active"}]

@router.get("/api/symbolic-memory")
def get_symbolic_memory():
    # TODO: Return filtered symbolic memory tags
    return [{"tag": "Hero", "importance": 0.8}] 
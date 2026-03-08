import os

def get_file_structure(root_path: str, _base_path: str = None):
    """
    Recursively builds a dictionary representing the file structure.
    File entries include a ``rel_path`` that is relative to *root_path* so the
    frontend can pass it directly to the ``/api/files/read`` endpoint.
    """
    if _base_path is None:
        _base_path = root_path

    structure = {"name": os.path.basename(root_path), "type": "directory", "children": []}
    
    try:
        for entry in os.scandir(root_path):
            rel = os.path.relpath(entry.path, _base_path)
            if entry.is_dir():
                child = get_file_structure(entry.path, _base_path)
                child["rel_path"] = rel
                structure["children"].append(child)
            else:
                structure["children"].append({
                    "name": entry.name,
                    "type": "file",
                    # Keep absolute path for internal use; also expose relative path for API calls
                    "path": entry.path,
                    "rel_path": rel,
                })
    except PermissionError:
        pass
        
    return structure

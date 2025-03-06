# Marks routes directory as Python package
# This allows the directory to be treated as a package, enabling the import of modules within it.

# Importing route modules from the current package
from . import db_routes, file_routes, ai_routes
from .EtlUpload import etl_upload_bp


# __all__ is a list of public objects of that module, as interpreted by import *
# It restricts what is imported when a client imports * from the package.
__all__ = ['db_routes', 'file_routes', 'ai_routes']

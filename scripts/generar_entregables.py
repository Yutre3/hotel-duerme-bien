"""Regenerar diagramas, interfaces, informe y portada del tema 6."""
from pathlib import Path
import runpy
BASE=Path(__file__).resolve().parent
for script in ['construir_modelado.py','construir_interfaces.py','construir_resumenes.py','construir_portada.py','construir_informe.py']:
    runpy.run_path(str(BASE/script),run_name='__main__')

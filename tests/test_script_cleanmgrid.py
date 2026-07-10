import pytest
from unittest.mock import patch
import os

from gridmarthe.scripts.cleanmgrid import read_rma, read_files_from_rma


def test_read_rma_extracts_filenames_correctly():

    # Prepare a fake rma content returned by gridmarthe.scripts.cleanmgrid.fred function
    fake_content = ("                = Asservissement Températ Drain Pompage => Inject.\n"
"                                    = Numéro de Zone d'initialisation géochimie PHREEQC\n"
"                                    = Liste de numéros de solutions chimiques\n"
"                                    = Altitude de Débordement\n"
"MOD82_Safran.seuil_r                = Hauteur du seuil à l'aval du tronçon de Rivière\n"
"MOD82_Safran.c_seu_r                = Facteur de la loi de débit du seuil de Rivière\n"
"=1.5                                = Exposant de la loi de débit du seuil de Rivière\n"
"                                    = Paramètres des engrais organiques\n"
"                                    = Paramètres des résidus culturaux après récolte\n"
"                                    = Paramètres de nitrif. et minéralisation du sol\n"
"                                    = Concentration maximale injectable\n"
    )

    # Inject a fake fread function inside read_rma
    with patch('gridmarthe.scripts.cleanmgrid.fread', return_value=fake_content):

        result = read_rma("dummy_path.rma")

        # Test read_rma on fake content
        assert result == ["MOD82_Safran.seuil_r", "MOD82_Safran.c_seu_r", "1.5"]


def test_read_files_from_rma_with_bare_filename(tmp_path, monkeypatch):
    """Regression test for issue #17: FileNotFoundError when calling read_files_from_rma with a relative path.

    When a .rma file is passed as a bare filename (no directory component), the function
    should correctly resolve the associated .layer file without raising FileNotFoundError.
    """
    # Create temporary .rma and .layer files
    rma_content = (
        "test.permh = PERMEAB\n"
        "test.layer = LAYERS\n"
    )
    layer_content = (
        "1=Nombre de couches\n"
        "Cou= 1;\n"
        "2=Nombre de gigognes\n"
    )

    rma_file = tmp_path / "myproject.rma"
    layer_file = tmp_path / "test.layer"

    rma_file.write_text(rma_content, encoding='ISO-8859-1')
    layer_file.write_text(layer_content, encoding='ISO-8859-1')

    # Change to the temporary directory so we can use a bare filename
    original_cwd = os.getcwd()
    monkeypatch.chdir(tmp_path)

    try:
        # This should NOT raise FileNotFoundError
        files, layers, ngrid = read_files_from_rma("myproject.rma")

        # Verify basic structure of returned data
        assert isinstance(files, list)
        assert isinstance(layers, list)
        assert ngrid is not None
    finally:
        monkeypatch.chdir(original_cwd)
import pytest
from unittest.mock import patch

from gridmarthe.scripts.cleanmgrid import read_rma


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
"""
Objets grilles de Marthe
"""
import re
import numpy as np
import pandas as pd
import gdal
import osr


def _replace(xstr):
    """
    Replace string
    """
    return re.sub('[0-9]-[1-9][0-9]', 'E-10', xstr)


def array2raster(
        newRasterfn,
        rasterOrigin,
        pixelWidth,
        pixelHeight,
        array,
        epsg
):
    """
    Convert an array to raster

    Parameters
    ----------
    newRasterfn : str
    rasterOrigin : tuple
        Raster origin (West, North) in meter
    pixelWidth : int
    pixelHeight : int
        Always negative
    array : numpy.array
        North to South orientation
    epsg : str or int
    """
    cols = array.shape[1]
    rows = array.shape[0]
    origin_x = rasterOrigin[0]
    origin_y = rasterOrigin[1]
    assert pixelHeight < 0

    driver = gdal.GetDriverByName('GTiff')
    out_raster = driver.Create(
        newRasterfn, cols, rows, 1, gdal.GDT_Float32
    )
    out_raster.SetGeoTransform(
        (origin_x, pixelWidth, 0, origin_y, 0, pixelHeight)
    )
    outband = out_raster.GetRasterBand(1)
    outband.WriteArray(array)
    out_raster_srs = osr.SpatialReference()
    out_raster_srs.ImportFromEPSG(int(epsg))
    out_raster.SetProjection(out_raster_srs.ExportToWkt())
    outband.FlushCache()


def _avancer(fichier, field):
    """
    Move forward in file
    """
    for line in fichier:
        if field in line.strip():
            return line

class AbstractMartheGrille(object):
    """
    """
    def __init__(self):
        self.x, self.dx, self.y, self.dy = [], [], [], []

    def _get_axes(self, fichier):
        line = _avancer(fichier, 'Data')
        if line.startswith('[Constant_Data]'):
            _avancer(fichier, '[Num_Columns')
            next(fichier)
            self.x.append(np.array(
                list(map(float, next(fichier).strip().split()))))
            self.dx.append(np.array(list(
                map(float, next(fichier).strip().split()))))
            _avancer(fichier, '[Num_Rows')
            next(fichier)
            self.y.append(np.array(list(
                map(float, next(fichier).strip().split()))))
            self.dy.append(np.array(list(
                map(float, next(fichier).strip().split()))))
        elif line.startswith('[Data_Descript]'):
            _avancer(fichier, '[Data]')
            line = next(fichier)
            self.x.append(np.array(list(
                map(float, next(fichier).strip().split()[2:]))))
            line = next(fichier).strip().split()
            y, dy = [], []
            while int(line[0]) != 0:
                y.append(float(line[1]))
                dy.append(float(line[-1]))
                line = next(fichier).strip().split()
            self.y.append(np.array(y))
            self.dy.append(np.array(dy))
            self.dx.append(np.array(list(map(float, line[2:]))))

    def to_raster(self, filename, field, data, epsg, **kwargs):
        """
            Convertit un champs Marthe en raster.
            Créé des fichiers raster tif.
            Arguments :
                - filename : préfixe des fichiers de sortie (
                    filename_field_gigogne_couche.tif
                )
                - data : array grille Marthe
                - field : nom du champs (ex : PERMEAB)
                - epsg : EPSG de la projection
            kwargs : 
                - unit : unité du champ (défaut = 1)
                - scale : conversion axes grille en m (défaut = 1)
                - clip_gig : True si les bordures du gigogne sont déjà enlevés
                dans le tableau data
        """
        unit = kwargs.get('unit', 1)
        scale = kwargs.get('scale', 1)
        clip_gig = kwargs.get('clip_gig', False)
        num_gig = len(data)
        num_layer = data[0].shape[0] 
        for igig in range(num_gig):
            mask = np.ma.mask_or(data[igig] == -9999., data[igig] == 9999.)
            data[igig] = np.where(mask, data[igig], data[igig]*unit)
            pixelWidth = self.dx[igig][1]*scale
            pixelHeight = -self.dy[igig][1]*scale
            if igig == 0:
                rasterOrigin = (
                    self.x[igig][0]*scale - pixelWidth/2.,
                    self.y[igig][0]*scale - pixelHeight/2.
                )
            elif igig > 0:
                if not clip_gig:
                    data[igig] = data[igig][:, 1:-1, 1:-1]
                rasterOrigin = (
                    self.x[igig][1]*scale - pixelWidth/2.,
                    self.y[igig][1]*scale - pixelHeight/2.
                )
            for icou in range(num_layer):
                newRasterfn = '{0}_{1}_{2}_{3}.tif'.format(
                    filename, field, igig, icou + 1
                )
                array2raster(
                    newRasterfn, rasterOrigin, pixelWidth, pixelHeight,
                    data[igig][icou], epsg
                )

    def to_xyz(self, field, data, unit=1, **kwargs):
        """
            Convertit un champs Marthe en fichier xyz
            Créé des fichiers xyzvalues_field.txt
            Arguments :
                - data : array grille Marthe
                - field : nom du champs (ex : PERMEAB)
                - unit : unité du champ (défaut = 1)
                - (optionnel) columns : colonnes à sortir 
                (x, y, dx, dy, valeur, couche, ligne, colonne, gigogne)
        """
        cols = kwargs.get(
            'columns', [
                'x', 'y', 'dx', 'dy', 'column',
                'line', 'layer', 'gigogne', 'value'
                ])
        filename = kwargs.get(
            'filename', 'xyvalues_{0}.txt'.format(field)
        )
        num_gig = len(data)
        num_layer = data[0].shape[0] 
        dfgig = []
        for igig in range(num_gig):
            indices = np.indices(list(data[igig].shape)) + 1
            x, y = np.meshgrid(self.x[igig], self.y[igig])
            dx, dy = np.meshgrid(self.dx[igig], self.dy[igig])
            x = np.repeat(x[np.newaxis, ...], num_layer, axis=0)
            y = np.repeat(y[np.newaxis, ...], num_layer, axis=0)
            dx = np.repeat(dx[np.newaxis, ...], num_layer, axis=0)
            dy = np.repeat(dy[np.newaxis, ...], num_layer, axis=0)
            df = {
                'x': x.flatten(),
                'y': y.flatten(), 
                'dx': dx.flatten(),
                'dy': dy.flatten(),
                'value': data[0].flatten()*unit,
                'layer': indices[0].flatten(),
                'line': indices[1].flatten(),
                'column': indices[2].flatten()
            }
            df = pd.DataFrame(df)
            df['gigogne'] = igig
            dfgig.append(df)
        dfgig = pd.concat(dfgig, axis=0, ignore_index=True)
        dfgig[cols].to_csv(
            filename, index=None, sep=' '
        )


class Permh(AbstractMartheGrille):
    def __init__(self, permh, field='PERMEAB'):
        AbstractMartheGrille.__init__(self)
        self.permh = permh
        fichier = open(permh, 'r', encoding='ISO-8859-1')
        line = _avancer(fichier, 'Title')
        inum_gig, inum_layer = self._get_gig_lay(line)
        inum_gig_before = inum_gig
        self._get_axes(fichier)
        while line:
            line = _avancer(fichier, 'Title')
            if line:
                inum_gig, inum_layer = self._get_gig_lay(line)
                if inum_gig.strip() and inum_gig != inum_gig_before:
                    self._get_axes(fichier)
                    inum_gig_before = inum_gig
        self.num_layer = int(inum_layer)
        self.num_gig = 0
        if inum_gig.strip():
            self.num_gig = int(inum_gig)
        fichier.close()

    def _get_gig_lay(self, line):
        search = re.findall('[0-9]+', line[-60:])
        if len(search) == 1:
            search = ['0'] + search
        return search

    def get_field(self):
        data_gig = []
        with open(self.permh, 'r', encoding='ISO-8859-1') as fichier:
            data = []
            line = _avancer(fichier, 'Title')
            inum_gig, _ = self._get_gig_lay(line)
            inum_gig = int(inum_gig)
            inum_gig_before = inum_gig
            while line:
                if inum_gig != inum_gig_before:
                    data_gig.append(np.ma.masked_values(np.array(data), 9999.))
                    inum_gig_before = inum_gig
                    data = []
                line = _avancer(fichier, 'Data]')
                # Lit l'ensemble des couches
                data_layer = []
                if 'Constant' in line:
                    value = float(next(fichier).split('=')[1].strip())
                    data_layer = np.ones((len(self.y[inum_gig]),
                                          len(self.x[inum_gig])))*value
                else:
                    for _ in range(2):
                        line = next(fichier)
                    line = list(map(_replace, next(fichier).strip().split()))
                    while int(line[0]) != 0:
                        data_layer.append(list(map(float, line[2:-1])))
                        line = list(
                            map(_replace, next(fichier).strip().split())
                        )
                    data_layer = np.array(data_layer)
                data.append(data_layer)
                line = _avancer(fichier, 'Title')
                if line:
                    inum_gig, _ = self._get_gig_lay(line)
                    inum_gig = int(inum_gig)
        data_gig.append(np.ma.masked_values(np.array(data), 9999.))
        return data_gig

    def superimpose(self, dataset):
        """
        ! Fonctionne uniquement avec fichier .permh
        """
        outputs = []
        for data in dataset:
            # Boucle layer
            output = np.zeros((data.shape[1], data.shape[2]))
            for ilayer, layer in enumerate(data[::-1]):
                layer = np.where(layer == -9999., 0, layer)
                layer = np.where(layer == 9999., 0, layer)
                output = np.where(layer != 0, self.num_layer - ilayer, output)
                # output = np.where(layer != 0, ilayer + 1, output)
            outputs.append(output)
        return outputs

    def find_col_lig(self, x, y, data, scale=1):
        """
        ! Fonctionne uniquement avec fichier .permh
        return (ligne, colonne, gigogne)
        """
        # On calcule les lignes colonnes gigognes du maillage principal
        # (toujours vrai)
        lig, col, gig = 0, 0, 0
        epsilon = 0.001
        deltax = self.dx[0][1]*scale
        deltay = self.dy[0][1]*scale
        for icol, xcoord in enumerate(self.x[0]):
            if np.abs(xcoord*scale-x) <= (deltax/2. + epsilon):
                break
        for ilig, ycoord in enumerate(self.y[0]):
            if np.abs(ycoord*scale-y) <= (deltay/2. + epsilon):
                gig = 0
                lig = int(self.y[0].tolist().index(ycoord) + 1)
                col = int(self.x[0].tolist().index(xcoord) + 1)
                break
        # On teste si éventuellement ça tombe dans un gigogne
        if self.num_gig > 0:
            for igig, (xgig, ygig) in enumerate(zip(self.x[1:], self.y[1:])):
                deltax = self.dx[igig + 1][1]*scale
                deltay = self.dy[igig + 1][1]*scale
                maybe_in_gig = False
                for icol, xcoord in enumerate(xgig):
                    if np.abs(xcoord*scale-x) <= (deltax/2. + epsilon):
                        maybe_in_gig = True
                        break
                if maybe_in_gig:
                    for ilig, ycoord in enumerate(ygig):
                        if (
                                np.abs(ycoord*scale-y) <= (deltay/2. + epsilon)
                                and data[igig + 1][ilig, icol] != 0
                                and data[igig + 1][ilig, icol] != -9999
                        ):
                            gig = igig + 1
                            lig = ilig + 1
                            col = icol + 1
                            break
        return lig, col, gig

class OutFile(AbstractMartheGrille):
    def __init__(self, filename):
        AbstractMartheGrille.__init__(self)
        self.filename = filename
        self.x, self.dx, self.y, self.dy = [], [], [], []
        with open(filename, 'r', encoding='ISO-8859-1') as fichier:
            self.num_gig = int(_avancer(fichier, 'Max_NestG').split("=")[-1])
            self.num_layer = int(_avancer(fichier, 'Max_Layer').split("=")[-1])
            for inum_gig in range(self.num_gig + 1):
                _ = _avancer(fichier, 'Nest_grid={0}'.format(inum_gig))
                self._get_axes(fichier)

    def _get_record(self, fichier, field, elem_number):
        # Pour un pas de temps et un gigogne
        # [couche, Y, X]
        # Initialise le nombre de gigognes
        data = []
        for inum_gig in range(self.num_gig + 1):
            data.append(np.ones((self.num_layer, len(self.y[inum_gig]),
                                 len(self.x[inum_gig]))))
        # data = [[] for inum_gig in range(self.num_gig + 1)]
        # Boucle sur les couches puis les gigognes
        for _ in range((self.num_gig + 1) * self.num_layer):
            line = _avancer(fichier, 'Field={0}'.format(field))
            line = _avancer(fichier, 'Elem_Number={0}'.format(elem_number))
            inum_lay = int(_avancer(fichier, 'Layer').split('=')[-1]) - 1
            inum_gig = int(_avancer(fichier, 'Nest_grid').split('=')[-1])
            line = _avancer(fichier, 'Data]')
            if 'Constant' in line:
                value = float(next(fichier).split('=')[1].strip())
                data_layer = np.ones((len(self.y[inum_gig]),
                                      len(self.x[inum_gig])))*value
            else:
                for _ in range(2):
                    line = next(fichier)
                # Lit l'ensemble des couches
                line = list(map(_replace, next(fichier).strip().split()))
                data_layer = []
                while int(line[0]) != 0:
                    data_layer.append(list(map(float, line[2:-1])))
                    line = list(map(_replace, next(fichier).strip().split()))
                data_layer = np.array(data_layer)
            data[inum_gig][inum_lay, :, :] = data_layer
        # for inum_gig in range(self.num_gig + 1):
        #    data[inum_gig] = np.ma.masked_values(np.vstack(data[inum_gig]),
        #                                         9999)
        return data

    def read_record(self, record, field, elem_number=0):
        """
        Read just one record for the selected field. Shape is [gigogne, couche,
        Y, X].
        """
        with open(self.filename, 'r', encoding='ISO-8859-1') as fichier:
            # Avance jusqu'au bon time step
            line = _avancer(fichier,  '{0};'.format(record))
            if line:
                return self._get_record(fichier, field, elem_number)
                # return np.ma.masked_values(np.squeeze(np.array(
                #  self._get_record(fichier, field, elem_number))), 9999.)

    def read_field(self, field, elem_number=0):
        """
        Read all the field.
        """
        time_data = [[] for inum_gig in range(self.num_gig + 1)]
        with open(self.filename, 'r', encoding='ISO-8859-1') as fichier:
            line = _avancer(fichier, 'Title')
            while line:
                text = 'Title.*{0} '.format(field)
                if elem_number > 0:
                    text = 'Title.*{0}.*_{1}'.format(field, elem_number)
                if re.search(text, line):
                    data = self._get_record(fichier, field, elem_number)
                    for inum_gig in range(self.num_gig + 1):
                        time_data[inum_gig].append(data[inum_gig])
                line = _avancer(fichier, 'Title')
        return time_data

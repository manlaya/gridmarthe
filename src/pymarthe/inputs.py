import pandas as pd

def build_entete(yentete):
    lines = [yentete]
    lines.append(
        ' #<V7.8># --- Fin du texte libre --- ;'
        ' Ne pas modifier/retirer cette ligne '
    )
    return lines

def build_line_collig(gig, champ, col, lig, cou, name=''):
    gig = int(gig)
    col = int(col)
    lig = int(lig)
    cou = int(cou)
    if gig == 0:
        gig = ''
    return ("{0:>2s}/{1:<13s}/HISTO/   ="
        "   /MAIL:C={2:7d}L={3:7d}P={4:7d};{5}".format(
            str(gig), champ, col, lig, cou, name))

def build_line_xy(gig, champ, x, y, cou, name=''):
    gig = int(gig)
    cou = int(cou)
    if gig == 0:
        gig = ''
    return ("{0:>2s}/{1:<13s}/HISTO/   ="
        "   /XCOO:X={2:7.0f}Y={3:7.0f}P={4:7d};{5}".format(
            str(gig), champ, x, y, cou, name))

def build_histo_collig(df):
    lines = []
    for row in df:
        if row['GIG'] == 0:
            row['GIG'] = ''
        lines.append(
            build_line_collig(row['GIG'], row['CHAMPS'], row['COL'],
                    row['LIG'], row['COU'], row['NAME'])
                    )
    return lines

def set_file_histo_collig(filename, yentete, df):
    lines = [] 
    lines.extend(build_entete(yentete))
    lines.extend(build_histo_collig(df))
    with open(filename, 'w', encoding='cp1252') as f:
        f.write('\n'.join(lines))

def build_timestep_line(var, typ, **kwargs):
    """
    Edit a line of a Marthe time step file 

    Parameters
    ----------
    var : str
        Variable to edit. Possible values are all the variable of
        MARTHE
    typ : str
        Geometry. Possible values are 
            'EDITION', 'COUCHE', 'ZONE_GEO', 'ZONEP', 'MAILLE', 'TRONCON', 'LIST_MAIL'
    
    Return
    ------
    line : str
        Line formatted for the MARTHE file
    """
    doptions = {
        'GRILLE':'N: {N}',
        'LIST_MAIL':'N: {N}',
        'COUCHE':'C={C:>7d}V={V:>10};',
        'ZONE_GEO':'Z={Z:>7d}V={V:>10};',
        'MAILLE':'C={C:>7d}L={L:>7d}P={P:>7d}V={V:>10};',
        'FICH_METE':'N={N:>7}',
        'ZONEP':'Z={Z:>7}V={V:>10};',
        'EDITION':'I={I:>2};',
        'FICHIER':'N: {N:>7}',
        'TRONCON':'A={A:>7}T={T:>7}V={V:>10};',
    }
    deditions = {
        'VITESSE':'I={I:>2} [C={C:>7d};L={L:>7d};P={P:>7d};Gig={Gig:>2d}]',
        'FLUX_INFILTR':'I={I:>2};Z={Z:>2};C={C:>2};',
        'DEBIT':'*={star:>2};V={I:>2};L={L:>2};S={F:>2};Z={Z:>2};',
        'DEBIT_RIVI':'I={I:>2};L={L:>2};F={F:>2};B={B:>2};',
        'RUISSEL':'I={I:>2};Z={Z:>2};C={C:>2};',
        'RECHARGE':'I={I:>2};Z={Z:>2};C={C:>2};',
        'FLUX_PLUV':'I={I:>2};Z={Z:>2};C={C:>2};',
        'PROFOND_NAPP':'I={I:>2};Z={S:>2};',
        'HAUTEU_RIVI':'I={I:>2};P={P:>2};',
        'SATUR_NAQ':'I={I:>2};R={P:>2};',
    }
    list_mail_opt = ['<Somm_Mail>', '<Keep_9999>', '<X_Y_V>',
                    '<Moyenne>', '<Init_a_Zero>', '<X_Y_C>', '<X_Y_Z>']
    yvar_type = '/{0}/{1}'.format(var, typ)
    yfile = kwargs.get('File', '')
    if yfile:
        yfile =' File= {0}'.format(kwargs['File'])
    ycolumn = kwargs.get('column', '')
    if ycolumn and int(ycolumn) == 1:
        ycolumn = ''
    elif ycolumn and int(ycolumn) > 1:
        ycolumn = '; Col={0}'.format(ycolumn)
    if typ == 'EDITION':
        opts = ['star', 'V', 'L', 'S', 'Z', 'I', 'F', 'B', 'C', 'P', 'Gig']
        dtemp = {opt:kwargs.get(opt, ' ') for opt in opts}
        if var in deditions.keys():
            dopt = deditions[var]
        else:
            dopt = doptions[typ]
        yoptions = dopt.format(**dtemp)
        yoptions = '{0}{1}'.format(yoptions, yfile)
    else:
        yoptions = doptions[typ].format(**kwargs)
        if typ == 'LIST_MAIL':
            opts = kwargs.get('list_mail_opts', [])
            opts = [opt for opt in opts if opt in list_mail_opt]
            yoptions = '{0} {1}'.format(yoptions, ' '.join(opts))
        if typ in ['COUCHE', 'ZONE_GEO', 'ZONEP', 'MAILLE', 'TRONCON']:
            yoptions = '{0}{1}{2}'.format(yoptions, yfile, ycolumn)
    return '  {0:25}{1}'.format(yvar_type, yoptions)

def build_init_timestep(date_perm, length, dactions):
    """
    Build the lines for initialization time step of MARTHE pastp file

    Parameters
    ----------
    date_perm : str
        Format %Y/%m/%d
    length : int
    dactions : dict

    Return
    ------
    lines : list of str
    """
    ystart_sim = ' *** Début de la simulation    à la date :{fdate}; ***'
    lines = [ystart_sim.format(fdate=' {0:{1}} '.format(date_perm, length))]
    actions = dactions.get(date_perm, [''])
    for action in actions:
        lines.append(action)
    lines.append('  /*****/***** Fin de ce pas')
    return lines

def build_pastp(dates_trans, length, dactions):
    """
    Build all lines of a pastp file

    Parameters
    ----------
    dates_trans : list of str
    length : int
    dactions : dict

    Return
    ------
    list of str 
    """
    lines = []
    ystart_step = ' *** Le pas :{fpas:5d}: se termine à la date :{fdate}; ***'
    for i, date in enumerate(dates_trans):
        lines.append(ystart_step.format(
            fpas=i+1, fdate=' {0:{1}} '.format(date, length)))
        actions = dactions.get(date, [])
        for action in actions:
            if action:
                lines.append(action)
        lines.append('  /*****/***** Fin de ce pas')
    return lines

def set_file_pastp(filename, yentete, date_perm, dates_trans, dactions={}):
    """
    Build a pastp file

    Parameters
    ----------
    filename : str
        name of the pastp file
    yentete : str
        first lines of the pastp file
    date_perm : str
    date_trans : list of str
    dactions : dict
        keys are dates in date_perm and date_trans
    """
    length = max([len(str(date_perm))] + [len(str(date)) for date in dates_trans])
    lines = [] 
    lines.extend(build_entete(yentete))
    lines.extend(build_init_timestep(date_perm, length, dactions))
    lines.extend(build_pastp(dates_trans, length, dactions))
    lines.append(' ***        :     : Fin de la simulation :            ; ***')
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

def set_edit_file(filename, entete, start, end, dates):
    """
    Build an editions file

    Parameters
    ----------
    filename : str
        name of the pastp file
    entete : str
        first lines of the pastp file
    start : datetime.datetime
    end : datetime.datetime
    dates : list of datetime.datetime
        date for which an edition will be set
    """
    with open(filename, 'w') as f:
        f.write('{0}\n'.format(entete))
        for date in pd.date_range(start, end):
            if date in dates:
                f.write('1\t{0}\n'.format(date.strftime("%Y/%m/%d")))
            else:
                f.write('0\t{0}\n'.format(date.strftime("%Y/%m/%d")))

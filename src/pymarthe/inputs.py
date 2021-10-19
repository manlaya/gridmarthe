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


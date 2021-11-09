MODULE MODGRIDMARTHE

INTEGER :: LEC                      ! Unité de lecture
INTEGER :: IOUCON                   ! Ecriture sur la console (<0 non, 0 = erreurs, >0 = tout)
INTEGER :: NLIG, NKOL               ! Nombre maximum de ligne et de colonne / en retour nbre de ligne et de colonne
INTEGER :: NTOT                     ! Nombre maxi de places dans le tableau FONC()
                                    ! NTOT  = Nombre de points = NKOL * NLIG
                                    ! N.B. : Si NTOT = 0 => On ne lit pas les points
                                    !        mais seulement les coordonnées (Il n'y a rien dans FONC)
INTEGER :: INVERS                   ! INVERS : 0 = La première ligne lue est rangée en premier (Modèles)
                                    !      : 1 = Inversion la première ligne lue est rangée en dernier
                                    !            et YLIG est inversé aussi (logiciels d'interpolation)
INTEGER :: LIRE_DXDY                ! LIRE_DXDY : 0 = On ne veut pas lire de DX() et DY()
                                    !                (On les saute s'ils existent)
                                    !           : 1 = On veut lire les DX() et DY() (s'ils existent)
CHARACTER (LEN=132) :: TITSEM       ! TITSEM = Dernier titre lu pour la Grille (len=132)
INTEGER :: LU_DXDY                  ! LU_DXDY : 0 = On n'a pas lu de DX et DY
                                    !         : 1 = On a lu des DX et DY
INTEGER :: LU_XY                    ! LU_XY   : 0 = On n'a pas lu de X() et Y() : Par ex lecture en format libre
                                    !         : 1 = On a lu des X() et Y()
REAL, DIMENSION(999)              :: XCOL ! XCOL  = Tableau des abscisses (si LU_XY > 0)
REAL, DIMENSION(999)              :: YLIG ! YLIG  = Tableau des ordonnées (si LU_XY > 0)
REAL, DIMENSION(999)              :: DXLU ! DXLU  = DX lus si LU_DXDY > 0
REAL, DIMENSION(999)              :: DYLU ! DYLU  = DY lus si LU_DXDY > 0
REAL    :: X0                       ! X0    = Abscisse du cote ouest de la colonne n°1    (si LU_XY > 0)
REAL    :: Y0                       ! Y0    = Ordonnée du    bas     de la ligne   n°NLIG (si LU_XY > 0)
REAL, DIMENSION(999*999)              :: FONC  ! FONC  = Tableau des valeurs lues
INTEGER :: IERLEC                   ! IERLEC =  0 Si normal
                                    ! IERLEC = -1 Si erreur dans les nombres de Ligne, Colonne ou Panneau
                                    ! IERLEC =  1 Si erreur de lecture         (Maille NUMERR)
                                    ! IERLEC =  2 Si fin de fichier rencontrée (Maille NUMERR)
                                    ! IERLEC =  3 Si absolument incorrect/dimensions permises ou précédentes
INTEGER    :: IANALY                ! IANALY : 0 = Lecture normale
                                    !        : 1 = Prélecture rapide (pour analyser les dimensions etc)
                                    !              FONC(), XCOL(), YLIG() ne sont pas valorisés
                                    !              (N.B. Si binaire => Pas plus rapide)
CHARACTER (LEN=132) :: TYP_DON      ! TYP_DON  = Type de donnée (len=13)
CHARACTER (LEN=7)   :: TYP_DON3     ! TYP_DON3 = Complément du type de donnée (len=7)
CHARACTER (LEN=132) :: LIBCHIM      ! LIBCHIM  = Libellé complémentaire (nom de l'Élément Chimique) (len=80)
INTEGER    :: N_ELEMCH              ! N_ELEMCH = Numéro associé au type de donnée (élément Chimique)
INTEGER    :: ISTEP                 ! ISTEP    = Numéro du pas de temps (-9999 si pas lu)
INTEGER    :: N_COUCH               ! N_COUCH  = Numéro de la Couche
INTEGER    :: NU_ZOO                ! NU_ZOO   = Numéro du Gigogne (0 = Main)
INTEGER    :: NUMERR                ! Maille NUMERR
INTEGER    :: NCOUC_MX              ! NCOUC_MX = Nombre maxi de Couches
INTEGER    :: NU_ZOOMX              ! NU_ZOOMX = Nombre maxi de Gigognes
REAL       :: DATE                  ! DATE     = Date associée à la Grille

CONTAINS

SUBROUTINE SCAN_NU_ZOOMX(XFILE, KNU_ZOOMX)
!
IMPLICIT NONE
!
CHARACTER (LEN=132), INTENT(IN) :: XFILE
INTEGER, INTENT(OUT) :: KNU_ZOOMX
!
INTEGER :: INUMSTEP
!
LIRE_DXDY = 0
IANALY = 1
INVERS = 0
IOUCON = -1
LEC = 10
IERLEC = 0
N_COUCH = 0
NU_ZOO = 0
INUMSTEP = 0
!
OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
!
CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
          , IOUCON, LEC, IERLEC, NUMERR, NTOT &
          , IANALY &
          , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
          , DATE, LIBCHIM &
          , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
!
KNU_ZOOMX = NU_ZOOMX
!
CLOSE(10)
!
END SUBROUTINE SCAN_NU_ZOOMX
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! =============================================================================!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE SCAN_DIM(XFILE, XTYP_DON, KNU_ZOOMX, KDIMEN, KNBSTEP)
!
IMPLICIT NONE
!
CHARACTER (LEN=132), INTENT(IN)               :: XFILE, XTYP_DON
INTEGER, INTENT(IN)                           :: KNU_ZOOMX
INTEGER, DIMENSION(KNU_ZOOMX + 1, 3), INTENT(OUT) :: KDIMEN
INTEGER, INTENT(OUT)                          :: KNBSTEP
!
INTEGER :: ISTEP_TEMP
!
LIRE_DXDY = 0
IANALY = 1
INVERS = 0
IOUCON = -1
LEC = 10
IERLEC = 0
N_COUCH = 0
NU_ZOO = 0
KNBSTEP = 0
!
ISTEP_TEMP = -1
!
OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
!
DO WHILE (IERLEC == 0)
    CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
              , IOUCON, LEC, IERLEC, NUMERR, NTOT &
              , IANALY &
              , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
              , DATE, LIBCHIM &
              , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
    IF (IERLEC == 0 .AND. TRIM(TYP_DON) == TRIM(XTYP_DON)) THEN
        KDIMEN(NU_ZOO + 1, 1) = NKOL
        KDIMEN(NU_ZOO + 1, 2) = NLIG
        KDIMEN(NU_ZOO + 1, 3) = NCOUC_MX
        IF (ISTEP /= ISTEP_TEMP) THEN
            KNBSTEP = KNBSTEP + 1
            ISTEP_TEMP = ISTEP
        ENDIF
    ENDIF
ENDDO
!
CLOSE(LEC)
!
END SUBROUTINE SCAN_DIM
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! =============================================================================!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE READ_GRID(XFILE, XTYP_DON, KNBSTEP, KNBTOT, KNU_ZOOMX, PVAR, PDATES, KSTEPS, PXCOL, PYLIG, PDXLU, PDYLU)
!
IMPLICIT NONE
!
CHARACTER (LEN=132), INTENT(IN)               :: XFILE, XTYP_DON
INTEGER, INTENT(IN)                           :: KNBTOT
INTEGER, INTENT(IN)                           :: KNBSTEP
INTEGER, INTENT(IN)                           :: KNU_ZOOMX
INTEGER, DIMENSION(KNBSTEP), INTENT(OUT)      :: KSTEPS
REAL(KIND=4), DIMENSION(KNBSTEP), INTENT(OUT) :: PDATES
REAL(KIND=4), DIMENSION(KNBSTEP, KNBTOT), INTENT(OUT) :: PVAR
REAL(KIND=4), DIMENSION(KNU_ZOOMX + 1, 999), INTENT(OUT) :: PXCOL, PYLIG, PDXLU, PDYLU
!
INTEGER    :: ISTEPINC, ISTEP_TEMP, INTOT_TEMP
!
LIRE_DXDY = 1
IANALY = 0
INVERS = 0
IOUCON = -1
LEC = 10
IERLEC = 0
!
N_COUCH = 0
NU_ZOO = 0
ISTEP = 0
!
PVAR(:,:) = 1e+20
PXCOL(:, :) = 1e+20
PYLIG(:, :) = 1e+20
PDXLU(:, :) = 1e+20
PDYLU(:, :) = 1e+20
!
ISTEPINC = 0
ISTEP_TEMP = -1
INTOT_TEMP = 1
!
OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
!
DO WHILE (IERLEC == 0)
    NLIG = 999.
    NKOL = 999.
    NTOT = NLIG * NKOL
    NCOUC_MX = 99.
    NU_ZOOMX = 99.
    CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
              , IOUCON, LEC, IERLEC, NUMERR, NTOT &
              , IANALY &
              , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
              , DATE, LIBCHIM &
              , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
    IF (IERLEC == 0 .AND. TRIM(TYP_DON) == TRIM(XTYP_DON)) THEN
        IF (ISTEP /= ISTEP_TEMP) THEN
            ISTEPINC = ISTEPINC + 1
            ISTEP_TEMP = ISTEP
            INTOT_TEMP = 1
            KSTEPS(ISTEPINC) = ISTEP
            PDATES(ISTEPINC) = DATE
        ENDIF
        IF (ISTEPINC == 1 .AND. N_COUCH == 1) THEN
            PXCOL(NU_ZOO + 1, :NKOL) = XCOL(:NKOL)
            PYLIG(NU_ZOO + 1, :NLIG) = YLIG(:NLIG)
            PDXLU(NU_ZOO + 1, :NKOL) = DXLU(:NKOL)
            PDYLU(NU_ZOO + 1, :NLIG) = DYLU(:NLIG)
        ENDIF
        PVAR(ISTEPINC, INTOT_TEMP:INTOT_TEMP + NTOT -1) = FONC(:NTOT)
        INTOT_TEMP = INTOT_TEMP + NTOT
    ENDIF
ENDDO
!
CLOSE(LEC)
!
END SUBROUTINE READ_GRID
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! =============================================================================!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
SUBROUTINE READ_GRID_SHALLOW(XFILE, XTYP_DON, KNBSTEP, KN_COUCHMX, KNBTOT, &
    KNU_ZOOMX, PVAR, PDATES, KSTEPS, PXCOL, PYLIG, PDXLU, PDYLU)
!
IMPLICIT NONE
!
CHARACTER (LEN=132), INTENT(IN)               :: XFILE, XTYP_DON
INTEGER, INTENT(IN)                           :: KNBTOT
INTEGER, INTENT(IN)                           :: KNBSTEP
INTEGER, INTENT(IN)                           :: KN_COUCHMX
INTEGER, INTENT(IN)                           :: KNU_ZOOMX
INTEGER, DIMENSION(KNBSTEP), INTENT(OUT)      :: KSTEPS
REAL(KIND=4), DIMENSION(KNBSTEP), INTENT(OUT) :: PDATES
REAL(KIND=4), DIMENSION(KNBSTEP, KNU_ZOOMX + 1, KNBTOT), INTENT(OUT) :: PVAR
REAL(KIND=4), DIMENSION(KNU_ZOOMX + 1, 999), INTENT(OUT) :: PXCOL, PYLIG, PDXLU, PDYLU
!
!
INTEGER    :: ISTEPINC, ISTEP_TEMP, INTOT_TEMP, N_COUCH2
REAL(KIND=4), DIMENSION(KNBSTEP, KNU_ZOOMX + 1, KN_COUCHMX, KNBTOT) :: ZTEMP
INTEGER, DIMENSION(KNU_ZOOMX + 1, 3) :: KDIMEN
!
!
LIRE_DXDY = 1
IANALY = 0
INVERS = 0
IOUCON = -1
LEC = 10
IERLEC = 0
!
N_COUCH = 0
NU_ZOO = 0
ISTEP = 0
!
ZTEMP(:,:,:,:) = 9999.
PXCOL(:, :) = 1e+20
PYLIG(:, :) = 1e+20
PDXLU(:, :) = 1e+20
PDYLU(:, :) = 1e+20
!
ISTEPINC = 0
ISTEP_TEMP = -1
INTOT_TEMP = 1
!
OPEN(UNIT=LEC, FILE=TRIM(XFILE), FORM='formatted', ACTION='read')
!
DO WHILE (IERLEC == 0)
    NLIG = 999.
    NKOL = 999.
    NTOT = NLIG * NKOL
    NCOUC_MX = 99.
    NU_ZOOMX = 99.
    CALL LECSEM_3(X0, Y0, FONC, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
              , IOUCON, LEC, IERLEC, NUMERR, NTOT &
              , IANALY &
              , TYP_DON, TYP_DON3, N_ELEMCH, ISTEP, N_COUCH, NCOUC_MX, NU_ZOO, NU_ZOOMX &
              , DATE, LIBCHIM &
              , LIRE_DXDY, LU_DXDY, LU_XY, DXLU, DYLU)
    IF (IERLEC == 0 .AND. TRIM(TYP_DON) == TRIM(XTYP_DON)) THEN
        KDIMEN(NU_ZOO + 1, 1) = NKOL
        KDIMEN(NU_ZOO + 1, 2) = NLIG
        KDIMEN(NU_ZOO + 1, 3) = NCOUC_MX
        IF (ISTEP /= ISTEP_TEMP) THEN
            ISTEPINC = ISTEPINC + 1
            ISTEP_TEMP = ISTEP
            INTOT_TEMP = 1
            KSTEPS(ISTEPINC) = ISTEP
            PDATES(ISTEPINC) = DATE
        ENDIF
        IF (ISTEPINC == 1 .AND. N_COUCH == 1) THEN
            PXCOL(NU_ZOO + 1, :NKOL) = XCOL(:NKOL)
            PYLIG(NU_ZOO + 1, :NLIG) = YLIG(:NLIG)
            PDXLU(NU_ZOO + 1, :NKOL) = DXLU(:NKOL)
            PDYLU(NU_ZOO + 1, :NLIG) = DYLU(:NLIG)
        ENDIF
        ZTEMP(ISTEPINC, NU_ZOO + 1, N_COUCH, :NTOT) = FONC(:NTOT)
    ENDIF
ENDDO
!
CLOSE(LEC)
!
PVAR(:,:,:) = 9999.
DO NU_ZOO = 1, NU_ZOOMX + 1
    NTOT = KDIMEN(NU_ZOO, 1)*KDIMEN(NU_ZOO, 2)
    DO N_COUCH = 1, KN_COUCHMX
        WHERE (ZTEMP(:, NU_ZOO, N_COUCH, :NTOT) /= 9999.)
            PVAR(:, NU_ZOO, :NTOT) = ZTEMP(:, NU_ZOO, N_COUCH, :NTOT)
        END WHERE
        DO N_COUCH2 = N_COUCH, KN_COUCHMX
            WHERE (PVAR(:, NU_ZOO, :NTOT) /= 9999.) ZTEMP(:, NU_ZOO, N_COUCH2, :NTOT) = 9999.
        ENDDO
    ENDDO
ENDDO
!
WHERE(PVAR(:,:,:) == 9999.) PVAR(:,:,:) = 1e+20
!
END SUBROUTINE READ_GRID_SHALLOW
!
END MODULE MODGRIDMARTHE
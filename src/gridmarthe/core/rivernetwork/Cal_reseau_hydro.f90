      SUBROUTINE Cal_reseau_hydro(FICH_PRESENCE, FICH_DIRECT, ITYP_DIRECT, SURF_RIV, NPERIO_TRONC, NBRE_VOIS_STATION, &
         FICH_ENT_EXIS_RIV, FICH_ENT_SURF_AMO, FICH_X_Y_SURF, FICH_COL_LIG_SOUS_BV, FICH_NUMER_SOUS_BV, &
         FICH_SOR_EXIS_RIV, FICH_SOR_SURF_AMO, FICH_ARBRE, FICH_AFFLU, FICH_TRONC, FICH_HISTORIQ, FICH_SOUS_BASSIN, FICH_LISTING)
!=======================================================================
!   ******************
!   *Cal_reseau_hydro*                 BRGM     B.P. 36009
!   ******************                 45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      Calcul du R�seau Hydro � partir des Directions de Drainage
!      Routines utilis�es :
!=======================================================================
!      * Lec_Param_Cal_Reseau
!      * Convert_Direct_Drain
!      * Definit_Sous_Bassins
!      * Direct_Drain_Mai_Ava
!      * Mai_Ava_Strahl_Surf_Drai
!      * Mai_Exu_Surf_Drai
!      * Dir_Drain_LigCol_Ava
!      * Verif_Surf_Stat_Hydro
!=======================================================================
      IMPLICIT NONE
!     ============
!      Interfaces
!     ============
      ! INTERFACE
      !   FUNCTION Dossier_et_Nom(NOM_FICH_PUR)
      !    CHARACTER (LEN=1024) :: Dossier_et_Nom
      !    CHARACTER (LEN=*), INTENT(IN) :: NOM_FICH_PUR
      !   END FUNCTION Dossier_et_Nom
      ! END INTERFACE
      INTEGER, PARAMETER :: NB_AMONT_MAX = 7
      REAL, DIMENSION(:), ALLOCATABLE :: XCOL, DX_LU
      REAL, DIMENSION(:), ALLOCATABLE :: YLIG, DY_LU
      REAL, DIMENSION(:), ALLOCATABLE :: HYDRO,PRESEN, ORIENT, SURF_DRA
      INTEGER, DIMENSION(:), ALLOCATABLE :: IORD,NMAI_AVAL
      INTEGER, DIMENSION(:), ALLOCATABLE :: NUM_SEMIS, NRIVAVA ,NRIAFFL, NRITRON &
                                          , IANALY
      INTEGER, DIMENSION(: , :), ALLOCATABLE :: NRIVAMO
      INTEGER, DIMENSION(:), ALLOCATABLE :: LISTSOUR ,NBR_TRONC_DS_AFFLU
      CHARACTER (LEN=132) :: TITSEM
      ! CHARACTER (LEN=401) :: FICH_401
      CHARACTER (LEN=20) :: CHARA20
      CHARACTER (LEN=12) :: CHARA12_SURF
      CHARACTER (LEN=13) :: CODTIT_13
      CHARACTER (LEN=80) :: NATUR_FICH
!     ======= Lecture
      ! CHARACTER (LEN=80) :: FICH_PARAM
      CHARACTER (LEN=132), INTENT(IN) :: FICH_PRESENCE &
                          , FICH_DIRECT &
                          , FICH_ENT_EXIS_RIV &
                          , FICH_ENT_SURF_AMO &
                          , FICH_X_Y_SURF &
                          , FICH_COL_LIG_SOUS_BV &
                          , FICH_NUMER_SOUS_BV &
                          , FICH_SOR_EXIS_RIV &
                          , FICH_SOR_SURF_AMO &
                          , FICH_ARBRE &
                          , FICH_AFFLU &
                          , FICH_TRONC &
                          , FICH_HISTORIQ &
                          , FICH_SOUS_BASSIN &
                          , FICH_LISTING


      CHARACTER (LEN=80) :: TITGEN, LABAUX
      ! CHARACTER (LEN=15) :: DATE_RELEASE
      ! CHARACTER (LEN=20) :: NAMEPG
      ! CHARACTER (LEN=6)  :: NRELEA
      ! COMMON /NVERSI/NAMEPG, NRELEA
      ! CHARACTER (LEN=80), DIMENSION(25) :: WINT_BUFF
      ! COMMON/WINT_WRITE/WINT_BUFF
      ! CHARACTER (LEN=3)   :: EXTEN_PROJ
      ! CHARACTER (LEN=50)  :: Nom_Logiciel
      ! CHARACTER (LEN=10)  :: Code_Fich_Recent
      ! CHARACTER (LEN=150) :: Fonction_Logiciel
      ! CHARACTER (LEN=40)  :: LABGEN
      CHARACTER (LEN=132)  :: FICH_SOR_RIV_BLN
      CHARACTER (LEN=7)   :: CHAR7
      REAL    :: X0, Y0, SOM_SURF_EXUT
      INTEGER, INTENT(IN) :: ITYP_DIRECT, NPERIO_TRONC, NBRE_VOIS_STATION
      REAL, INTENT(IN) :: SURF_RIV
!     =======
      INTEGER :: LEC, IOU, INPCON, IOUCON, IOUCON_NUL, LISTIN, INVERS, INVY, NTOT, NLIG, NKOL &
                ,IEREDI, IEROLD, IERNEW, IERLEC, IERRAUX, IER, NUMERR, LIRE_DXDY &
                ,LU_DXDY, LU_XY &
                ,NB_NON_DEFINIS, NB_HORS_DOMAIN, IOUMAI, KOL, LIG, KOLVOIS, LIGVOIS &
                ,IANGL, NVOIS, NUMAFL, KONT, NBMRIV, N, K, IR,IRAVA, KONSOUR, ISOUR &
                ,NBAMONT, NUMAFL_AVA, IEDIT_RESEAU, IEX_SURF, KONT_EXUT !, ISTOP, No_New_FILE
!     =======
!      Début
!     =======
      INPCON = 5
      IOUCON = 6
      IOUCON_NUL = 0
      LEC    = 1
      IOU    = 3
      IOUMAI = 3
      LISTIN = 7
      INVERS = 0
      INVY   = 0
      ! Nom_Logiciel = "Cal_Reseau_Hydro"
      ! NAMEPG = Nom_Logiciel
! #ifdef RIVI_VERSION
!       NRELEA = RIVI_VERSION
! #else
!       NRELEA = "vX.XX "
! #endif
! !
! #ifdef RIVI_DATE_RELEASE
!       DATE_RELEASE = RIVI_DATE_RELEASE
! #else
!       DATE_RELEASE = "YYYY-MM-DD"
! #endif
!     =======================================
!      Ouverture du projet et de Winteracter
!     =======================================
!       FICH_PARAM = " "
!       EXTEN_PROJ = "rhy"
!       Code_Fich_Recent = "R�hyd"
!       Fonction_Logiciel = "Calcul du r�seau Hydro � partir des Dir. Drainage"
!       No_New_FILE = 0
!       CALL Ouvre_Mon_Projet(Nom_Logiciel, Code_Fich_Recent, Fonction_Logiciel &
!                           , FICH_PARAM, EXTEN_PROJ, DATE_RELEASE, 0, No_New_FILE)
!       LABGEN = "Calcul R�seau Hydro"
!       CALL Affich_Titr_Gene(1, LABGEN)
!       CALL Set_Line_of_Screen(7)
!       TITGEN = "Calcul du r�seau Hydro � partir des Dir. Drainage"
!       SELECT CASE (FICH_PARAM)
!       CASE (" ")
! !        ===============================================
! !         D�finition des noms de Fichiers et Param�tres
! !        ===============================================
!          ! CALL WRIT_STATUS_BAR("D�finition des Param�tres", 0, 0)
!          CALL Cree_Param_Cal_Reseau(FICH_PARAM, TITGEN, IOU,ITYP_DIRECT &
!            , NPERIO_TRONC, NBRE_VOIS_STATION, SURF_RIV &
!            , FICH_PRESENCE, FICH_DIRECT, FICH_ENT_EXIS_RIV, FICH_SOR_EXIS_RIV &
!            , FICH_ENT_SURF_AMO, FICH_SOR_SURF_AMO, FICH_ARBRE, FICH_AFFLU &
!            , FICH_TRONC, FICH_LISTING, FICH_X_Y_SURF, FICH_HISTORIQ &
!            , FICH_COL_LIG_SOUS_BV, FICH_SOUS_BASSIN, FICH_NUMER_SOUS_BV)
!          IF (FICH_PARAM /= " ") THEN
! !           =============
! !            Nom Complet
! !           =============
!             FICH_401 = DOSSIER_ET_NOM(FICH_PARAM)
! !           ===========
! !            Sauvegarde
! !           ============
!             CALL EDI_FICH_RECENT(FICH_401, Code_Fich_Recent)
!          ENDIF
!       CASE DEFAULT
! !        ============================================
! !         Lecture des noms de fichiers et param�tres
! !        ============================================
!          CALL WRIT_STATUS_BAR("Lecture des Param�tres", 0, 0)
!          CALL Lec_Param_Cal_Reseau(FICH_PARAM, TITGEN, LEC, ITYP_DIRECT &
!            , NPERIO_TRONC, NBRE_VOIS_STATION, SURF_RIV &
!            , FICH_PRESENCE, FICH_DIRECT, FICH_ENT_EXIS_RIV, FICH_SOR_EXIS_RIV &
!            , FICH_ENT_SURF_AMO, FICH_SOR_SURF_AMO, FICH_ARBRE, FICH_AFFLU &
!            , FICH_TRONC, FICH_LISTING, FICH_X_Y_SURF, FICH_HISTORIQ &
!            , FICH_COL_LIG_SOUS_BV, FICH_SOUS_BASSIN, FICH_NUMER_SOUS_BV)
!       END SELECT
!     =================
!      Fichier Listing
!     =================
      TITGEN = "Calculation of river network based on flow directions"

      ! IF (FICH_LISTING == " ") FICH_LISTING = "Cal_Res_Hydro.txt"
      ! CALL OPENEW(LISTIN, FICH_LISTING, IERNEW, 1)
      OPEN(UNIT=LISTIN, FILE=FICH_LISTING, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
      IF (IERNEW /= 0) THEN
         NATUR_FICH = "listing file "
         WRITE(*,*) "Problem when opening file: ", TRIM(NATUR_FICH), TRIM(FICH_LISTING)
         ! WRITE (WINT_BUFF, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH), TRIM(FICH_LISTING)
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         STOP " "
      ENDIF
      ! WRITE (LISTIN, 9005, IOSTAT=IERRAUX) TRIM(FICH_PARAM)
      ! WRITE (LISTIN, *)
      ! FICH_HISTORIQ = " "
      ! FICH_SOUS_BASSIN = " "
      WRITE (LISTIN, "(A)", IOSTAT=IERRAUX) TRIM(TITGEN)
      WRITE (LISTIN, *)
      WRITE (LISTIN, 9002, IOSTAT=IERRAUX) TRIM(FICH_PRESENCE) &
                                         , TRIM(FICH_DIRECT) &
                                         , TRIM(FICH_ENT_EXIS_RIV) &
                                         , TRIM(FICH_ENT_SURF_AMO) &
                                         , TRIM(FICH_X_Y_SURF) &
                                         , TRIM(FICH_COL_LIG_SOUS_BV)
      WRITE (LISTIN, *)
      WRITE (LISTIN, 9003, IOSTAT=IERRAUX) TRIM(FICH_SOR_SURF_AMO) &
                                         , TRIM(FICH_ARBRE) &
                                         , TRIM(FICH_AFFLU) &
                                         , TRIM(FICH_TRONC) &
                                         , TRIM(FICH_SOR_EXIS_RIV) &
                                         , TRIM(FICH_LISTING) &
                                         , TRIM(FICH_HISTORIQ) &
                                         , TRIM(FICH_SOUS_BASSIN) &
                                         , TRIM(FICH_NUMER_SOUS_BV)
      WRITE (LISTIN, *)
      CALL CODE_SUR_12_CARACT(SURF_RIV, CHARA12_SURF)
      WRITE (LISTIN, 9004, IOSTAT=IERRAUX) ITYP_DIRECT &
                                         , CHARA12_SURF &
                                         , NPERIO_TRONC &
                                         , NBRE_VOIS_STATION
      WRITE (LISTIN, *)
!     ==========
!      Lectures
!     ==========
!     =====================================
!      Fichier Présence Domaine de Surface
!     =====================================
      NATUR_FICH = "Surface domaine presence"
      ! CALL WRIT_STATUS_BAR("Lecture : "//TRIM(NATUR_FICH), 0, 0)
      ! CALL OPEOLD(LEC, FICH_PRESENCE, IEROLD)
      OPEN (UNIT=LEC, FILE=FICH_PRESENCE, STATUS="old", ACTION="read", BLANK="zero", IOSTAT=IEROLD)
      IF (IEROLD /= 0) THEN
         WRITE (LISTIN, 9006, IOSTAT=IERRAUX)    TRIM(FICH_PRESENCE), TRIM(NATUR_FICH)
         WRITE (*,*) "Problem when reading file: ", TRIM(FICH_PRESENCE), TRIM(NATUR_FICH)
         ! WRITE (WINT_BUFF, 9006, IOSTAT=IERRAUX) TRIM(FICH_PRESENCE), TRIM(NATUR_FICH)
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         STOP " "
      ENDIF
      CALL DIMSEM(NLIG, NKOL, TITSEM, IOUCON_NUL, LEC, IERLEC)

      IF (IERLEC /= 0) THEN
         WRITE (LISTIN, 9027, IOSTAT=IERRAUX) TRIM(NATUR_FICH), IERLEC, NKOL, NLIG
         WRITE (*, 9027, IOSTAT=IERRAUX) TRIM(NATUR_FICH), IERLEC, NKOL, NLIG
         ! WRITE (WINT_BUFF, 9027, IOSTAT=IERRAUX) TRIM(NATUR_FICH), IERLEC, NKOL, NLIG
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         STOP " "
      ENDIF
      REWIND (LEC)
!     =============
!      Allocations
!     =============
      NTOT = NLIG * NKOL
      ALLOCATE (XCOL(NKOL), DX_LU(NKOL), YLIG(NLIG), DY_LU(NLIG) &
              , HYDRO(NTOT), PRESEN(NTOT), ORIENT(NTOT), SURF_DRA(NTOT) &
              , IORD(NTOT), NMAI_AVAL(NTOT), STAT=IERRAUX)
      IF (IERRAUX /= 0) THEN
         WRITE (LISTIN, 9028, IOSTAT=IERRAUX) NKOL, NLIG, NTOT
         WRITE(*, 9028, IOSTAT=IERRAUX) NKOL, NLIG, NTOT
         ! WRITE (WINT_BUFF, 9028, IOSTAT=IERRAUX) NKOL, NLIG, NTOT
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         STOP " "
      ENDIF
      LIRE_DXDY = 1
      LU_DXDY = 1
      DX_LU(:) = -9999.
      DY_LU(:) = -9999.
      CALL LECSEM8_0(X0,Y0,PRESEN,XCOL,YLIG,NLIG,NKOL,INVERS,TITSEM &
          , IOUCON_NUL,LEC,IERLEC,NUMERR,NTOT &
          , LIRE_DXDY,LU_DXDY,LU_XY,DX_LU,DY_LU)
      CLOSE (LEC)
      IF (IERLEC == 0) THEN
         WRITE (LISTIN, 9007, IOSTAT=IERRAUX) TRIM(NATUR_FICH), TRIM(TITSEM(1:68)), NKOL, NLIG
         ! WRITE (*, 9029, IOSTAT=IERRAUX) TRIM(NATUR_FICH)
         ! WRITE (WINT_BUFF, 9029, IOSTAT=IERRAUX) TRIM(NATUR_FICH)
         ! CALL WRIT_ECR(IOUCON,WINT_BUFF,0)
         IF (LU_DXDY <= 0) THEN
!           =========================
!            Calcul des DX_LU, DY_LU
!           =========================
            CALL XY_DXDY(X0, Y0, XCOL, YLIG, DX_LU, DY_LU, NLIG, NKOL &
             , IOUCON, INVY, IER)
         ENDIF
      ELSE
         WRITE (LISTIN, 9008, IOSTAT=IERRAUX) TRIM(NATUR_FICH), IERLEC, NUMERR
         STOP " "
      ENDIF
!     ================================================
!      Initialisations car on connait maintenant NTOT
!     ================================================
      IORD(1:NTOT) = 0
      NMAI_AVAL(1:NTOT) = 0
!     =============================================
!      Orientations (degr�s ou 1001:1008 ou 1:128)
!     =============================================
      NATUR_FICH = "Flow_directions"
      ! CALL WRIT_STATUS_BAR("Lecture : "//TRIM(NATUR_FICH), 0, 0)
      ! CALL OPEOLD(LEC,FICH_DIRECT,IEROLD)
      OPEN (UNIT=LEC, FILE=FICH_DIRECT, STATUS="old", ACTION="read", BLANK="zero", IOSTAT=IEROLD)
      IF (IEROLD /= 0) THEN
         WRITE (LISTIN, 9006, IOSTAT=IERRAUX)    TRIM(FICH_DIRECT), TRIM(NATUR_FICH)
         WRITE (*, 9006, IOSTAT=IERRAUX) TRIM(FICH_DIRECT), TRIM(NATUR_FICH)
         ! WRITE (WINT_BUFF, 9006, IOSTAT=IERRAUX) TRIM(FICH_DIRECT), TRIM(NATUR_FICH)
         ! CALL Dial_Message_Wait(WINT_BUFF, 0 ,400)
         STOP " "
      ENDIF
      LIRE_DXDY = 0
      CALL LECSEM8_0(X0, Y0, ORIENT, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
         , IOUCON_NUL, LEC, IERLEC, NUMERR, NTOT &
         , LIRE_DXDY, LU_DXDY, LU_XY, DX_LU, DY_LU)
      CLOSE (LEC)
      IF (IERLEC == 0) THEN
         WRITE (LISTIN, 9007, IOSTAT=IERRAUX) TRIM(NATUR_FICH), TRIM(TITSEM(1:68)), NKOL, NLIG
         ! WRITE (*, 9029, IOSTAT=IERRAUX) TRIM(NATUR_FICH)
         ! WRITE (WINT_BUFF, 9029, IOSTAT=IERRAUX) TRIM(NATUR_FICH)
         ! CALL WRIT_ECR(IOUCON,WINT_BUFF,0)
      ELSE
         WRITE (LISTIN, 9008, IOSTAT=IERRAUX) TRIM(NATUR_FICH), IERLEC, NUMERR
         STOP " "
      ENDIF
!     ======================================================================
!      Pre-traitement des Directions de Drainages
!      * ITYP_DIRECT = 0 => Angles ou 1001:1008 => 1001:1008 (MARTHE)
!      * ITYP_DIRECT = 1 => ArcView 1:128       => 1001:1008 (MARTHE)
!      Si 9999   => Laisse 9999
!      1001-1004 => Sens aiguilles montre : N-E-S-W
!      1005-1008 => Directions obliques   : NE-SE-SW-NW
!      1,2,4,8,16,32,64,128 = est � est sens aiguilles montre de 45� en 45�
!     ======================================================================
      CALL Convert_Direct_Drain(ITYP_DIRECT, NTOT, ORIENT)
!     =============================================================================
!      Calcule le num�ro NMAI_AVAL(1:NTOT) de la maille Aval
!      � partir des Orientations (Directions de Drainage) 1001 � 1008
!      Provisoirement : met NMAI_AVAL = -9999 si sort du rectangle pour identifier
!     =============================================================================
      ! CALL WRIT_STATUS_BAR("Calcul du num�ro aval", 0, 0)
      CALL Direct_Drain_Mai_Ava(NTOT , NKOL , NLIG , ORIENT , NMAI_AVAL)
      NB_NON_DEFINIS = COUNT( ((PRESEN(1:NTOT) > 0.).AND. &
                               (ABS(PRESEN(1:NTOT)) /= 9999.).AND. &
                               (NMAI_AVAL(1:NTOT) == 0)) )
      NB_HORS_DOMAIN = COUNT( ((PRESEN(1:NTOT) > 0.).AND. &
                               (ABS(PRESEN(1:NTOT)) /= 9999.).AND. &
                               (NMAI_AVAL(1:NTOT) == -9999)) )
      WRITE (LISTIN, 9009, IOSTAT=IERRAUX) NB_NON_DEFINIS, NB_HORS_DOMAIN
!     ==================================================================
!      Si sort du rectangle (-9999) => Remet NMAI_AVAL = 0 (pas d'aval)
!     ==================================================================
      WHERE (NMAI_AVAL(1:NTOT) == -9999) NMAI_AVAL(1:NTOT) = 0
!     =======================================================
!      On met NMAI_AVAL = -1 en dehors du domaine de surface
!     =======================================================
      WHERE ((PRESEN(1:NTOT) == 0.).OR.(ABS(PRESEN(1:NTOT)) == 9999.)) &
       NMAI_AVAL(1:NTOT) = -1
!     ===========================================================
!      Lecture de [Pr�sence Rivi�res] ou [Surfaces Drain�es]
!      * Si Fichier Pr�sence Rivi�re (non " ") => Lit Pr�sence
!      * Si pas de Fichier Pr�sence Rivi�re = Cas g�n�ral
!        => Utilise SURF_RIV => Seuil pour d�terminer si rivi�re
!        * Si fichier Surfaces Drain�es => Les lit
!        * Si pas de fichier Surfaces Drain�es => Les calcule
!     ===========================================================
      IEX_SURF = 0
      NATUR_FICH = "River presence (indicator)"
      SELECT CASE (FICH_ENT_EXIS_RIV)
      CASE DEFAULT
!        ===================================================================
!         Lecture d'un fichier "Pr�sence rivi�res"
!         cad un fichier avec "1" sur les cours d'eau et 0 ou 9999 ailleurs
!        ===================================================================
         ! CALL WRIT_STATUS_BAR("Lecture : "//TRIM(NATUR_FICH), 0, 0)
         ! CALL OPEOLD(LEC,FICH_ENT_EXIS_RIV,IEROLD)
         OPEN (UNIT=LEC, FILE=FICH_ENT_EXIS_RIV, STATUS="old", ACTION="read", BLANK="zero", IOSTAT=IEROLD)
         IF (IEROLD /= 0) THEN
            WRITE (LISTIN, 9006, IOSTAT=IERRAUX)    TRIM(FICH_ENT_EXIS_RIV), TRIM(NATUR_FICH)
            WRITE (*, 9006, IOSTAT=IERRAUX) TRIM(FICH_ENT_EXIS_RIV), TRIM(NATUR_FICH)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0 ,400)
            STOP " "
         ENDIF
         LIRE_DXDY = 0
         CALL LECSEM8_0(X0, Y0, HYDRO, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
            , IOUCON_NUL, LEC, IERLEC, NUMERR, NTOT &
            , LIRE_DXDY, LU_DXDY, LU_XY, DX_LU, DY_LU)
         CLOSE (LEC)
         IF (IERLEC == 0) THEN
            WRITE (LISTIN, 9007, IOSTAT=IERRAUX) TRIM(NATUR_FICH), TRIM(TITSEM(1:68)), NKOL, NLIG
            ! WRITE (*, 9029, IOSTAT=IERRAUX) TRIM(NATUR_FICH)
            ! WRITE (WINT_BUFF, 9029, IOSTAT=IERRAUX) TRIM(NATUR_FICH)
            ! CALL WRIT_ECR(IOUCON,WINT_BUFF,0)
         ELSE
            WRITE (LISTIN, 9008, IOSTAT=IERRAUX) TRIM(NATUR_FICH), IERLEC, NUMERR
            STOP " "
         ENDIF
      CASE (" ")
!        =================================================================
!         Cas g�n�ral :
!         Pas de fichier "Existence Rivi�re"
!         => D�termination de surfaces drain�es : Il faut SURF_RIV > 0.
!         Lecture d'un fichier "Pr�sence rivi�res" ou [Surfaces Drain�es]
!        =================================================================
         ! WRITE (*,*) "Determination of drained surfaces ", TRIM(NATUR_FICH)
         ! CALL WRIT_STATUS_BAR("D�termination des surfaces drain�es", 0, 0)
         IF (SURF_RIV <= 0.) THEN
            WRITE (LISTIN, 9010, IOSTAT=IERRAUX)
            STOP " "
         ENDIF
         SELECT CASE (TRIM(FICH_ENT_SURF_AMO))
         CASE DEFAULT
!           ==========================================
!            Lecture d'un fichier "Surfaces Drain�es"
!            (calcul�es par "Cal_Direct_drainage"
!            Lues dans la variable "SURF_DRA"
!           ==========================================
            NATUR_FICH = "Grainage areas (surface drainée)"
            ! CALL WRIT_STATUS_BAR("Lecture : "//TRIM(NATUR_FICH), 0, 0)
            OPEN (UNIT=LEC, FILE=FICH_ENT_SURF_AMO, STATUS="old", ACTION="read", BLANK="zero", IOSTAT=IEROLD)
            ! CALL OPEOLD(LEC,FICH_ENT_SURF_AMO,IEROLD)
            IF (IEROLD /= 0) THEN
               WRITE (LISTIN, 9006, IOSTAT=IERRAUX)    TRIM(FICH_ENT_SURF_AMO), TRIM(NATUR_FICH)
               WRITE (*, 9006, IOSTAT=IERRAUX) TRIM(FICH_ENT_SURF_AMO), TRIM(NATUR_FICH)
               ! WRITE (WINT_BUFF, 9006, IOSTAT=IERRAUX) TRIM(FICH_ENT_SURF_AMO), TRIM(NATUR_FICH)
               ! CALL Dial_Message_Wait(WINT_BUFF, 0 ,400)
               STOP " "
            ENDIF
            LIRE_DXDY = 0
            CALL LECSEM8_0(X0,Y0,SURF_DRA,XCOL,YLIG,NLIG,NKOL,INVERS,TITSEM &
                , IOUCON_NUL,LEC,IERLEC,NUMERR,NTOT &
                , LIRE_DXDY,LU_DXDY,LU_XY,DX_LU,DY_LU)
            CLOSE (LEC)
            IF (IERLEC == 0) THEN
               WRITE (LISTIN, 9007, IOSTAT=IERRAUX) TRIM(NATUR_FICH), TRIM(TITSEM(1:68)), NKOL, NLIG
               ! WRITE (*, 9029, IOSTAT=IERRAUX) TRIM(NATUR_FICH)
               ! WRITE (WINT_BUFF, 9029, IOSTAT=IERRAUX) TRIM(NATUR_FICH)
               ! CALL WRIT_ECR(IOUCON,WINT_BUFF,0)
            ELSE
               WRITE (LISTIN, 9008, IOSTAT=IERRAUX) TRIM(NATUR_FICH), IERLEC, NUMERR
               STOP " "
            ENDIF
!           ===================================================================
!            Masquage des surfaces (Utile si un fichier "SURF_DRA" a �t� lu)
!            Pour �viter des Surfaces = 9999.
!           ===================================================================
            WHERE ((PRESEN(1:NTOT) == 0.).OR.(ABS(PRESEN(1:NTOT)) == 9999.)) SURF_DRA(1:NTOT) = 0.
            IEX_SURF = 1
         CASE (" ")
!           ===============================================================
!            Pas de fichier de "Surfaces drain�es Amonts"
!            Calcul des surfaces drain�es => Dans la variable "SURF_DRA()"
!           ===============================================================
            ! CALL WRIT_STATUS_BAR("Calcul des surfaces drain�es", 0, 0)
            WRITE (LISTIN, 9011, IOSTAT=IERRAUX)
!           ==============================================
!            *** Att : Routine appel�e plusieurs fois ***
!           ==============================================
            CALL Mai_Ava_Strahl_Surf_Drai(SURF_DRA, PRESEN, NMAI_AVAL &
              , NLIG, NKOL, NTOT, LISTIN, DX_LU, DY_LU)
            IEX_SURF = 1
            IF (FICH_SOR_SURF_AMO /= " ") THEN
               ! CALL WRIT_STATUS_BAR("�dition des surfaces drain�es", 0, 0)
               ! CALL PEEK_4_MES(ISTOP, 1)
!              =========================================
!               �dition des Surfaces Drain�es calcul�es
!              =========================================
               OPEN(UNIT=IOUMAI, FILE=FICH_SOR_SURF_AMO, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
               ! CALL OPENEW(IOUMAI,FICH_SOR_SURF_AMO,IERNEW,1)
               IF (IERNEW /= 0) THEN
                  NATUR_FICH = "Drainage areas calculation"
                  WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                        , TRIM(FICH_SOR_SURF_AMO)
                  WRITE (*, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                        , TRIM(FICH_SOR_SURF_AMO)
                  ! WRITE (WINT_BUFF, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                  !                                       , TRIM(FICH_SOR_SURF_AMO)                                                        
                  ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
               ELSE
                  TITSEM = "Drainage areas"
                  CODTIT_13 = "SURFA_DRAI"
                  WRITE (CHARA20, "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13), 1
                  TITSEM(71:) = TRIM(CHARA20)
                  CALL EDSEMI7_0(SURF_DRA, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
                     , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
                  CLOSE (IOUMAI)
                  ! CALL WRIT_STATUS_BAR("Fin de l'�dition des surfaces drain�es", 0, 0)
                  ! CALL PEEK_4_MES(ISTOP, 1)
               ENDIF
            ENDIF
         END SELECT
!        ===================================================================
!         On d�duit des surfaces drain�es : PRESENCE_RIV si Surface > SEUIL
!         (=> Variable "HYDRO()")
!        ===================================================================
         WHERE (SURF_DRA(1:NTOT) <= SURF_RIV) HYDRO(1:NTOT) = 0.
         WHERE (SURF_DRA(1:NTOT) >  SURF_RIV) HYDRO(1:NTOT) = 1.
         ! FICH_SOR_EXIS_RIV = " "
         IF (FICH_SOR_EXIS_RIV /= " ") THEN
            ! CALL WRIT_STATUS_BAR("�dition des pr�sences rivi�res", 0, 0)
            ! CALL PEEK_4_MES(ISTOP, 1)
!           =====================================
!            �dition du fichier Pr�sence Rivi�re
!           =====================================
            OPEN(UNIT=IOUMAI, FILE=FICH_SOR_EXIS_RIV, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
            ! CALL OPENEW(IOUMAI,FICH_SOR_EXIS_RIV,IERNEW,1)
            IF (IERNEW /= 0) THEN
               NATUR_FICH = "River presence (indicator) cal."
               WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                     , TRIM(FICH_SOR_EXIS_RIV)
               WRITE (*, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                     , TRIM(FICH_SOR_EXIS_RIV)
               ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
            ELSE
               TITSEM = "Présence Riviére calculées (1 = Riv.)"
               CODTIT_13 = "INDIC_RIVI"
               WRITE (CHARA20 , "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13), 1
               TITSEM(71:) = TRIM(CHARA20)
               CALL EDSEMI7_0(HYDRO, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
                  , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
               CLOSE (IOUMAI)
               ! CALL WRIT_STATUS_BAR("Fin de l'�dition des pr�sences rivi�res", 0, 0)
               ! CALL PEEK_4_MES(ISTOP, 1)
            ENDIF
         ENDIF
      END SELECT
!     ================================================================
!      Masquage du champ "Presence riviere"
!      (utile surtout si "Presence riviere" a �t� lu dans un fichier)
!     ================================================================
      WHERE ((PRESEN(1:NTOT) == 0.).OR.(ABS(PRESEN(1:NTOT)) == 9999.)) HYDRO(1:NTOT) = 0.
!     =========================================================================
!      D�termination du Nombre de mailles rivi�re : NBMRIV (pour dimensionner)
!     =========================================================================
      NBMRIV = COUNT(HYDRO(1:NTOT) == 1.)
      WRITE (LISTIN, 9013, IOSTAT=IERRAUX) NBMRIV
!     =============
!      Allocations
!     =============
      ALLOCATE (NUM_SEMIS(NBMRIV), NRIVAVA(NBMRIV), NRIAFFL(NBMRIV) &
              , NRITRON(NBMRIV), IANALY(NBMRIV), NBR_TRONC_DS_AFFLU(NBMRIV) &
              , NRIVAMO(NBMRIV, NB_AMONT_MAX), STAT=IERRAUX)
      IF (IERRAUX /= 0) THEN
         WRITE (LISTIN, 9030, IOSTAT=IERRAUX) NBMRIV, NB_AMONT_MAX
         WRITE (*, 9030, IOSTAT=IERRAUX) NBMRIV, NB_AMONT_MAX
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         STOP " "
      ELSE
         NUM_SEMIS = 0
         NRIVAVA = 0
         NRIAFFL = 0
         NRITRON = 0
         IANALY = 0
         NRIVAMO = 0
      ENDIF
!     ======================================================
!      Liste des mailles rivi�re : NBMRIV tron�ons au total
!     ======================================================
      KONT = 0
      DO N=1,NTOT
         IF (HYDRO(N) == 1.) THEN
            KONT = KONT + 1
            NUM_SEMIS(KONT) = N
            IORD(N) = KONT
         ENDIF
      ENDDO
!     ==========================================================
!      Analyse des mailles hors r�seau hydrographique
!      D�tection des mailles Sortant du Domaine ou non d�finies
!     ==========================================================
      ! CALL WRIT_STATUS_BAR("Analyse des mailles Hors r�seau hydrographique", 0, 0)
      ! CALL PEEK_4_MES(ISTOP, 1)
      CALL Mai_Exu_Surf_Drai(SURF_DRA, PRESEN, ORIENT, HYDRO, NMAI_AVAL &
                           , NTOT, NKOL, LISTIN)
!     ===================================================================
!      Calcul des num�ros d'ordre avals des Tron�ons rivi�re : NRIVAVA()
!     ===================================================================
      ! CALL WRIT_STATUS_BAR("Calcul des num. d'ordre des Tron�ons", 0, 0)
      KONT_EXUT = 0
      SOM_SURF_EXUT = 0.
      DO IR=1,NBMRIV
         N = NUM_SEMIS(IR)
         LIG = (N - 1) / NKOL + 1
         KOL = N - (LIG - 1) * NKOL
         IANGL = NINT(ORIENT(N))
         KOLVOIS = KOL
         LIGVOIS = LIG
!        ==============================================
!         IANGL => (KOLVOIS , LIGVOIS)
!         *** Att : Routine appel�e plusieurs fois ***
!        ==============================================
         IF (IANGL == 9999) THEN
            KOLVOIS = 9999
            LIGVOIS = 9999
         ELSE
            CALL Dir_Drain_LigCol_Ava(KOL, LIG, IANGL, KOLVOIS, LIGVOIS)
         ENDIF
         IF ((KOLVOIS == 9999).AND.(LIGVOIS == 9999)) THEN
!           ==========================
!            Incorrect (angle = 9999)
!            => NRIVAVA = 0
!           ==========================
            WRITE (LISTIN, 9014, IOSTAT=IERRAUX) IR, XCOL(KOL), YLIG(LIG), KOL, LIG, IANGL
            IF (IEX_SURF == 1) THEN
               CALL CODE_SUR_12_CARACT(SURF_DRA(N), CHARA12_SURF)
               WRITE (LISTIN, 9021, IOSTAT=IERRAUX) CHARA12_SURF
            ENDIF
            NRIVAVA(IR) = 0
            CYCLE
         ENDIF
!        ===========================
!         V�rif si sort du maillage
!        ===========================
         IF ((KOLVOIS < 1).OR.(KOLVOIS > NKOL).OR. &
             (LIGVOIS < 1).OR.(LIGVOIS > NLIG)) THEN
!           ============================
!            Maille aval hors rectangle
!           ============================
            KONT_EXUT = KONT_EXUT + 1
            WRITE (LISTIN, 9015, IOSTAT=IERRAUX) IR, XCOL(KOL), YLIG(LIG), KOL, LIG, IANGL &
                                               , KOLVOIS,LIGVOIS
            IF (IEX_SURF == 1) THEN
               CALL CODE_SUR_12_CARACT(SURF_DRA(N), CHARA12_SURF)
               WRITE (LISTIN, 9021, IOSTAT=IERRAUX) CHARA12_SURF
               SOM_SURF_EXUT = SOM_SURF_EXUT + SURF_DRA(N)
            ENDIF
            NRIVAVA(IR) = 0
            CYCLE
         ENDIF
         NVOIS = (LIGVOIS - 1) * NKOL + KOLVOIS
         IF ((PRESEN(NVOIS) == 0.).OR.(ABS(PRESEN(NVOIS)) == 9999.)) THEN
!           ==========================
!            Maille aval hors domaine
!           ==========================
            KONT_EXUT = KONT_EXUT + 1
            WRITE (LISTIN, 9016, IOSTAT=IERRAUX) IR,XCOL(KOL), YLIG(LIG), KOL, LIG, IANGL &
                                               , KOLVOIS, LIGVOIS, PRESEN(NVOIS)
            IF (IEX_SURF == 1) THEN
               CALL CODE_SUR_12_CARACT(SURF_DRA(N), CHARA12_SURF)
               WRITE (LISTIN, 9021, IOSTAT=IERRAUX) CHARA12_SURF
               SOM_SURF_EXUT = SOM_SURF_EXUT + SURF_DRA(N)
            ENDIF
         ELSE IF (HYDRO(NVOIS) /= 1.) THEN
!           =========================
!            Maille aval non rivi�re
!           =========================
            WRITE (LISTIN, 9017, IOSTAT=IERRAUX) IR, XCOL(KOL), YLIG(LIG), KOL, LIG, IANGL &
                                               , KOLVOIS, LIGVOIS
            IF (IEX_SURF == 1) THEN
               CALL CODE_SUR_12_CARACT(SURF_DRA(N), CHARA12_SURF)
               WRITE (LISTIN, 9021, IOSTAT=IERRAUX) CHARA12_SURF
            ENDIF
            NVOIS = 0
         ENDIF
         IF (NVOIS >= 1) THEN
            IRAVA = IORD(NVOIS)
         ELSE
            IRAVA = 0
         ENDIF
         NRIVAVA(IR) = IRAVA
      ENDDO
      WRITE (LISTIN, 9025, IOSTAT=IERRAUX) KONT_EXUT
      IF (IEX_SURF == 1) THEN
         CALL CODE_SUR_12_CARACT(SOM_SURF_EXUT, CHARA12_SURF)
         WRITE (LISTIN, 9026, IOSTAT=IERRAUX) CHARA12_SURF
      ENDIF
!     ===================================================================================
!      Calcul des num�ros d'ordre Amonts des tron�ons Rivi�re : NRIVAMO(IR,NB_AMONT_MAX)
!     ===================================================================================
      ! CALL WRIT_STATUS_BAR("Calcul des num�ros amonts", 0, 0)
      ! CALL PEEK_4_MES(ISTOP, 1)
      BAL_AVA: DO IR=1,NBMRIV
         IRAVA = NRIVAVA(IR)
         IF (IRAVA <= 0) CYCLE
!        ===================================
!         La maille IRAVA a pour amont : IR
!        ===================================
         DO K=1,NB_AMONT_MAX
            IF (NRIVAMO(IRAVA,K) == 0) THEN
!              ====================
!               UNE PLACE DE LIBRE
!              ====================
               NRIVAMO(IRAVA,K) = IR
               CYCLE BAL_AVA
            ENDIF
         ENDDO
!        ==============
!         Pas de place
!        ==============
!!!!!!!!!!!!!!!!!!!!!
          write (LISTIN,*)
          write (LISTIN,*) " Att tronçon IRAVA=",IRAVA," Plus de",NB_AMONT_MAX," amonts !"
         LIG = (NUM_SEMIS(IRAVA) -1) / NKOL + 1
         KOL = NUM_SEMIS(IRAVA) - (LIG - 1) * NKOL
         write (77,*) " Maille NUM_SEMIS(IRAVA)=",NUM_SEMIS(IRAVA)," KOL=",KOL," LIG=",LIG
         DO K=1,NB_AMONT_MAX
            NUMERR = NRIVAMO(IRAVA,K)
            IF (NUMERR == 0) CYCLE
            LIG = (NUM_SEMIS(NUMERR) -1) / NKOL + 1
            KOL = NUM_SEMIS(NUMERR) - (LIG - 1) * NKOL
            write (77,*) K," Tronc :",NUMERR," Maille NUM_SEMIS(NUMERR)=",NUM_SEMIS(NUMERR)," KOL=",KOL," LIG=",LIG
         ENDDO
!!!!!!!!!!!!!!!!!!!!!
      ENDDO BAL_AVA
!     =================================================================
!      D�termination du nombre KONSOURC de Sources (pour dimensionner)
!     =================================================================
      KONT = 0
      DO IR=1,NBMRIV
         IF (NRIVAMO(IR,1) == 0) THEN
!           ====================================
!            Troncon IR : Pas d'amont => Source
!           ====================================
            KONT = KONT + 1
         ENDIF
      ENDDO
      KONSOUR = KONT
      WRITE (LISTIN, 9019, IOSTAT=IERRAUX) KONSOUR
!     =============
!      Allocations
!     =============
      ALLOCATE (LISTSOUR(KONSOUR) ,STAT=IERRAUX)
      IF (IERRAUX /= 0) THEN
         WRITE (LISTIN, 9018, IOSTAT=IERRAUX) KONSOUR
         WRITE (*, 9030, IOSTAT=IERRAUX) KONSOUR
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         STOP " "
      ELSE
         LISTSOUR = 0
      ENDIF
!     ====================================
!      D�termination des KONSOURC sources
!     ====================================
      KONT = 0
      DO IR=1,NBMRIV
         IF (NRIVAMO(IR,1) == 0) THEN
!           ====================================
!            Troncon IR : pas d'amont => Source
!           ====================================
            KONT = KONT + 1
            LISTSOUR(KONT) = IR
         ENDIF
      ENDDO
!     ====================================
!      Numeros d'Affluents et de Troncons
!     ====================================
      ! CALL WRIT_STATUS_BAR("Calcul des num Affl. & Tron�ons", 0, 0)
      ! CALL PEEK_4_MES(ISTOP, 1)
!     ==================================
!      Balaye les Sources
!      => Calcule :
!      * NRIAFFL() = Numero d'Affluent
!      * NRITRON() = Numero de Tron�ons
!      * NUMAFL    = Nombre d'Affluents
!     ==================================
      IANALY (1:NBMRIV) = 0
      NUMAFL = 0
      BAL_SOUR: DO ISOUR=1,KONSOUR
         NUMAFL = NUMAFL + 1
         IR = LISTSOUR(ISOUR)
         KONT = 1
         NRIAFFL(IR) = NUMAFL
         NRITRON(IR) = KONT
         IANALY (IR) = 1
         NBR_TRONC_DS_AFFLU(NUMAFL) = KONT
         DO K=1,NBMRIV
!           ================
!            Passe � l'aval
!           ================
            IRAVA = NRIVAVA(IR)
!           ========================
!            L'aval est un exutoire
!           ========================
            IF (IRAVA <= 0) CYCLE BAL_SOUR
            IR = IRAVA
!           ===============================
!            D�j� pass� (cad d�j� analys�)
!            => Source suivante
!           ===============================
            IF (IANALY (IR) > 0) THEN
!              ==============
!               Pour Raccord
!              ==============
               NBR_TRONC_DS_AFFLU(NUMAFL) = KONT + 1
               CYCLE BAL_SOUR
            ENDIF
            KONT = KONT + 1
            NBR_TRONC_DS_AFFLU(NUMAFL) = KONT
!           ===============================
!            Recherche si plusieurs amonts
!           ===============================
            NBAMONT = COUNT( (NRIVAMO(IR,1:NB_AMONT_MAX) > 0) )
            IF (NBAMONT > 1) THEN
!              ====================================
!               Plusieurs amonts => Autre affluent
!              ====================================
!              =================================================================
!               On incr�mente NUMAFL apr�s avoir m�moris� le nombre de tron�ons
!              =================================================================
               NUMAFL = NUMAFL + 1
               KONT = 1
               NBR_TRONC_DS_AFFLU(NUMAFL) = KONT
            ENDIF
            NRIAFFL(IR) = NUMAFL
            NRITRON(IR) = KONT
            IANALY (IR) = 1
         ENDDO
      ENDDO BAL_SOUR
!     ==========================
!      Nombre total d'Affluents
!     ==========================
      WRITE (LISTIN, 9020, IOSTAT=IERRAUX) NUMAFL
      IF (FICH_SOR_EXIS_RIV /= " ") THEN
!        ===================================================
!         �dition du trac� [*.bln] du R�seau Hydrographique
!        ===================================================
!        ====================================
!         Addition du suffixe "bln" Toujours
!        ====================================
         ! CALL WRIT_STATUS_BAR("�dition du trac� du r�seau [.bln]", 0, 0)
         ! CALL PEEK_4_MES(ISTOP, 1)
         CALL Ajout_Toujours_Extens(FICH_SOR_EXIS_RIV, FICH_SOR_RIV_BLN, "bln")
         ! WRITE(*,*) "FICH_SOR_RIV_BLN = ", FICH_SOR_RIV_BLN
         OPEN(UNIT=IOUMAI, FILE=FICH_SOR_RIV_BLN, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
         ! CALL OPENEW(IOUMAI, FICH_SOR_RIV_BLN, IERNEW, 1)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Tracé du réseau"
            WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOR_RIV_BLN)
            WRITE (*, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOR_RIV_BLN)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         ELSE
!           =====================================
!            �dition des coordonn�es du parcours
!           =====================================
            IANALY (1:NBMRIV) = 0
            NUMAFL = 0
            BAL_SOUR5: DO ISOUR=1,KONSOUR
               NUMAFL = NUMAFL + 1
               IR = LISTSOUR(ISOUR)
               IANALY (IR) = 1
               WRITE (CHAR7 , "(I7)", IOSTAT=IERRAUX) NUMAFL
               WRITE (IOUMAI, "(I7,' 0 Afflu_',A,' xy')", IOSTAT=IERRAUX) &
                             NBR_TRONC_DS_AFFLU(NUMAFL), TRIM(ADJUSTL(CHAR7))
               LIG = (NUM_SEMIS(IR) - 1) / NKOL + 1
               KOL = NUM_SEMIS(IR) - (LIG - 1) * NKOL
               WRITE (IOUMAI, *) XCOL(KOL), YLIG(LIG)
               DO K=1,NBMRIV
!                 ================
!                  Passe � l'aval
!                 ================
                  IRAVA = NRIVAVA(IR)
!                 ===================
!                  C'est un Exutoire
!                 ===================
                  IF (IRAVA <= 0) CYCLE BAL_SOUR5
                  IR = IRAVA
                  LIG = (NUM_SEMIS(IR) - 1) / NKOL + 1
                  KOL = NUM_SEMIS(IR) - (LIG - 1) * NKOL
                  WRITE (IOUMAI, *) XCOL(KOL),YLIG(LIG)
!                 =================================
!                  D�j� pass� (c-�-d d�j� analys�)
!                  => Source suivante
!                 =================================
                  IF (IANALY (IR) > 0) CYCLE BAL_SOUR5
!                 ===============================
!                  Recherche si plusieurs Amonts
!                 ===============================
                  NBAMONT = COUNT( (NRIVAMO(IR,1:NB_AMONT_MAX) > 0) )
                  IF (NBAMONT > 1) THEN
!                    ====================================
!                     Plusieurs amonts => Autre affluent
!                    ====================================
                     NUMAFL = NUMAFL + 1
                     WRITE (CHAR7 , "(I7)", IOSTAT=IERRAUX) NUMAFL
                     WRITE (IOUMAI, "(I7,' 0 Afflu_',A,' xy')", IOSTAT=IERRAUX) &
                             NBR_TRONC_DS_AFFLU(NUMAFL), TRIM(ADJUSTL(CHAR7))
                     LIG = (NUM_SEMIS(IR) - 1) / NKOL + 1
                     KOL = NUM_SEMIS(IR) - (LIG - 1) * NKOL
                     WRITE (IOUMAI, *) XCOL(KOL), YLIG(LIG)
                  ENDIF
                  IANALY (IR) = 1
               ENDDO
            ENDDO BAL_SOUR5
            CLOSE (IOUMAI)
            ! CALL WRIT_STATUS_BAR("Fin de l'�dition du trac� du r�seau [.bln]", 0, 0)
            ! CALL PEEK_4_MES(ISTOP, 1)
         ENDIF
      ENDIF
      IF (NPERIO_TRONC > 1) THEN
!        =====================================
!         P�riodicit� des Num�ros de Troncons
!        =====================================
         WHERE (ABS(NRITRON(1:NBMRIV)) /= 9999) NRITRON(1:NBMRIV) &
                                              = NRITRON(1:NBMRIV) * NPERIO_TRONC
      ENDIF
!     ====================================
!      Arbre de Branchement des Affluents
!     ====================================
      IF (FICH_ARBRE /= " ") THEN
!        =================================================
!         �dition de l'Arbre de branchement des affluents
!        =================================================
         ! CALL WRIT_STATUS_BAR("Arbre de branchement", 0, 0)
         ! CALL PEEK_4_MES(ISTOP, 1)
         OPEN(UNIT=IOUMAI, FILE=FICH_ARBRE, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
         ! CALL OPENEW(IOUMAI,FICH_ARBRE,IERNEW,1)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Arbre de branchement des affluents"
            WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_ARBRE)
            WRITE (*, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_ARBRE)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0 ,400)
         ELSE
!           ===================
!            Calcul et �dition
!           ===================
            TITSEM = "Arbre de branchement des affluents"
            WRITE (IOUMAI, "(A)", IOSTAT=IERRAUX) TRIM(TITSEM)//" Affl , Affl_Aval"
!           ========================================
!            � partir des Sources (=> Dans l'ordre)
!           ========================================
            IANALY (1:NBMRIV) = 0
            BAL_SOUR3: DO ISOUR=1,KONSOUR
               IR = LISTSOUR(ISOUR)
               IANALY (IR) = 1
               DO K=1,NBMRIV
                  NUMAFL = NRIAFFL(IR)
!                 ================
!                  Passe � l'aval
!                 ================
                  IRAVA = NRIVAVA(IR)
                  IF (IRAVA <= 0) THEN
!                    ================================
!                     C'est un exutoire
!                     => On a fini pour cette Source
!                    ================================
                     NUMAFL_AVA = 0
                     WRITE (IOUMAI, *, IOSTAT=IERRAUX) NUMAFL, NUMAFL_AVA
                     CYCLE BAL_SOUR3
                  ENDIF
                  NUMAFL_AVA = NRIAFFL(IRAVA)
                  IF (NUMAFL_AVA /= NUMAFL) WRITE (IOUMAI, *, IOSTAT=IERRAUX) NUMAFL, NUMAFL_AVA
                  IR = IRAVA
!                 ================================
!                  D�j� pass� (Cad d�j� analys�e)
!                 ================================
                  IF (IANALY (IR) > 0) CYCLE BAL_SOUR3
                  IANALY (IR) = 1
               ENDDO
            ENDDO BAL_SOUR3
            LABAUX = " *** Fin du fichier Arbre des Affluents Rivière      ***"
            WRITE (IOUMAI, "(A)", IOSTAT=IERRAUX) TRIM(LABAUX)
           CLOSE (IOUMAI)
         ENDIF
      ENDIF
!     ==========
!      �ditions
!     ==========
      ! CALL WRIT_STATUS_BAR("�dition des Affl. & Tron�ons", 0, 0)
      ! CALL PEEK_4_MES(ISTOP, 1)
      IEDIT_RESEAU = 0
      IEDIT_RESEAU = 1
      IF (IEDIT_RESEAU == 1) THEN
!        ===========================================
!         �dition des Tron�ons � partir des Sources
!        ===========================================
         ! CALL WRIT_STATUS_BAR("�dition du parcours depuis les sources", 0, 0)
         WRITE (LISTIN, 9024)
         IANALY (1:NBMRIV) = 0
         BAL_SOUR2: DO ISOUR=1,KONSOUR
            KONT = 1
            IR = LISTSOUR(ISOUR)
            LIG = (NUM_SEMIS(IR) - 1) / NKOL + 1
            KOL = NUM_SEMIS(IR) - (LIG - 1) * NKOL
            WRITE (LISTIN, 9022) ISOUR, KOL, LIG, NRIAFFL(IR), NRITRON(IR)
            IANALY (IR) = 1
            DO K=1,NBMRIV
!              ================
!               Passe � l'aval
!              ================
               IRAVA = NRIVAVA(IR)
!              ===================
!               C'est un exutoire
!              ===================
               IF (IRAVA <= 0) EXIT
!              ================================
!               D�j� pass� (Cad d�j� analys�e)
!              ================================
               IF (IANALY (IRAVA) > 0) EXIT
               IR = IRAVA
               KONT = KONT + 1
               LIG = (NUM_SEMIS(IR) - 1) / NKOL + 1
               KOL = NUM_SEMIS(IR) - (LIG - 1) * NKOL
               IANALY (IR) = 1
            ENDDO
            WRITE (LISTIN, 9023) KONT, KOL, LIG, NRIAFFL(IR), NRITRON(IR)
         ENDDO BAL_SOUR2
         CLOSE (IOUMAI)
      ENDIF
!     ============================
!      �dition des Grilles Marthe
!      N.B. �crase HYDRO()
!     ============================
      IF (FICH_AFFLU /= " ") THEN
!        =================================
!         �dition des num�ros d'Affluents
!        =================================
         ! CALL WRIT_STATUS_BAR("�dition des num�ros d'Affluents", 0, 0)
         ! CALL PEEK_4_MES(ISTOP, 1)
         OPEN(UNIT=IOUMAI, FILE=FICH_AFFLU, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
         ! CALL OPENEW(IOUMAI, FICH_AFFLU, IERNEW, 1)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Numéros d'Affluents"
            WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_AFFLU)
            WRITE (*, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_AFFLU)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         ELSE
            TITSEM = "Numéros d'Affluents"
            CODTIT_13 = "AFFLU_RIVI"
            WRITE (CHARA20, "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13), 1
            TITSEM(71:) = TRIM(CHARA20)
!           ====================================================
!            Chargement des num�ros d'Affluents => Pour �dition
!           ====================================================
            HYDRO(1:NTOT) = 0.
            DO IR=1,NBMRIV
               N = NUM_SEMIS(IR)
               HYDRO(N) = REAL( NRIAFFL(IR) )
            ENDDO
            CALL EDSEMI7_0(HYDRO, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
               , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
           CLOSE (IOUMAI)
         ENDIF
      ENDIF
      IF (FICH_TRONC /= " ") THEN
!        =================================
!         édition des numéros de Tronçons
!        =================================
         ! CALL WRIT_STATUS_BAR("�dition des num�ros de tron�ons", 0, 0)
         ! CALL PEEK_4_MES(ISTOP, 1)
         OPEN(UNIT=IOUMAI, FILE=FICH_TRONC, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
         ! CALL OPENEW(IOUMAI, FICH_TRONC, IERNEW, 1)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Numéros de Tronçons"
            WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_TRONC)
            WRITE (*, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_TRONC)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         ELSE
            TITSEM = "Numéros de Tronçons"
            CODTIT_13 = "TRONC_RIVI"
            WRITE (CHARA20 , "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13), 1
            TITSEM(71:) = TRIM(CHARA20)
!           =================================================
!            Chargement des numéros de Tronçons pour édition
!           =================================================
            HYDRO(1:NTOT) = 0.
            DO IR=1,NBMRIV
               N = NUM_SEMIS(IR)
               HYDRO(N) = REAL( NRITRON(IR) )
            ENDDO
            CALL EDSEMI7_0(HYDRO, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
               , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
           CLOSE (IOUMAI)
         ENDIF
      ENDIF
      IF (FICH_X_Y_SURF /= " ") THEN
!        ======================================================
!         Calcul et correction des Surfaces des Stations hydro
!         � partir du fichier surfaces drain�es
!        ======================================================
         ! CALL WRIT_STATUS_BAR("Contr�le des surfaces des stations", 0, 0)
         ! CALL PEEK_4_MES(ISTOP, 1)
         IF (IEX_SURF == 0) THEN
!           =======================================================
!            Les surfaces drain�es des mailles ne sont pas connues
!           =======================================================
            ! CALL WRIT_STATUS_BAR("Calcul des surfaces drain�es", 0, 0)
            WRITE (LISTIN, 9011, IOSTAT=IERRAUX)
!           ==============================================
!            *** Att : Routine appel�e plusieurs fois ***
!           ==============================================
            CALL Mai_Ava_Strahl_Surf_Drai(SURF_DRA, PRESEN,NMAI_AVAL &
              , NLIG,NKOL,NTOT,LISTIN,DX_LU,DY_LU)
            IEX_SURF = 1
         ENDIF
!        =========================================================
!         Chargement des num�ros d'Affluents pour calcul surfaces
!        =========================================================
         HYDRO(1:NTOT) = 0.
         DO IR=1,NBMRIV
            N = NUM_SEMIS(IR)
            HYDRO(N) = REAL( NRIAFFL(IR) )
         ENDDO
         CALL Verif_Surf_Stat_Hydro(FICH_X_Y_SURF, FICH_HISTORIQ, LEC, LISTIN, IOUMAI &
                                  , HYDRO, SURF_DRA &
                                  , XCOL, YLIG, DX_LU, DY_LU, NLIG, NKOL, NTOT &
                                  , NBRE_VOIS_STATION)
      ENDIF
      IF (FICH_COL_LIG_SOUS_BV /= " ") THEN
!        =======================================================================
!         Calcul des mailles des sous-bassins dont les exutoires sont col, lign
!         � partir du fichier des directions de drainage
!         => En retour : HYDRO() => Grille Marthe avec num�ros des sous-bassins
!        =======================================================================
         ! CALL WRIT_STATUS_BAR("Calcul de mailles de sous-bassins", 0, 0)
         ! CALL PEEK_4_MES(ISTOP, 1)
         CALL Definit_Sous_Bassins(FICH_COL_LIG_SOUS_BV, FICH_SOUS_BASSIN &
                                 , LEC, LISTIN, IOUMAI &
                                 , PRESEN, HYDRO, NMAI_AVAL &
                                 , DX_LU, DY_LU, NLIG, NKOL, NTOT, X0, Y0)
!        ===========================================================
!         �dition de la 'Grille Marthe' des num�ros de sous-bassins
!        ===========================================================
         ! CALL WRIT_STATUS_BAR("�dition du champs des num�ros de sous-bassins", 0, 0)
         ! CALL PEEK_4_MES(ISTOP, 1)
         OPEN(UNIT=IOUMAI, FILE=FICH_NUMER_SOUS_BV, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
         ! CALL OPENEW(IOUMAI, FICH_NUMER_SOUS_BV, IERNEW, 1)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Numéros de sous-bassins"
            WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_NUMER_SOUS_BV)
            WRITE (*, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_NUMER_SOUS_BV)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         ELSE
            TITSEM = "Numéros des Sous-Bassins"
            CODTIT_13 = "NUM_SOUS_BASS"
            WRITE (CHARA20 , "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13) , 1
            TITSEM(71:) = TRIM(CHARA20)
            CALL EDSEMI7_0(HYDRO, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
               , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
           CLOSE (IOUMAI)
         ENDIF
      ENDIF
#ifndef ENGLISH      
 9001 FORMAT (" Impossible d'ouvrir un fichier ",A," :" &
             /" de nom :",A)
 9002 FORMAT (" Fichiers d'entrée :" &
             /" Présence domaine surface   =",1X,A &
             /" Directions                 =",1X,A &
             /" Présence Riviére           =",1X,A &
             /" Surfaces Drainées          =",1X,A &
             /" X_Y_Surf. Stations hydro   =",1X,A &
             /" Col Lign des Exut Sous-Bass=",1X,A)
 9003 FORMAT (" Fichiers de sortie :" &
             /" Surf_Drainées Calculées    =",1X,A &
             /" Arbre de branchement       =",1X,A &
             /" Num d'Affluents            =",1X,A &
             /" Num de Tronçons            =",1X,A &
             /" Présence Rivière Calcul.   =",1X,A &
             /" Listing                    =",1X,A &
             /" Historiques de débits      =",1X,A &
             /" Sous_Bassins               =",1X,A &
             /" Numéros des Sous_Bassins   =",1X,A)
 9004 FORMAT (" Paramètres :" &
             /" Type de directions (0=1001:1008 = MARTHE)  =",1X,I10 &
             /" Surface drainée mini Riv.                  =",1X,A &
             /" Périodicité Num Tronçons                   =",1X,I10 &
             /" Nbre de mailles vois. pour stations Hydro  =",1X,I10)
!  9005 FORMAT (/" Fichier paramètres : ",A)
 9006 FORMAT (//" *** Le fichier de nom '",A,"'",T77,"***" &
               /" *** n'a pas été trouvé",T77,"***" &
               /" *** pour les données de '",A,"'",T77,"***"/)
 9007 FORMAT (/" Lecture du fichier ",A," effectuée" &
              /" Titre descriptif = ",A &
              /" Nombre de colonnes = ",I0 &
              /" Nombre de lignes   = ",I0)
 9008 FORMAT (/" Erreur dans la lecture du fichier ",A," :" &
              /" (IERLEC = ",I0," Maille NUMERR ",I0)
 9009 FORMAT (/" Nombre de Directions du domaine non définies         =",I6 &
              /" Nombre de Directions sortant du rectangle du domaine =",I6)
 9010 FORMAT (/" Il faut définir une surface minimale pour rivières ((surf_riv)) !")
 9011 FORMAT (/" Calcul des surfaces drainées (surfaces amont)"/)
 9013 FORMAT (/" Nombre de tronçons détectés = ",I0)
 9014 FORMAT (/" Maille Rivière Num_Ordre n° ",I0," : x=",ES13.5," , y=",ES13.5 &
              /" Colonne = ",I0," , Ligne = ",I0," => Direction (angle) = ",I0," Non définie")
 9015 FORMAT (/" Maille Rivière Num_Ordre n° ",I0," : x=",ES13.5," , y=",ES13.5 &
              /" Colonne = ",I0," , Ligne = ",I0," Direction (angle) = ",I0 &
              /" => Tronçon aval : Colonne = ",I0," , Ligne = ",I0," ** Hors Rectangle **")
 9016 FORMAT (/" Maille Rivière Num_Ordre n° ",I0," : x=",ES13.5," , y=",ES13.5 &
              /" Colonne = ",I0," , Ligne = ",I0," Direction (angle) = ",I0 &
              /" => Tronçon aval : Colonne = ",I0," , Ligne = ",I0," => Exutoire" &
              /"    (Valeur de l'indicateur de présence =",F0.1,")")
 9017 FORMAT (/" Maille Rivière Num_Ordre n° ",I0," : x=",ES13.5," , y=",ES13.5 &
              /" Colonne = ",I0," , Ligne = ",I0," Direction (angle) = ",I0 &
              /" => Tronçon aval : Colonne = ",I0," Ligne = ",I0 &
              ," ** qui n'est pas une rivière **")
 9018 FORMAT (/" Erreur : Impossible d'allouer la mémoire nécessaire" &
              /" ",I0," Sources d'affluents")
 9019 FORMAT (/" Nombre de Sources d'affluents détectées =",I7)
 9020 FORMAT (/" Nombre total d'affluents détectés       =",I7)
 9021 FORMAT ( "    (Surface drainée =",A,")")
 9022 FORMAT ( " Source n° ",I0," : Maille Col= ",I0," , Lig= ",I0," , Affl= ",I0," , Tronç= ",I0)
 9023 FORMAT (" ",I0," tronçons => Maille Col =",I0," , Lig =",I0 &
              ," , Affl= ",I0," , Tronç= ",I0)
 9024 FORMAT (/" Analyse du réseau"/)
 9025 FORMAT (/" Nombre total d'exutoires                =",I7)
 9026 FORMAT ( " Surface totale drainée par les exutoires=",A)
 9027 FORMAT (/" Erreur dans la lecture du fichier ",A," :" &
              /" (IERLEC = ",I0,") ; ",I0," Colonnes ; ",I0," Lignes")
 9028 FORMAT (/" Erreur : Impossible d'allouer la mémoire nécessaire" &
              /" ",I0," Colonnes ; ",I0," Lignes ; ",I0," Mailles")
!  9029 FORMAT (" Lecture du fichier ",A," terminée")
 9030 FORMAT (/" Erreur : Impossible d'allouer la mémoire nécessaire" &
              /" ",I0," Tronçons de rivières ; ",I0," Amonts maximum")
#else
 9001 FORMAT (" Impossible to open a file ",A," :" &
             /" with name :",A)
 9002 FORMAT (" Input files :" &
             /" Presence of surface domaine      =",1X,A &
             /" Flow rections                    =",1X,A &
             /" River presence indicators        =",1X,A &
             /" Drainage areas                   =",1X,A &
             /" X_Y_Surf. hydro Stations         =",1X,A &
             /" Col row of subbasin outlet       =",1X,A)
 9003 FORMAT (" Output files :" &
             /" Calculated Drainage areas        =",1X,A &
             /" River connection tree            =",1X,A &
             /" Num of tributaries               =",1X,A &
             /" Num of reaches                   =",1X,A &
             /" Calculated river indicators      =",1X,A &
             /" Listing                          =",1X,A &
             /" Historical discharge             =",1X,A &
             /" Sub-basin                        =",1X,A &
             /" Numver of sub-basins             =",1X,A)
 9004 FORMAT (" Parameters :" &
             /" Type of directions (0=1001:1008 = MARTHE; 1=1:128 = ArcGis)  =",1X,I10 &
             /" Minimum drained surface area Riv.                            =",1X,A &
             /" Periodicity num reaches                                      =",1X,I10 &
             /" Number of neighboring cells for hydro stations               =",1X,I10)
!  9005 FORMAT (/" Fichier paramètres : ",A)
 9006 FORMAT (//" *** The file '",A,"'",T77,"***" &
               /" *** was not found",T77,"***" &
               /" *** for data of '",A,"'",T77,"***"/)
 9007 FORMAT (/" File ",A," read complete " &
              /" Descriptive title = ",A &
              /" Number of columns = ",I0 &
              /" Number of rows   = ",I0)
 9008 FORMAT (/" Error when reading file ",A," :" &
              /" (IERLEC = ",I0," Maille NUMERR ",I0)
 9009 FORMAT (/" Number of flow directions not defined   =",I6 &
              /" Number of directions outside the domain =",I6)
 9010 FORMAT (/" A minimum surface area for rivers (surf_riv) must be defined!")
 9011 FORMAT (/" Calculation of drainage areas (upstream areas)"/)
 9013 FORMAT (/" Number of river reaches detected = ",I0)
 9014 FORMAT (/" Cell river Num_Order n° ",I0," : x=",ES13.5," , y=",ES13.5 &
              /" Column = ",I0," , Row = ",I0," => Direction (angle) = ",I0," Not defined")
 9015 FORMAT (/" Cell river Num_Order n° ",I0," : x=",ES13.5," , y=",ES13.5 &
              /" Column = ",I0," , Row = ",I0," Direction (angle) = ",I0 &
              /" => Downstream reach: Column = ",I0," , Row = ",I0," ** Outside Rectangle **")
 9016 FORMAT (/" Cell river Num_Order n° ",I0," : x=",ES13.5," , y=",ES13.5 &
              /" Column = ",I0," , Row = ",I0," Direction (angle) = ",I0 &
              /" => Downstream reach: Column = ",I0," , Row = ",I0," => Outlet" &
              /"    (Value of the river presence indicator =",F0.1,")")
 9017 FORMAT (/" Cell river Num_Order n° ",I0," : x=",ES13.5," , y=",ES13.5 &
              /" Column = ",I0," , Row = ",I0," Direction (angle) = ",I0 &
              /" => Downstream reach: Column = ",I0," Row = ",I0 &
              ," ** which is not a river **")
 9018 FORMAT (/" Error : Impossible to allocate the necessary memory" &
              /" ",I0," Sources of tributaries")
 9019 FORMAT (/" Number of Tributary Sources detected =",I7)
 9020 FORMAT (/" Total number of tributaries detected =",I7)
 9021 FORMAT ( "    (Drained surface =",A,")")
 9022 FORMAT ( " Source n° ",I0," : Cell Col= ",I0," , Row= ",I0," , Tributary= ",I0," , Reach= ",I0)
 9023 FORMAT (" ",I0," reaches => Cell Col =",I0," , Row =",I0 &
              ," , Tribu= ",I0," , Reach= ",I0)
 9024 FORMAT (/" Network analysis"/)
 9025 FORMAT (/" Total number of outlets                  =",I7)
 9026 FORMAT ( " Total surface area drained by the outlets=",A)
 9027 FORMAT (/" Error when reading file ",A," :" &
              /" (IERLEC = ",I0,") ; ",I0," Columns ; ",I0," Rows")
 9028 FORMAT (/" Error : Impossible to allocate the necessary memory" &
              /" ",I0," Columns ; ",I0," Rows ; ",I0," Cells")
!  9029 FORMAT (" Lecture du fichier ",A," terminée")
 9030 FORMAT (/" Error : Impossible to allocate the necessary memory" &
              /" ",I0," River reaches ; ",I0," Maximum upstreams")
#endif            
         CONTAINS
!        ////////
         SUBROUTINE CODE_SUR_12_CARACT(VALEUR , CHARA12_SURF)
            IMPLICIT NONE
            REAL    , INTENT(IN):: VALEUR
            CHARACTER (LEN=12), INTENT(OUT) :: CHARA12_SURF
!           ========
!            Locaux
!           ========
            INTEGER :: IERRAUX
!           =======
!            D�but
!           =======
            IF ( (VALEUR == 0.).OR. &
                ((VALEUR >= 0.1).AND.(VALEUR <= 10000.)) ) THEN
               WRITE (CHARA12_SURF, "(F12.3)", IOSTAT=IERRAUX) VALEUR
            ELSE
               WRITE (CHARA12_SURF, "(ES12.3)", IOSTAT=IERRAUX) VALEUR
            ENDIF
         END SUBROUTINE CODE_SUR_12_CARACT
      END SUBROUTINE Cal_reseau_hydro

      SUBROUTINE Verif_Surf_Stat_Hydro(FICH_X_Y_SURF, FICH_HISTORIQ, LEC, LISTIN, IOUMAI &
                                     , HYDRO, SURF_DRA &
                                     , XCOL, YLIG, DX_LU, DY_LU, NLIG, NKOL, NTOT &
                                     , NBRE_VOIS_STATION)
!=======================================================================
!   ***********************
!   *Verif_Surf_Stat_Hydro*            BRGM     B.P. 36009
!   ***********************            45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      Calcul et correction des surfaces des Stations Hydrom�triques
!      � partir du fichier des Surfaces Drain�es
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NLIG, NKOL, NTOT, LEC, LISTIN, IOUMAI
      INTEGER, INTENT(IN) :: NBRE_VOIS_STATION
      REAL, DIMENSION(NKOL), INTENT(IN) :: XCOL, DX_LU
      REAL, DIMENSION(NLIG), INTENT(IN) :: YLIG, DY_LU
      REAL, DIMENSION(NTOT), INTENT(IN) :: HYDRO, SURF_DRA
      CHARACTER (LEN=*), INTENT(IN) :: FICH_X_Y_SURF, FICH_HISTORIQ
      ! CHARACTER (LEN=80), DIMENSION(25) :: WINT_BUFF
      ! COMMON/WINT_WRITE/WINT_BUFF
!     ========
!      Locaux
!     ========
      INTEGER, PARAMETER :: MAX_STAT = 500
      REAL, DIMENSION(MAX_STAT) :: XP, YP, SURFP
      CHARACTER (LEN=7) :: CHAR7_X, CHAR7_Y
      CHARACTER (LEN=40), DIMENSION(MAX_STAT) :: NOM_STAT
      CHARACTER (LEN=80) :: TITAUX, NATUR_FICH
      REAL    :: SURF_REF, SURF_CEN, DIF_SURF, DIFF_OPT, XX, YY &
                ,YHAUT, YBAS, XDROI, XGAUC, X_HIST, Y_HIST, SURF_OPT, SURF_VOI, DIF_VOIS
      INTEGER :: I, K, L, LIG, KOL, LIGCEN, KOLCEN, KOLOPT, LIGOPT, NCEN, NBSTAT &
                ,LIGVOI, KOLVOI, NVOI, IEROLD, IERRAUX, NUM_AFF_CEN, NUM_AFF_OPT &
                ,IEDIT_HIST, IERNEW
!     =======
!      D�but
!     =======
!     ==========================================================
!      Lecture de la liste des stations Hydro avec la Surface :
!     ==========================================================
      NATUR_FICH = "X , Y , Surface des stations Hydro"
      ! CALL OPEOLD(LEC, FICH_X_Y_SURF, IEROLD)
      OPEN (UNIT=LEC, FILE=FICH_X_Y_SURF, STATUS="old", ACTION="read", BLANK="zero", IOSTAT=IEROLD)
      IF (IEROLD /= 0) THEN
         WRITE (LISTIN, 9006, IOSTAT=IERRAUX)    TRIM(FICH_X_Y_SURF), TRIM(NATUR_FICH)
         WRITE (*, 9006, IOSTAT=IERRAUX) TRIM(FICH_X_Y_SURF), TRIM(NATUR_FICH)
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         STOP " "
      ENDIF
      NBSTAT = 0
      READ (LEC, "(A)", IOSTAT=IERRAUX) TITAUX
      WRITE (LISTIN, "(/A)", IOSTAT=IERRAUX) TRIM(TITAUX)
      DO I=1,MAX_STAT
         READ (LEC, *, IOSTAT=IERRAUX) NOM_STAT(I), XP(I), YP(I), SURFP(I)
         IF (IERRAUX /= 0) EXIT
         NOM_STAT(I) = ADJUSTL(NOM_STAT(I))
         NBSTAT = NBSTAT + 1
      ENDDO
      CLOSE (UNIT=LEC, IOSTAT=IERRAUX)
      IEDIT_HIST = 0
      IF (FICH_HISTORIQ /= " ") THEN
!        ============================================
!         �dition des Historiques de D�bits Rivi�res
!        ============================================
         OPEN(UNIT=IOUMAI, FILE=FICH_HISTORIQ, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
         ! CALL OPENEW(IOUMAI, FICH_HISTORIQ, IERNEW, 1)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Historiques D�bits cal."
            WRITE (LISTIN   , 9009, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_HISTORIQ)
            WRITE (*, 9009, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_HISTORIQ)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         ELSE
            IEDIT_HIST = 1
         ENDIF
      ENDIF
      WRITE (LISTIN, 9001, IOSTAT=IERRAUX) NBSTAT
      WRITE (LISTIN, 9002, IOSTAT=IERRAUX)
      IF (IEDIT_HIST >= 1) THEN
         WRITE (IOUMAI, "(A)") "Mailles � historique de d�bits rivi�res des Stations Hydrom�triques."
         WRITE (IOUMAI, "(A)") " #<V7.3># --- Fin du texte libre --- ;" &
                             //" Ne pas modifier/retirer cette ligne"
      ENDIF
!     =====================
!      Balayage des Points
!     =====================
      DO I=1,NBSTAT
         XX = XP(I)
         YY = YP(I)
         SURF_REF = SURFP(I)
!        ========================================
!         Recherche de la Maille qui la contient
!        ========================================
!        =================================================================
!         Initialisation pour le cas o� on ne trouve pas de KOLCEN,LIGCEN
!        =================================================================
         NCEN = 0
         SURF_CEN = 0.
         DIFF_OPT = 0
         KOLOPT = 0
         LIGOPT = 0
         KOLCEN = 0
         LIGCEN = 0
         DIF_SURF = 0.
         NUM_AFF_CEN = 0
         BAL_1: DO LIG=1,NLIG
            YHAUT = YLIG(LIG) + 0.5 * DY_LU(LIG)
            YBAS  = YLIG(LIG) - 0.5 * DY_LU(LIG)
            IF (YY < YBAS) CYCLE
            DO KOL=1,NKOL
               XDROI = XCOL(KOL) + 0.5 * DX_LU(KOL)
               XGAUC = XCOL(KOL) - 0.5 * DX_LU(KOL)
               IF (XX > XDROI) CYCLE
               KOLCEN = KOL
               LIGCEN = LIG
               NCEN = (LIG - 1) * NKOL + KOL
               SURF_CEN = SURF_DRA(NCEN)
               DIF_SURF = SURF_CEN - SURF_REF
               IF ((HYDRO(NCEN) <= 0.).OR.(HYDRO(NCEN) == 9999.)) THEN
!                 =========================================
!                  Maille Non Rivi�re => Code N�gativement
!                 =========================================
                  NUM_AFF_CEN = 0
                  KOLCEN = -KOL
                  LIGCEN = -LIG
               ELSE
                  NUM_AFF_CEN = NINT(HYDRO(NCEN))
               ENDIF
!              ============================
!               Trouv� => Sort du balayage
!              ============================
               EXIT BAL_1
            ENDDO
         ENDDO BAL_1
         KOL = ABS(KOLCEN)
         LIG = ABS(LIGCEN)
!        ======================
!         Examen des 8 voisins
!        ======================
         SELECT CASE (NUM_AFF_CEN)
         CASE (:0)
            DIFF_OPT = 1E15
            SURF_OPT = 0.
            KOLOPT = 0
            LIGOPT = 0
         CASE (1:)
            DIFF_OPT = DIF_SURF
            SURF_OPT = SURF_CEN
            KOLOPT = KOLCEN
            LIGOPT = LIGCEN
         END SELECT
         DO L=-NBRE_VOIS_STATION , +NBRE_VOIS_STATION
            LIGVOI = LIG + L
            DO K=-NBRE_VOIS_STATION , +NBRE_VOIS_STATION
               KOLVOI = KOL + K
               IF ((K == 0).AND.(L == 0)) CYCLE
               NVOI = (LIGVOI - 1) * NKOL + KOLVOI
               IF ((NVOI < 1).OR.(NVOI > NTOT)) CYCLE
!              ================================
!               Si maille Non Rivi�re => Saute
!              ================================
               IF ((HYDRO(NVOI) <= 0.).OR. &
                   (HYDRO(NVOI) == 9999.)) CYCLE
               SURF_VOI = SURF_DRA(NVOI)
               DIF_VOIS = SURF_VOI - SURF_REF
               IF (ABS(DIF_VOIS) < ABS(DIFF_OPT)) THEN
                  DIFF_OPT = DIF_VOIS
                  SURF_OPT = SURF_VOI
                  KOLOPT = KOLVOI
                  LIGOPT = LIGVOI
                  NUM_AFF_OPT = NINT(HYDRO(NVOI))
               ENDIF
            ENDDO
         ENDDO
!        ======================
!         �dition des surfaces
!        ======================
         WRITE (LISTIN, 9003, IOSTAT=IERRAUX) NOM_STAT(I), XX, YY, SURF_REF
         WRITE (LISTIN, 9004, IOSTAT=IERRAUX) ADJUSTR("Ref."), SURF_CEN &
                                            , DIF_SURF, KOLCEN, LIGCEN, NUM_AFF_CEN
         IF ((KOLOPT > 0).AND.(LIGOPT > 0)) THEN
            WRITE (LISTIN, 9005, IOSTAT=IERRAUX) ADJUSTR("Opt. =>") &
                                               , XCOL(KOLOPT), YLIG(LIGOPT), SURF_OPT &
                                               , DIFF_OPT,KOLOPT, LIGOPT,NUM_AFF_OPT
            X_HIST = XCOL(KOLOPT)
            Y_HIST = YLIG(LIGOPT)
         ELSE
            X_HIST = XX
            Y_HIST = YY
         ENDIF
         CALL EDI7CA(CHAR7_X , X_HIST , 1)
         CALL EDI7CA(CHAR7_Y , Y_HIST , 1)
         IF (IEDIT_HIST >= 1) WRITE (IOUMAI, 9007) CHAR7_X, CHAR7_Y, TRIM(NOM_STAT(I))
      ENDDO
      IF (IEDIT_HIST >= 1) THEN
         WRITE (IOUMAI, 9008)
         CLOSE (IOUMAI)
      ENDIF
 9001 FORMAT (/" Nombre de stations hydrom�triques lues = ",I6/)
 9002 FORMAT (/"     Station                         X_ref       Y_ref   Surface" &
              ,"   Er_Surf   Col   Lig  Affl")
 9003 FORMAT (A30,2F12.3,F10.1)
 9004 FORMAT (A30,24X   ,2F10.1,2I6,I5)
 9005 FORMAT (A30,2F12.3,2F10.1,2I6,I5)
 9006 FORMAT (//" *** Le fichier de nom ",A," n'a pas �t� trouv�",T77,"***" &
               /" *** pour les donn�es de ",A,T77,"***"/)
 9007 FORMAT ("  /D�bit_Rivi   /HISTO/   =   /XCOO:X=",A7,"Y=",A7,"P=      1;",A)
 9008 FORMAT (" *** Fin du fichier des 'Mailles � Historique'       ***")
 9009 FORMAT (" Impossible d'ouvrir un fichier ",A," :" &
             /" de nom :",A)
      END SUBROUTINE Verif_Surf_Stat_Hydro

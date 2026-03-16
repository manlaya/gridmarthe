      SUBROUTINE Definit_Sous_Bassins(FICH_COL_LIG_SOUS_BV, FICH_SOUS_BASSIN &
                                    , LEC, LISTIN, IOUMAI &
                                    , PRESEN, HYDRO, NMAI_AVAL &
                                    , DX_LU, DY_LU, NLIG, NKOL, NTOT, X0, Y0)
!===========================================================================
!   ***********************
!   *Definit_Sous_Bassins*            BRGM     B.P. 36009
!   ***********************            45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!===========================================================================
!      Calcul et correction des surfaces des Stations Hydro
!      � partir du fichier des Surfaces Drain�es
!      * En retour : HYDRO() => Grille Marthe avec num�ros des sous-bassins
!===========================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NLIG, NKOL, NTOT, LEC, LISTIN, IOUMAI
      REAL   , DIMENSION(NKOL), INTENT(IN) :: DX_LU
      REAL   , DIMENSION(NLIG), INTENT(IN) :: DY_LU
      REAL   , DIMENSION(NTOT), INTENT(IN) :: PRESEN
      INTEGER, DIMENSION(NTOT), INTENT(IN) :: NMAI_AVAL
      CHARACTER (LEN=*), INTENT(IN) :: FICH_COL_LIG_SOUS_BV, FICH_SOUS_BASSIN
      REAL   , DIMENSION(NTOT), INTENT(OUT) :: HYDRO
      REAL   , INTENT(IN) :: X0, Y0
      CHARACTER (LEN=80), DIMENSION(25) :: WINT_BUFF
      COMMON/WINT_WRITE/WINT_BUFF
!     ========
!      Locaux
!     ========
      INTEGER, PARAMETER :: MAX_STAT = 500
      INTEGER, DIMENSION(MAX_STAT) :: KOL_EXUT, LIG_EXUT, N_EXUT, NAV_EXUT
      REAL   , DIMENSION(MAX_STAT) :: SURF_SOUS_BV
      INTEGER, DIMENSION(NTOT) :: I_SOURCE, IVERI_PASS, LISTE_MAI
      REAL   , DIMENSION(NTOT) :: SURF_MAIL
      INTEGER, DIMENSION(:,:), ALLOCATABLE :: NB_TRAJ_MAIL
      CHARACTER (LEN=80) :: TITAUX, NATUR_FICH
      CHARACTER (LEN=132) :: FICH_SOUS_BASSIN_BLN
      LOGICAL :: OD
      INTEGER :: I, K, L, NAV, LIG, KOL, N, NN, NBSTAT, NUMAVA, KONT, IEDIT, MUET &
               , NUM, IER &
               , IEROLD, IERRAUX, IERNEW, IER_ALLO, N_ABSENT = 100000000
!     =======
!      D�but
!     =======
!     ==========================================================
!      Lecture de la liste KOL_EXUT , LIG_EXUT des stations Hydro
!      c'est � dire des exutoires des sous-bassins
!     ==========================================================
      NATUR_FICH = "Col Lign des exutoires des Sous-Bassins"
      OPEN (UNIT=LEC, FILE=FICH_COL_LIG_SOUS_BV, STATUS="old", ACTION="read", BLANK="zero", IOSTAT=IEROLD)
      ! CALL OPEOLD(LEC, FICH_COL_LIG_SOUS_BV, IEROLD)
      IF (IEROLD /= 0) THEN
         WRITE (LISTIN, 9006, IOSTAT=IERRAUX)    TRIM(FICH_COL_LIG_SOUS_BV), TRIM(NATUR_FICH)
         WRITE (*, 9006, IOSTAT=IERRAUX) TRIM(FICH_COL_LIG_SOUS_BV), TRIM(NATUR_FICH)
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
         STOP " "
      ENDIF
      NBSTAT = 0
      READ (LEC, "(A)", IOSTAT=IERRAUX) TITAUX
      WRITE (LISTIN, "(/A)", IOSTAT=IERRAUX) TRIM(TITAUX)
      DO I=1,MAX_STAT
         READ (LEC, *, IOSTAT=IERRAUX) KOL_EXUT(I), LIG_EXUT(I)
         IF (IERRAUX /= 0) EXIT
!        ==================================================
!         Saute les num�ros de ligne ou colonne incorrects
!        ==================================================
         IF ((KOL_EXUT(I) <= 0).OR.(KOL_EXUT(I) > NKOL).OR.(LIG_EXUT(I) <= 0)) CYCLE
         N = (LIG_EXUT(I) - 1) * NKOL + KOL_EXUT(I)
         IF ((N <= 0).OR.(N > NTOT)) CYCLE
         NBSTAT = NBSTAT + 1
         N_EXUT(NBSTAT) = N
         KOL_EXUT(NBSTAT) = KOL_EXUT(I)
         LIG_EXUT(NBSTAT) = LIG_EXUT(I)
      ENDDO
      CLOSE (UNIT=LEC, IOSTAT=IERRAUX)
      WRITE (LISTIN, 9004) NBSTAT
      IF (NBSTAT <= 0) GO TO 999
      ALLOCATE (NB_TRAJ_MAIL(NTOT,NBSTAT), STAT=IER_ALLO)
      IF (IER_ALLO /= 0) THEN
!        ======================
!         Erreur d'allocations
!        ======================
         IF (LISTIN > 0) WRITE (LISTIN, 9003)
         STOP
      ELSE
         NB_TRAJ_MAIL = N_ABSENT
      ENDIF
      IEDIT = 0
      IF (FICH_SOUS_BASSIN /= " ") THEN
!        ===============================================
!         �dition des Liste de mailles des sous-bassins
!        ===============================================
         OPEN(UNIT=IOUMAI, FILE=FICH_SOUS_BASSIN, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
         ! CALL OPENEW(IOUMAI,FICH_SOUS_BASSIN,IERNEW,1)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Sous_Bassins"
            WRITE (LISTIN   , 9009, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOUS_BASSIN)
            WRITE (*, 9009, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOUS_BASSIN)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0 ,400)
         ELSE
            IEDIT = 1
         ENDIF
      ENDIF
      WRITE (LISTIN, 9001, IOSTAT=IERRAUX) NBSTAT
      WRITE (LISTIN, 9002, IOSTAT=IERRAUX)
      IF (IEDIT >= 1) THEN
         WRITE (IOUMAI, "(A)") "Num_Ordr"//CHAR(9)//"N_Ident"//CHAR(9) &
                             //"N_BV_Aval"//CHAR(9)//"Surf_Elem"//CHAR(9)
      ENDIF
!     =======================
!      Surfaces �l�mentaires
!     =======================
      DO LIG=1,NLIG
         DO KOL=1,NKOL
            N = (LIG - 1) * NKOL + KOL
            SURF_MAIL(N) = DX_LU(KOL) * DY_LU(LIG)
         ENDDO
      ENDDO
!     =======================================================================
!      D�termination de l'aval des Exutoires : Pour l'Arbre ses sous-bassins
!     =======================================================================
      NAV_EXUT(1:NBSTAT) = 0
      DO L=1,NBSTAT
         NN = N_EXUT(L)
         NAV = NN
!        ====================================================
!         On descend d'aval en aval � partir de cet exutoire
!        ====================================================
         IVERI_PASS(:) = 0
         BAL_AV: DO MUET=1,NTOT
            N = NAV
            IF (IVERI_PASS(N) /= 0) THEN
!              =====================================================================
!               � partir de l'exutoire NN : D�j� pass� par cette maille => Boucle !
!               => Fini pour cet Exutoire
!              =====================================================================
               EXIT
            ENDIF
            IVERI_PASS(N) = 1
!           =========================================
!            Examine si cette maille est un exutoire
!           =========================================
            DO K=1,NBSTAT
               IF ((N_EXUT(K) == N).AND.(N_EXUT(K) /= NN)) THEN
!                 =======================================================
!                  On a atteint l'exutoire n�K de la liste des exutoires
!                  (diff�rent de l'exutoire de d�part)
!                  => L'exutoire K est � l'aval de l'exutoire L
!                 =======================================================
                  NAV_EXUT(L) = K
!                 ================================================
!                  On a trouv� l'exutoire dans la maille courante
!                  => On s'arr�te pour cet exutoire
!                 ================================================
                  EXIT BAL_AV
               ENDIF
            ENDDO
            NAV = NMAI_AVAL(N)
            IF ((NAV <= 0).OR.(NAV > NTOT)) EXIT
         ENDDO BAL_AV
      ENDDO
!     ===============================================
!      D�termination des mailles Sources (du bassin)
!     ===============================================
      I_SOURCE(:) = 1
      DO N=1,NTOT
!        ============
!         Pr�sence !
!        ============
         IF ((PRESEN(N) <= 0.).OR.(ABS(PRESEN(N)) == 9999.)) THEN
            I_SOURCE(N) = 0
            CYCLE
         ENDIF
         NUMAVA = NMAI_AVAL(N)
         IF ((NUMAVA > 0).AND.(NUMAVA <= NTOT)) THEN
!           ===========================================
!            La maille N a pour aval la maille NUMAVA
!            => La maille NUMAVA a N pour num�ro Amont
!           ============================================
            I_SOURCE(NUMAVA) = 0
         ENDIF
      ENDDO
!     ==========================================
!      Balayage des mailles Sources (du bassin)
!     ==========================================
      DO NN=1,NTOT
         IF (I_SOURCE(NN) == 0) CYCLE
!        ==================================================================
!         Maille source : On regarde si elle aboutit � une maille exutoire
!        ==================================================================
         LISTE_MAI(:) = 0
         KONT = 0
         NAV = NN
!        ================================================
!         On descend d'aval en aval � partir des sources
!        ================================================
         IVERI_PASS(:) = 0
         BAL_AVAL: DO MUET=1,NTOT
            N = NAV
            IF (IVERI_PASS(N) /= 0) THEN
!              ====================================================================
!               � partir de la source NN : D�j� pass� par cette maille => Boucle !
!               => Fini pour cette Source
!              ====================================================================
               EXIT
            ENDIF
            KONT = KONT + 1
            IF (KONT > NTOT) EXIT
            LISTE_MAI(KONT) = N
            IVERI_PASS(N) = 1
!           =========================================
!            Examine si cette maille est un exutoire
!           =========================================
            DO K=1,NBSTAT
               IF (N_EXUT(K) == N) THEN
!                 ============================================================
!                  On a atteint l'exutoire K de la liste des exutoires
!                  => On marque chaque maille NUM de la liste parcourue
!                     par le nombre de mailles travers�es pour cette exutoire
!                 ============================================================
                  DO L=1,KONT
                     NUM = LISTE_MAI(L)
                     NB_TRAJ_MAIL(NUM , K) = MIN(NB_TRAJ_MAIL(NUM , K) , KONT)
                  ENDDO
!                 ===================================================================
!                  On a trouv� l'exutoire dans la maille courante
!                  => On s'arr�te pour cette source, (car si on poursuivait
!                     on arriverait forc�ment en aval, dans dans un bassin contenant
!                     ce sous-bassin
!                 ===================================================================
                  EXIT BAL_AVAL
               ENDIF
            ENDDO
            NAV = NMAI_AVAL(N)
            IF ((NAV <= 0).OR.(NAV > NTOT)) EXIT
         ENDDO BAL_AVAL
      ENDDO
!     ==================
!      Valorise HYDRO()
!     ==================
      HYDRO(:) = 9999.
      DO K=1,NBSTAT
         KONT = 0
         LISTE_MAI(:) = 0
         DO N=1,NTOT
            IF (NB_TRAJ_MAIL(N , K) == N_ABSENT) CYCLE
            IF (MINVAL(NB_TRAJ_MAIL(N , 1:NBSTAT)) == NB_TRAJ_MAIL(N , K)) THEN
               KONT = KONT + 1
               LISTE_MAI(KONT) = N
               HYDRO(N) = K
            ENDIF
         ENDDO
         SURF_SOUS_BV(K) = SUM(SURF_MAIL( LISTE_MAI(1:KONT) ) )
         WRITE (IOUMAI,*) K,CHAR(9),K,CHAR(9),NAV_EXUT(K),CHAR(9),SURF_SOUS_BV(K),CHAR(9)
      ENDDO
      INQUIRE (UNIT=IOUMAI, OPENED=OD, IOSTAT=IERRAUX)
      IF (OD) CLOSE (UNIT=IOUMAI, IOSTAT=IERRAUX)
      DEALLOCATE (NB_TRAJ_MAIL, STAT=IERRAUX)
      IF (FICH_SOUS_BASSIN /= " ") THEN
!        ===================================================
!         �dition du contour de chaque sous-bassin
!        ===================================================
!        ====================================
!         Addition du suffixe "bln" Toujours
!        ====================================
         ! CALL WRIT_STATUS_BAR("�dition du contour des sous-bassins [.bln]", 0, 0)
         ! CALL PEEK_4_MES(ISTOP , 1)
         CALL Ajout_Toujours_Extens(FICH_SOUS_BASSIN, FICH_SOUS_BASSIN_BLN, "bln")
         OPEN(UNIT=IOUMAI, FILE=FICH_SOUS_BASSIN_BLN, STATUS="replace", ACTION="write", IOSTAT=IERNEW)
         ! CALL OPENEW(IOUMAI , FICH_SOUS_BASSIN_BLN ,IERNEW,1)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Contour des sous-bassins"
            WRITE (LISTIN   , 9009, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOUS_BASSIN_BLN)
            WRITE (*, 9009, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOUS_BASSIN_BLN)
            ! CALL Dial_Message_Wait(WINT_BUFF, 0, 400)
            GO TO 999
         ENDIF
         CALL Masque_des_Sous_Bass(HYDRO, NLIG, NKOL, NTOT, NBSTAT &
          , IER, X0, Y0, IOUMAI &
          , DX_LU, DY_LU)
         INQUIRE (UNIT=IOUMAI, OPENED=OD, IOSTAT=IERRAUX)
         IF (OD) CLOSE (UNIT=IOUMAI, IOSTAT=IERRAUX)
      ENDIF
  999 CONTINUE
#ifndef ENGLISH  
 9001 FORMAT (/" Nombre de sous-bassins � calculer = ",I6/)
 9002 FORMAT (/" Exutoire Colonne, Ligne" &
              ,"   Er_Surf   Col   Lig  Affl")
 9003 FORMAT (/" *** Module de calcul des sous-bassins :" &
              ," Mémoire insuffisante",T77,"***")
 9004 FORMAT (/I0," exutoires de sous-bassins lus"/)
 9006 FORMAT (//" *** Le fichier de nom '",A,"'",T77,"***" &
               /" *** n'a pas été trouvé",T77,"***" &
               /" *** pour les données de '",A,"'",T77,"***"/)
 9009 FORMAT (" Impossible d'ouvrir un fichier ",A," :" &
             /" de nom :",A)
#else
 9001 FORMAT (/" Number of sub-basins to calcaute  = ",I6/)
 9002 FORMAT (/" Outlet Column, Row" &
              ,"   Er_Surf   Col   Lig  Affl")
 9003 FORMAT (/" *** Sub-basin calculation module:" &
              ," Insufficient memory",T77,"***")
 9004 FORMAT (/I0," sub-basin outlets read"/)
 9006 FORMAT (//" *** The file with the name '",A,"'",T77,"***" &
               /" *** was not found",T77,"***" &
               /" *** for the data of '",A,"'",T77,"***"/)
 9009 FORMAT (" Impossible to open a file ",A," :" &
             /" named :",A)
#endif
      END SUBROUTINE Definit_Sous_Bassins
      SUBROUTINE Masque_des_Sous_Bass(HYDRO, NLIG, NKOL, NTOT, NBSTAT &
        , IER, X0, Y0, IOUMAI &
        , DX_LU, DY_LU)
!=======================================================================
!   **********************
!   *Masque_des_Sous_Bass*             BRGM     B.P. 36009
!   **********************             45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      Calcul du Masque des Sous-Bassins
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NLIG, NKOL, NTOT, NBSTAT, IOUMAI
      REAL   , INTENT(IN) :: X0, Y0
      REAL   , DIMENSION(NTOT), INTENT(IN) :: HYDRO
      REAL   , DIMENSION(NKOL), INTENT(IN) :: DX_LU
      REAL   , DIMENSION(NLIG), INTENT(IN) :: DY_LU
      INTEGER, INTENT(OUT) :: IER
!     ========
!      Locaux
!     ========
      REAL   , DIMENSION( MAX(NLIG,NKOL) +1) :: DXCUM, DYCUM
      REAL   , DIMENSION(NTOT) :: PER
      REAL    :: FMANQ, SOM
      INTEGER :: LIG, KOL, LIGAUX, IBASS
!     =======
!      D�but
!     =======
      FMANQ = 9999.
!     ===============================================================
!      Calcul des DX et DY cumul�s => Dans DXCUM(KOL+1),DYCUM(LIG+1)
!      Y_Maxi est en Haut
!     ===============================================================
!     ==========================================================================
!      DXCUM  = Largeur Cumul�e ( DXCUM(1) = 0  DXCUM(NKOL+1) = Largeur Totale)
!      DYCUM  = Hauteur Cumul�e ( DYCUM(1) = Hauteur Totale  DXCUM(NLIG+1) = 0)
!     ==========================================================================
      DYCUM(NLIG+1) = 0.
      SOM  = 0.
      DO LIGAUX=1,NLIG
         LIG = NLIG - LIGAUX + 1
         SOM = SOM + DY_LU(LIG)
         DYCUM(LIG) = SOM
      ENDDO
      DXCUM(1) = 0.
      SOM      = 0.
      DO KOL=1,NKOL
         SOM = SOM + DX_LU(KOL)
         DXCUM(KOL+1) = SOM
      ENDDO
      DO IBASS=1,NBSTAT
!        ================================================================
!         Pour Chaque sous bassin => FMANQ sauf si num�ro du sous vassin
!        ================================================================
         WHERE (NINT(HYDRO) == IBASS)
            PER = HYDRO
         ELSEWHERE
            PER = FMANQ
         ENDWHERE
!        ===========================================
!         Calcul et �criture du Masque de ce bassin
!        ===========================================
         IER = 0
         CALL Masque_Bassin(PER, NLIG, NKOL, IBASS &
            , IER, X0, Y0, IOUMAI, FMANQ, DXCUM, DYCUM)
      ENDDO
      END SUBROUTINE Masque_des_Sous_Bass
      SUBROUTINE Masque_Bassin(PER, NLIG, NKOL, IBASS &
       , IER, X0, Y0, IOU, FMANQ, DXCUM, DYCUM)
!================================================================================
!   ***************
!   *Masque_Bassin*                    BRGM     B.P. 36009
!   ***************                    45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!================================================================================
!      Calcul du Masque Ext�rieur d'une Grille Marthe ; Valeurs Absentes = FMANQ
!      Format d'�dition [.bln] Surfer
!================================================================================
!      En Entr�e :
!     PER()  = Champ dont on veut calculer le masque
!     FMANQ  = Valeur manquante dans le champ => contact masque
!     NLIG   = Nombre de Lignes
!     NKOL   = Nombre de Colonnes
!     IOU    = Unit� logique pour �crire les coordonn�es
!     X0, Y0 = Coordonn�es de l'Origine de la Grille Marthe
!      En Retour :
!     IER    > 0 si erreurs
!================================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: NLIG, NKOL, IOU, IBASS
      REAL   , DIMENSION(*), INTENT(IN) :: PER
      REAL   , DIMENSION( MAX(NLIG,NKOL) +1 ), INTENT(IN) :: DXCUM
      REAL   , DIMENSION( MAX(NLIG,NKOL) +1 ), INTENT(IN) :: DYCUM
      REAL   , INTENT(IN)  :: X0, Y0, FMANQ
      INTEGER, INTENT(OUT) :: IER
      ! CHARACTER (LEN=80), DIMENSION(25) :: WINT_BUFF
      ! COMMON/WINT_WRITE/WINT_BUFF
!     ========
!      Locaux
!     ========
      INTEGER :: IDIMXX
      REAL   , DIMENSION(NLIG*NKOL) :: XM, YM
      REAL   , DIMENSION(NLIG*NKOL) :: XD, YD, XF, YF
      ! CHARACTER (LEN=450) :: QUESTION
      REAL    :: COTEST, XP, YP, XXM, YYM
      INTEGER :: NPOINT, NBSEGM, NPOINT_MOD, IAUXP, IAUYP, IAUX, IAUY, I &
               , LASTXECR, LASTYECR, ISAVE, IERRAUX, NBMAS
!     =======
!      D�but
!     =======
      IER = 0
      NBMAS = 0
      IDIMXX = NLIG * NKOL
!     ==========================================================================
!      DXCUM  = Largeur Cumul�e ( DXCUM(1) = 0  DXCUM(NKOL+1) = Largeur Totale)
!      DYCUM  = Hauteur Cumul�e ( DYCUM(1) = Hauteur Totale  DXCUM(NLIG+1) = 0)
!     ==========================================================================
!     ========================================================================
!      D�termination des segments
!      (Masque des Limites des Mailles)
!      => NBSEGM Segments, de coordonn�es XD, YD, XF, YF
!         Les XD() ,YD() ,XF() ,YF() contiennent en fait des valeurs enti�res
!         exprim�es en Colonne ou ligne
!     ========================================================================
      CALL Masque_Mailles_Limite(PER, NLIG, NKOL, NBSEGM, FMANQ, XD, YD, XF, YF &
                               , IDIMXX, IER)
      IF (IER > 0) THEN
         WRITE (*, 9005) IDIMXX
         ! CALL Dial_Message_Wait(WINT_BUFF, 0, 900)
         IER = 1
         GO TO 999
      ENDIF
      WRITE (*, 9006) NBSEGM
      ! CALL WRIT_STATUS_BAR(QUESTION, 0, 0)
      COTEST = 1.
!     ================================================
!      NBMAS => Nombre de Morceaux de Masques trouv�s
!     ================================================
      NBMAS = 0
      RECOL: DO WHILE (.TRUE.)
         NBMAS = NBMAS + 1
!        ===================================================================
!         Recollage des Segments de Masque
!         En retour : XM(), YM() = Coordonn�es r�elles des Points du Masque
!         N.B. XM(), YM() contiennent ici des valeurs enti�res
!        ===================================================================
!!!!!    CALL Colle_Segments(XD, YD, XF, YF, NBSEGM, COTEST, NPOINT, XM, YM, IDIMXX, IER)
         CALL Colle_Segments(XD, YD, XF, YF, NBSEGM, COTEST, NPOINT, XM, YM, IER)
         IF (NPOINT <= 0) GO TO 999
         IF (IER == 1) GO TO 999
         WRITE (*, 9007) NPOINT
         ! CALL WRIT_STATUS_BAR(QUESTION, 0 , 0)
         IF (NBSEGM /= 0) THEN
            WRITE (*, 9008) NBSEGM
            ! CALL WRIT_STATUS_BAR(QUESTION, 0 , 0)
         ENDIF
         WRITE (*, 9004) NBMAS
         ! CALL WRIT_STATUS_BAR(QUESTION, 0 , 0)
!        ================================
!         Calcul des coordonn�es r�elles
!        ================================
         NPOINT_MOD = 0
         IAUXP = 0
         IAUYP = 0
         LASTXECR = -999999
         LASTYECR = -999999
         XP = 0.
         YP = 0.
         DO I=1,NPOINT
!           ======================================================================
!            � l'arriv�e, les XM(), YM() contiennent en fait des valeurs enti�res
!            car les XD() ,YD() ,XF() ,YF() contenaient des valeurs enti�res
!            Transformation :
!            Les XM(), YM() contiendront les coordonn�es r�elles du masque
!           ======================================================================
            IAUX = NINT(XM(I))
            IAUY = NINT(YM(I))
            XXM = DXCUM(IAUX) + X0
            YYM = DYCUM(IAUY) + Y0
            ISAVE = 0
            IF ((I == 1).OR.(I == NPOINT)) THEN
!              ==========================
!               Premier ou dernier point
!              ==========================
               ISAVE = 1
               IF (I == NPOINT) THEN
!                 ========================================================
!                  Dernier point : Il faut enregistrer le point pr�c�dent
!                 ========================================================
                  IF (NPOINT_MOD > 0) THEN
                     IF ((XM(NPOINT_MOD) /= XP).OR.(YM(NPOINT_MOD) /= YP)) THEN
                        NPOINT_MOD = NPOINT_MOD + 1
                        XM(NPOINT_MOD) = XP
                        YM(NPOINT_MOD) = YP
                     ENDIF
                  ENDIF
               ENDIF
!              ==================================================================
!               Il faut toujours enregistrer le premier ou dernier point courant
!              ==================================================================
               IAUXP = IAUX
               IAUYP = IAUY
               XP = XXM
               YP = YYM
            ELSE
!              ==========================================================
!               Point interm�diaire => On �limine les �ventuels Doublons
!              ==========================================================
               IF ((IAUX == IAUXP).AND.(IAUY == IAUYP)) CYCLE
            ENDIF
            IF (ISAVE == 0) THEN
!              =========================================================
!               Si les 2 coordonn�es ont chang� depuis l'enregistrement
!               Il faudra enregistrer le Point Pr�c�dent
!              =========================================================
               IF ((IAUX /= LASTXECR).AND.(IAUY /= LASTYECR)) ISAVE = 1
            ENDIF
            IF (ISAVE == 1) THEN
!              ================================================
!               Il faut enregistrer le Point Pr�c�dent
!               et noter que ces coordonn�es sont enregistr�es
!              ================================================
               NPOINT_MOD = NPOINT_MOD + 1
               XM(NPOINT_MOD) = XP
               YM(NPOINT_MOD) = YP
               LASTXECR = IAUXP
               LASTYECR = IAUYP
            ENDIF
            IAUXP = IAUX
            IAUYP = IAUY
            XP = XXM
            YP = YYM
         ENDDO
         NPOINT = NPOINT_MOD
!        =========================
!         �dition des coordonn�es
!        =========================
         WRITE (IOU, 9003) NPOINT,IBASS
         DO I=1,NPOINT
            WRITE (IOU, "(1P,G15.7,G15.7)", IOSTAT=IERRAUX) XM(I), YM(I)
         ENDDO
         IF (NBSEGM > 1) CYCLE RECOL
         EXIT
      ENDDO RECOL
  999 CONTINUE
 9003 FORMAT (" ",I0," 0 Mask_Zone_",I0," xy")
#ifndef ENGLISH
 9004 FORMAT (" masque calcul�  partie n� ",I0)
 9005 FORMAT (" * Tableaux sous-dimensionn�s � ",I0,"      *" &
             /30X," * dans la routine Masque_Bassin *")
 9006 FORMAT (" ",I0," segments masque")
 9007 FORMAT (" ",I0," points de Masque")
 9008 FORMAT (" ",I0," segments restants")
#else

9004 FORMAT (" Mask calculated part no: ",I0)
9005 FORMAT (" * Out of memory : array dimension (",I0,") too small *" &
            /30X," * in routine Masque_Bassin  *")
9006 FORMAT (" ",I0," mask segments")
9007 FORMAT (" ",I0," mask points")
9008 FORMAT (" ",I0," remaining segments")
#endif
      END SUBROUTINE Masque_Bassin
      SUBROUTINE Masque_Mailles_Limite(PER, NLIG, NKOL, NBSEGM, FMANQ, XD, YD, XF, YF &
                          , IDIMXX, IER)
!=======================================================================
!   ***********************
!   *Masque_Mailles_Limite*             BRGM     B.P. 36009
!   ***********************             45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      D�termination des Segments : Limites des Mailles
!      IDIMXX = Dimension des tableaux XD(), YD(), XF(), YF()
!             = Nombre maxi NBSEGM de segments possibles
!       En Retour :
!      NBSEGM = Nombre de Segments
!      XD(), YD() = Coordonn�es des D�buts de segments
!      XF(), YF() = Coordonn�es des Fins   de segments
!      IER = 1 si erreur : sous-dimensionn�
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NLIG, NKOL, IDIMXX
      REAL   , DIMENSION(*), INTENT(IN) :: PER
      REAL   , DIMENSION(*), INTENT(OUT) :: XD, YD, XF, YF
      INTEGER, INTENT(OUT) :: NBSEGM
      INTEGER, INTENT(OUT) :: IER
      REAL   , INTENT(IN)  :: FMANQ
!     ========
!      Locaux
!     ========
      INTEGER :: KONT, LIG, KOL, N, IND, NN, NS, NO, NE, INORD, ISUD, IEST, IOUES
      REAL    :: YN, YS, XO, XE
!     =======
!      D�but
!     =======
      IER = 0
      NBSEGM = 0
      KONT = 0
      DO LIG=1,NLIG
         IND = (LIG - 1) * NKOL
         YN = REAL(LIG)
         YS = REAL(LIG+1)
         DO KOL=1,NKOL
            N =IND + KOL
            IF (ABS(PER(N)) /= ABS(FMANQ)) THEN
               XO = REAL(KOL)
               XE = REAL(KOL+1)
               NN = N - NKOL
               NS = N + NKOL
               NO = N - 1
               NE = N + 1
!              ======
!               Nord
!              ======
               INORD = 1
               IF (LIG /= 1) THEN
                  INORD = 0
                  IF (ABS(PER(NN)) == ABS(FMANQ)) INORD = 1
               ENDIF
               IF (INORD == 1) THEN
                  KONT = KONT + 1
                  IF (KONT > IDIMXX) THEN
                     IER = 1
                     GO TO 999
                  ENDIF
                  XD(KONT) = XO
                  YD(KONT) = YN
                  XF(KONT) = XE
                  YF(KONT) = YN
               ENDIF
!              ======
!               Sud
!              ======
               ISUD = 1
               IF (LIG /= NLIG) THEN
                  ISUD = 0
                  IF (ABS(PER(NS)) == ABS(FMANQ)) ISUD = 1
               ENDIF
               IF (ISUD == 1) THEN
                  KONT = KONT + 1
                  IF (KONT > IDIMXX) THEN
                     IER = 1
                     GO TO 999
                  ENDIF
                  XD(KONT) = XO
                  YD(KONT) = YS
                  XF(KONT) = XE
                  YF(KONT) = YS
               ENDIF
!              ======
!               Ouest
!              ======
               IOUES = 1
               IF (KOL /= 1) THEN
                  IOUES = 0
                  IF (ABS(PER(NO)) == ABS(FMANQ)) IOUES = 1
               ENDIF
               IF (IOUES == 1) THEN
                  KONT = KONT + 1
                  IF (KONT > IDIMXX) THEN
                     IER = 1
                     GO TO 999
                  ENDIF
                  XD(KONT) = XO
                  YD(KONT) = YN
                  XF(KONT) = XO
                  YF(KONT) = YS
               ENDIF
!              ======
!               Est
!              ======
               IEST = 1
               IF (KOL /= NKOL) THEN
                  IEST = 0
                  IF (ABS(PER(NE)) == ABS(FMANQ)) IEST = 1
               ENDIF
                  IF (IEST == 1) THEN
                  KONT = KONT + 1
                  IF (KONT > IDIMXX) THEN
                     IER = 1
                     GO TO 999
                  ENDIF
                  XD(KONT) = XE
                  YD(KONT) = YN
                  XF(KONT) = XE
                  YF(KONT) = YS
               ENDIF
            ENDIF
         ENDDO
      ENDDO
      NBSEGM = KONT
  999 CONTINUE
      END SUBROUTINE Masque_Mailles_Limite

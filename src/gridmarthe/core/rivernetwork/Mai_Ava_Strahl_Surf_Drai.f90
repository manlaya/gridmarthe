      MODULE MOD_RESEAU_8_DIREC_STRAHL
!=======================================================================
!   ***************************
!   *MOD_RESEAU_8_DIREC_STRAHL*        BRGM    B.P. 36009
!   **************************        45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 02/04/2018
!=======================================================================
!      Calcul de R�seaux Strahler
!=======================================================================
        TYPE T_RESEAU_8_DIR_STRAHL
!          =========================================
!           Param�tres pour calcul R�seau Strahler
!           N.B. 8 directions => 7 amonts possibles
!          =========================================
           INTEGER :: NUMAVA = 0
           INTEGER, DIMENSION(7) :: NUMAMO = 0
           INTEGER :: LIS_SOUR = 0
           INTEGER :: ORDR_TRC = 0
           INTEGER :: LIS_JOIN = 0
        END TYPE T_RESEAU_8_DIR_STRAHL
!       ===============
!        Derived types
!       ===============
        TYPE (T_RESEAU_8_DIR_STRAHL), DIMENSION(:), TARGET, ALLOCATABLE :: RESEAU_RUI
        TYPE (T_RESEAU_8_DIR_STRAHL), DIMENSION(:), POINTER :: P_RESEAU_STRAHL
      END MODULE MOD_RESEAU_8_DIREC_STRAHL
      SUBROUTINE Mai_Ava_Strahl_Surf_Drai(SURF_DRA, PRESEN, MAI_RUIS_AVA &
              , NLIG, NKOL, NTOT, LISTIN, DX_LU, DY_LU)
!===========================================================================
!   **************************
!   *Mai_Ava_Strahl_Surf_Drai*         BRGM     B.P. 36009
!   **************************         45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 02/04/2018
!===========================================================================
!      Calcule la Surface Drain�e : M�thode Strahler
!      � partir de :
!       En entr�e :
!      * Pr�sence : PRESEN(NTOT)
!      * Num�ro MAI_RUIS_AVA (1:NTOT) de la maille aval
!      LISTIN = IUL Pour messages
!      DX_LU,DY_LU = Dimensions des mailles
!       En Retour :
!      SURF_DRA(NTOT) = Surface drain�e par les mailles en amont
!                       + surface de la maille elle m�me
!                     = Surface Drain�e en Amont de l'exutoire de la maille
!===========================================================================
      USE MOD_RESEAU_8_DIREC_STRAHL, ONLY : RESEAU_RUI, P_RESEAU_STRAHL
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NLIG, NKOL, NTOT, LISTIN
      INTEGER, DIMENSION(NTOT), INTENT(IN)  :: MAI_RUIS_AVA
      REAL   , DIMENSION(NTOT), INTENT(IN)  :: PRESEN
      REAL   , DIMENSION(NKOL), INTENT(IN)  :: DX_LU
      REAL   , DIMENSION(NLIG), INTENT(IN)  :: DY_LU
      REAL   , DIMENSION(NTOT), INTENT(OUT) :: SURF_DRA
!     ========
!      Locaux
!     ========
      INTEGER ,PARAMETER :: NB_AMONT_MAX = 7
      INTEGER, DIMENSION(NB_AMONT_MAX , NTOT) :: MAI_RUIS_AMO
      INTEGER, DIMENSION(NTOT) :: LIS_RUIS_SOUR
      INTEGER, DIMENSION(NTOT) :: LIS_RUIS_JOIN, NORDR_MAI_RUIS
      INTEGER :: NBJOIN_RIVDRA, NORDR_MAXRIVDRA
      INTEGER :: LIG, KOL, N, IERRAUX
      INTEGER :: NU_DS_COUCH, NUMAVA, K, NB_MAI_SOURC_RUIS, ISOURC, NUMAMO, IER_ALLO
!     =======
!      D�but
!     =======
!     ===============================================================
!      D�termination du num�ro des mailles Amont : Op�ration Inverse
!      � partir de MAI_RUIS_AVA()
!     ===============================================================
      ! CALL WRIT_STATUS_BAR("Calcul des surfaces drain�es : Num�ros Amonts", 0, 0)
!     ================
!      Initialisation
!     ================
      MAI_RUIS_AMO(:,:) = 0
      BAL_MAI2: DO NU_DS_COUCH=1,NTOT
!        ============
!         Pr�sence !
!        ============
         IF ((PRESEN(NU_DS_COUCH) <= 0.).OR.(ABS(PRESEN(NU_DS_COUCH)) == 9999.)) CYCLE
         NUMAVA = MAI_RUIS_AVA(NU_DS_COUCH)
         IF ((NUMAVA > 0).AND.(NUMAVA <= NTOT)) THEN
!           =====================================================
!            La maille NU_DS_COUCH a pour aval la maille NUMAVA
!            => La maille NUMAVA a NU_DS_COUCH pour num�ro Amont
!           =====================================================
            DO K=1,NB_AMONT_MAX
               IF (MAI_RUIS_AMO(K , NUMAVA) == 0) THEN
!                 ===========
!                  Une place
!                 ===========
                  MAI_RUIS_AMO(K , NUMAVA) = NU_DS_COUCH
                  CYCLE BAL_MAI2
               ENDIF
            ENDDO
!           ============================================
!            Pas de place (plus de NB_AMONT_MAX amonts)
!           ============================================
            IF (LISTIN > 0) THEN
               LIG = (NUMAVA - 1) / NKOL + 1
               KOL = NUMAVA - (LIG - 1) * NKOL
               WRITE (LISTIN, 9002, IOSTAT=IERRAUX) KOL, LIG, NB_AMONT_MAX
            ENDIF
         ENDIF
      ENDDO BAL_MAI2
!     ===============================================================================
!      D�termination des mailles Sources pour le ruissellement :
!      � partir de MAI_RUIS_AMO(1:NB_AMONT_MAX,*) = 0 et MAI_RUIS_AVA >= 0 (pas < 0)
!      N.B. Si MAI_RUIS_AVA < 0 (= -1) => En dehors du domaine => Pas Source
!      Liste des Sources => : NB_MAI_SOURC_RUIS , LIS_RUIS_SOUR
!     ===============================================================================
      ! CALL WRIT_STATUS_BAR("Calcul des surfaces drain�es : Sources", 0, 0)
      NB_MAI_SOURC_RUIS = 0
      DO NU_DS_COUCH=1,NTOT
         ISOURC = 1
!        ============
!         Pr�sence !
!        ============
         IF ((PRESEN(NU_DS_COUCH) <= 0.).OR. &
         (ABS(PRESEN(NU_DS_COUCH)) == 9999.)) THEN
!           =======================
!            Hors maillage surface
!           =======================
            ISOURC = 0
            CYCLE
         ENDIF
         IF (MAI_RUIS_AVA(NU_DS_COUCH) <= -1) THEN
!           =======================
!            Hors maillage surface
!           =======================
            ISOURC = 0
            CYCLE
         ENDIF
         BAL_3AFF: DO K=1,NB_AMONT_MAX
            NUMAMO = MAI_RUIS_AMO(K , NU_DS_COUCH)
!           =================================================
!            NUMAMO est le num�ro d'ordre d'un Tron�on Amont
!           =================================================
            IF (NUMAMO > 0) THEN
!              =========================
!               Ce n'est pas une Source
!              =========================
               ISOURC = 0
               EXIT BAL_3AFF
            ENDIF
         ENDDO BAL_3AFF
         IF (ISOURC == 1) THEN
!           =======================================================
!            NB_MAI_SOURC_RUIS = Simplement ordre o� on les trouve
!           =======================================================
            NB_MAI_SOURC_RUIS = NB_MAI_SOURC_RUIS + 1
            LIS_RUIS_SOUR(NB_MAI_SOURC_RUIS) = NU_DS_COUCH
         ENDIF
      ENDDO
      IF (LISTIN > 0) THEN
          write (LISTIN, *) NB_MAI_SOURC_RUIS," Mailles Sources"
          write (LISTIN, *) COUNT((PRESEN(1:NTOT) > 0.).AND. &
                           (ABS(PRESEN(1:NTOT)) /= 9999.))," Mailles dans le domaine"
      ENDIF
      ! CALL WRIT_STATUS_BAR("Calcul des surfaces drain�es : Ordres de Strahler", 0, 0)
!     ==============================================================================
!      Charge les donn�es n�cessaires pour Strahler sur Ruissellement Superficiel :
!      MAI_RUIS_AVA , LIS_RUIS_SOUR , MAI_RUIS_AMO
!     ==============================================================================
      ALLOCATE (RESEAU_RUI(NTOT), STAT=IER_ALLO)
      IF (IER_ALLO /= 0) THEN
!        ======================
!         Erreur d'allocations
!        ======================
         IF (LISTIN > 0) WRITE (LISTIN, 9001)
         STOP
      ENDIF
!     ==============================
!      Charge ce qui est n�cessaire
!     ==============================
      RESEAU_RUI(1:NTOT)%NUMAVA   = MAI_RUIS_AVA(1:NTOT)
      RESEAU_RUI(1:NTOT)%LIS_SOUR = LIS_RUIS_SOUR(1:NTOT)
      DO N=1,NTOT
         RESEAU_RUI(N)%NUMAMO(1:NB_AMONT_MAX) = MAI_RUIS_AMO(1:NB_AMONT_MAX , N)
      ENDDO
!     ==========
!      Pointeur
!     ==========
      P_RESEAU_STRAHL => RESEAU_RUI
!     ================================================
!      Calcul des Ordres de Strahler et des jonctions
!     ================================================
      CALL ORDRIV_8_DIR_STRAHL(LISTIN, NTOT, NB_MAI_SOURC_RUIS, NB_AMONT_MAX &
                        , NBJOIN_RIVDRA, NORDR_MAXRIVDRA)
!     ========================================================
!      Recup�re NORDR_MAI_RUIS et LIS_RUIS_JOIN
!      � partir de %LIS_JOIN et %ORDR_TRC qui ont �t� d�finis
!     ========================================================
      NORDR_MAI_RUIS(1:NTOT) = RESEAU_RUI(1:NTOT)%ORDR_TRC
      LIS_RUIS_JOIN (1:NTOT) = RESEAU_RUI(1:NTOT)%LIS_JOIN
      DEALLOCATE (RESEAU_RUI,STAT=IERRAUX)
      NULLIFY(P_RESEAU_STRAHL)
!     ==============================
!      Calcul des Surfaces Drain�es
!     ==============================
      ! CALL WRIT_STATUS_BAR("Calcul des surfaces drain�es : Strahler => Surfaces", 0, 0)
      CALL BAL_MAI_8_DIR_RUIS(NTOT, NB_AMONT_MAX, NORDR_MAXRIVDRA, NBJOIN_RIVDRA, NLIG, NKOL &
            , MAI_RUIS_AMO, LIS_RUIS_JOIN, NORDR_MAI_RUIS, MAI_RUIS_AVA, SURF_DRA &
            , DX_LU,DY_LU)
#ifndef ENGLISH
 9001 FORMAT (/" *** Module de calcul des ordres de Strahler :" &
              ," M�moire insuffisante",T77,"***")
 9002 FORMAT (/" Maille : Colonne =",I5," Ligne =",I5," => Plus de ",I2," amonts (creux ?)")
#else

9001 FORMAT (/" *** Strahler order calculation: Out of Memory",T77,'***')
9002 FORMAT (/" Cell : Column =",I5," Row =",I5," => More than ",I2," upstreams (depression ?)")
#endif
      END SUBROUTINE Mai_Ava_Strahl_Surf_Drai
      SUBROUTINE ORDRIV_8_DIR_STRAHL(LISTIN, NBMRIVDRA, NBSOURC_RIVDRA, NB_AMONT_MAX &
                        , NBJOIN_RIVDRA, NORDR_MAXRIVDRA)
!=============================================================================
!   *********************
!   *ORDRIV_8_DIR_STRAHL*              BRGM     B.P. 36009
!   *********************              45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 02/04/2018
!=============================================================================
!      Calcul des num�ros d'Ordre de Strahler et de la Liste des Jonctions
!      N.B. Passer en arguments NBMRIVDRA , NBSOURC_RIVDRA
!           Car appel avec d'autres arguments pour les drains
!      Utilise   : %LIS_SOUR , %NUMAMO(NB_AMONT_MAX) , %NUMAVA
!      En retour : NBJOIN_RIVDRA,NORDR_MAXRIVDRA
!                  %LIS_JOIN = Liste ordonn�e des NBJOIN_RIVDRA jonctions
!                  %ORDR_TRC = Ordre de Strahler des NBMRIVDRA tron�ons
!      *** Att : Routine utilis�e �galement pour Ruissellement de Surface ***
!=============================================================================
!      Version pour Calcul du R�seau Hydrographique Hors MARTHE
!=============================================================================
      USE MOD_RESEAU_8_DIREC_STRAHL, ONLY : P_RESEAU_STRAHL
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: LISTIN, NBMRIVDRA, NBSOURC_RIVDRA, NB_AMONT_MAX
      INTEGER, INTENT(OUT) :: NBJOIN_RIVDRA, NORDR_MAXRIVDRA
!     ============
!      Interfaces
!     ============
      ! INTERFACE
      !   SUBROUTINE PEEK_4_MES(ISTOP, IMMEDIAT)
      !    INTEGER, INTENT(IN)  :: IMMEDIAT
      !    INTEGER, INTENT(OUT) :: ISTOP
      !   END SUBROUTINE PEEK_4_MES
      ! END INTERFACE
!     =====================
!      Tableau automatique
!     =====================
      INTEGER, DIMENSION(NBMRIVDRA) :: NUMJOIN, IVERI_PASS
!     ========
!      Locaux
!     ========
      ! CHARACTER (LEN=80) :: TITAUX
      REAL    :: POURC
      INTEGER :: ITER, MUET, K, IR, IR_PRE, NAV, NAM, NORDR, IVARIA, MEME_ORDR_AM &
               , NORDAM_MAX, ISOUR, NBAM &
               , IULERR_FICT ,KONT, KONT_AUX, IPOURC &
               , NITER_MAX
!     =======
!      D�but
!     =======
      POURC = 0.01
      NBJOIN_RIVDRA   = 0
      NORDR_MAXRIVDRA = 0
      IF (NBMRIVDRA <= 0) GO TO 999
      IULERR_FICT = 0
!     ========================================
!      Calcul it�ratif de l'ordre de Strahler
!     ========================================
      NUMJOIN(1:NBMRIVDRA) = 0 !! #########" pas n�cess (fait plus loin) ####
      P_RESEAU_STRAHL(1:NBMRIVDRA)%ORDR_TRC = 0
!     ============================================
!      On fait uniquement une Seule It�ration :
!      car pas n�cessaire sauf si d�rivations ...
!     ============================================
      NITER_MAX = 1
      DO ITER=1,NITER_MAX
         IVARIA = 0
!        =====================
!         On part des sources
!        =====================
         KONT = 0
         KONT_AUX = 0
         DO ISOUR=1,NBSOURC_RIVDRA
!           ===================================
!            Contr�le du calcul (permet arr�t)
!           ===================================
            KONT = KONT + 1
            KONT_AUX = KONT_AUX + 1
            IF (KONT_AUX >= NINT(POURC * NBSOURC_RIVDRA)) THEN
               KONT_AUX = 0
               IPOURC = NINT(100. * REAL(KONT) / NBSOURC_RIVDRA)
               ! WRITE (TITAUX,*, IOSTAT=IERRAUX) "Calcul des surfaces drain�es Iter=",ITER," ; ",IPOURC," % Sources"
               ! CALL WRIT_STATUS_BAR(TRIM(TITAUX), 0, 0)
               ! CALL PEEK_4_MES(ISTOP, 1)
            ENDIF
            NORDR = 0
            IR  = P_RESEAU_STRAHL(ISOUR)%LIS_SOUR
            NAV = IR
            IR_PRE = 0
!           =================================
!            On descend a partir des sources
!           =================================
            DO MUET=1,NBMRIVDRA
               IR = NAV
               NBAM = COUNT( P_RESEAU_STRAHL(IR)%NUMAMO(1:NB_AMONT_MAX) > 0)
               SELECT CASE (NBAM)
               CASE(0)
!                 ==============================
!                  0 Amont => Source => Ordre 1
!                 ==============================
                  NORDR = 1
               CASE(1)
!                 ===============================================
!                  1 seul Amont => Pas branchement => M�me ordre
!                 ===============================================
               CASE(2:)
!                 =======================================
!                  Plusieurs amonts => R�gle de Strahler
!                  On examine les "Autres Amonts"
!                 =======================================
                  NORDAM_MAX = 0
                  DO K=1,NB_AMONT_MAX
                     NAM = P_RESEAU_STRAHL(IR)%NUMAMO(K)
                     IF (NAM == IR_PRE) CYCLE
                     IF (NAM == 0) EXIT
                     NORDAM_MAX = MAX( NORDAM_MAX, P_RESEAU_STRAHL(NAM)%ORDR_TRC )
                  ENDDO
                  IF (NORDAM_MAX < NORDR) THEN
!                    ================
!                     Ordre inchang�
!                    ================
                  ELSE IF (NORDAM_MAX == NORDR) THEN
!                    ================================
!                     Plusieurs Amonts du m�me ordre
!                    ================================
                     NORDR = NORDR + 1
                  ELSE IF (NORDAM_MAX > NORDR) THEN
                     NORDR = NORDAM_MAX
                  ENDIF
               END SELECT
               IR_PRE = IR
!              =================================
!               On ne peut qu'augmenter l'ordre
!              =================================
               NORDR = MAX(NORDR , P_RESEAU_STRAHL(IR)%ORDR_TRC)
               IVARIA = IVARIA + ABS(P_RESEAU_STRAHL(IR)%ORDR_TRC - NORDR)
               P_RESEAU_STRAHL(IR)%ORDR_TRC = NORDR
               NAV = P_RESEAU_STRAHL(IR)%NUMAVA
               IF (NAV <= 0) EXIT
            ENDDO
         ENDDO
!        ====================
!         Test si Variations
!        ====================
         IF (IVARIA == 0) EXIT
      ENDDO
      NORDR_MAXRIVDRA = MAXVAL( P_RESEAU_STRAHL(1:NBMRIVDRA)%ORDR_TRC )
!     ======================================================
!      Mailles Ext�rieures : %NUMAVA = -1 => On prend >= 0)
!     ======================================================
      WRITE (LISTIN, 9006) COUNT(P_RESEAU_STRAHL(1:NBMRIVDRA)%NUMAVA >= 0)
      IF ((NITER_MAX > 1).AND.(ITER > 1)) THEN
         WRITE (LISTIN,9002) ITER, IVARIA
      ENDIF
!     =========================================================
!      Calcul des Jonctions � partir des Ordres
!      P_RESEAU_STRAHL(IR)%ORDR_TRC contient le Num�ro d'Ordre
!     =========================================================
      NUMJOIN(1:NBMRIVDRA) = 0
      P_RESEAU_STRAHL(1:NBMRIVDRA)%LIS_JOIN = 0
      IVERI_PASS(1:NBMRIVDRA) = 0
!     =====================
!      On part des Sources
!     =====================
      DO ISOUR=1,NBSOURC_RIVDRA
         NORDR = 0
         IR  = P_RESEAU_STRAHL(ISOUR)%LIS_SOUR
         NAV = IR
!        =================================
!         On descend � partir des Sources
!        =================================
         DO MUET=1,NBMRIVDRA
            IR = NAV
            IF (IVERI_PASS(IR) /= 0) THEN
!              =====================================
!               D�j� pass� par ce d�but de Jonction
!               => Fini pour cette Source
!              =====================================
               EXIT
            ENDIF
            IF (P_RESEAU_STRAHL(IR)%ORDR_TRC /= NORDR) THEN
!              =================================================
!               Ordre diff�rent + Pas d�j� pass�
!               => Nouvelle Jonction pas un Amont du m�me ordre
!              =================================================
               NORDR = P_RESEAU_STRAHL(IR)%ORDR_TRC
!              =====================================================
!               On regarde s'il n'existe pas un Amont du m�me Ordre
!              =====================================================
               MEME_ORDR_AM = 0
               DO K=1,NB_AMONT_MAX
                  NAM = P_RESEAU_STRAHL(IR)%NUMAMO(K)
                  IF (NAM <= 0) EXIT
                  IF (P_RESEAU_STRAHL(NAM)%ORDR_TRC == NORDR) THEN
                     MEME_ORDR_AM = 1
                     EXIT
                  ENDIF
               ENDDO
               IF (MEME_ORDR_AM == 0) THEN
!                 ===========================
!                  Pas d'Amont du m�me ordre
!                 ===========================
                  NUMJOIN(IR) = NORDR
                  IVERI_PASS(IR) = 1
               ENDIF
            ENDIF
            NAV = P_RESEAU_STRAHL(IR)%NUMAVA
            IF (NAV <= 0) EXIT
         ENDDO
      ENDDO
!     ==============================
!      Liste ordonn�e des Jonctions
!     ==============================
      NBJOIN_RIVDRA = 0
      DO NORDR=1,NORDR_MAXRIVDRA
         DO IR=1,NBMRIVDRA
            IF (NUMJOIN(IR) /= NORDR) CYCLE
            NBJOIN_RIVDRA = NBJOIN_RIVDRA + 1
            P_RESEAU_STRAHL(NBJOIN_RIVDRA)%LIS_JOIN = IR
         ENDDO
      ENDDO
      IF (LISTIN > 0) WRITE (LISTIN,9001) NBJOIN_RIVDRA,NORDR_MAXRIVDRA
  999 CONTINUE
#ifndef ENGLISH
 9001 FORMAT ( I10," = Nombre de jonctions du r�seau" &
              /I10," = Ordre de Strahler maximal")
 9002 FORMAT (/I10," = Nombre de passages n�cessaires pour calculer les ordres de Strahler" &
              /I10," = Nombre d'�carts r�siduels")
 9006 FORMAT (/" Mailles du domaine de surface (",I8," mailles)")
#else

9001 FORMAT ( I10," = Number of Junctions in the network" &
             /I10," = Maximum Strahler order")
9002 FORMAT (/I10," = Number of pass used to compute the Strahler orders" &
             /I10," = Number of residual variations")
9006 FORMAT (/" Surface domain cells (",I5," cells)")
#endif
      END SUBROUTINE ORDRIV_8_DIR_STRAHL
      SUBROUTINE BAL_MAI_8_DIR_RUIS(NTOT, NB_AMONT_MAX, NORDR_MAXRUIS, NBJOIN_RUIS, NLIG, NKOL &
            , MAI_RUIS_AMO, LIS_RUIS_JOIN, NORDR_MAI_RUIS, MAI_RUIS_AVA, SURF_DRA &
            , DX_LU, DY_LU)
!=======================================================================
!   ********************
!   *BAL_MAI_8_DIR_RUIS*               BRGM     B.P. 36009
!   ********************               45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 02/04/2018
!=======================================================================
!      Balayage des Mailles de Ruissellement (Strahler)
!      et calcul des Surfaces Amonts des Affluents (pour �dition)
!      N.B. Routine appel�e uniquement quand : ISTRAHL_RUISS > 0
!           c'est � dire Ruissellement Superficiel par Strahler
!=======================================================================
!      Version pour Calcul du r�seau Hydrographique Hors MARTHE
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NTOT, NB_AMONT_MAX, NORDR_MAXRUIS, NBJOIN_RUIS, NLIG, NKOL
      INTEGER, DIMENSION(NB_AMONT_MAX , NTOT), INTENT(IN) :: MAI_RUIS_AMO
      INTEGER, DIMENSION(NTOT), INTENT(IN) :: LIS_RUIS_JOIN, NORDR_MAI_RUIS &
                                            , MAI_RUIS_AVA
      REAL   , DIMENSION(NKOL), INTENT(IN)  :: DX_LU
      REAL   , DIMENSION(NLIG), INTENT(IN)  :: DY_LU
      REAL   , DIMENSION(NTOT), INTENT(OUT) :: SURF_DRA
!     ========
!      Locaux
!     ========
      ! CHARACTER (LEN=80) :: TITAUX
      REAL    :: SURFMAI
      INTEGER :: IOR, IJOIN, MUET, IDEBUT_JOIN, IDBJOIN, IR, NAV, K, NUMAMO, N, LIG, KOL !&
               !  ,IERRAUX, ISTOP
!     =======
!      D�but
!     =======
      SURF_DRA(1:NTOT) = 0.
      IDEBUT_JOIN = 1
      BAL_ORDR: DO IOR=1,NORDR_MAXRUIS
!        ===================================
!         Boucle sur les Ordres de Strahler
!        ===================================
         IDBJOIN = IDEBUT_JOIN
!        ================================
!         Initialise IDEBUT_JOIN au maxi
!        ================================
         IDEBUT_JOIN = NBJOIN_RUIS
!        ===================================
!         Contr�le du calcul (permet arr�t)
!        ===================================
         ! WRITE (TITAUX, *, IOSTAT=IERRAUX) "Calcul des surfaces amonts Ordre=",IOR
         ! CALL WRIT_STATUS_BAR(TRIM(TITAUX), 0, 0)
         ! CALL PEEK_4_MES(ISTOP, 1)
         BAL_JOIN: DO IJOIN=IDBJOIN,NBJOIN_RUIS
!           ==========================================
!            Balaye les Jonctions de l'Ordre en cours
!           ==========================================
            IR = LIS_RUIS_JOIN(IJOIN)
!           ================================================================
!            Passe � la jonction suivante si pas Num�ro de l'Ordre en cours
!           ================================================================
            IF (NORDR_MAI_RUIS(IR) /= IOR) CYCLE BAL_JOIN
            NAV = IR
            TRONCON: DO MUET=1,NTOT
               IR = NAV
!              ==========================================================
!               N.B. MAI_RUIS_AVA < 0 (-1 ou -9999) en dehors du domaine
!                    On garde cependant MAI_RUIS_AVA = 0 (exutoire)
!              ==========================================================
               IF (MAI_RUIS_AVA(IR)  < 0) EXIT TRONCON
!              ================================================================
!               Passe � la jonction suivante si pas Num�ro de l'Ordre en cours
!               => Optimal car un segment a un num�ro d'Ordre unique
!                  donc d�s le premier tron�on quitte si pas bon
!              ================================================================
               IF (NORDR_MAI_RUIS(IR) < IOR) EXIT TRONCON
               IF (NORDR_MAI_RUIS(IR) == IOR+1) THEN
!                 =================================================
!                  D�passe => M�morise le numero de la
!                             premi�re Jonction de l'Ordre Suivant
!                 =================================================
                  IDEBUT_JOIN = MIN(IDEBUT_JOIN , IJOIN)
                  EXIT TRONCON
               ENDIF
               IF (NORDR_MAI_RUIS(IR) > IOR + 1) THEN
                  EXIT TRONCON
               ENDIF
!              ========================================
!               Coeur du calcul
!               N.B. Ici IR est le num�ro de la Maille
!              ========================================
               N = IR
               LIG = (N - 1) / NKOL + 1
               KOL = N - (LIG - 1) * NKOL
               SURFMAI = DX_LU(KOL) * DY_LU(LIG)
               SURF_DRA(IR) = SURFMAI
               DO K=1,NB_AMONT_MAX
                  NUMAMO = MAI_RUIS_AMO(K , IR)
                  IF ((NUMAMO <= 0).OR.(NUMAMO > NTOT)) CYCLE
!                 ================
!                  Surfaces Amont
!                 ================
                  SURF_DRA(IR) = SURF_DRA(IR) + SURF_DRA(NUMAMO)
               ENDDO
!              =====================
!               Condition de sortie
!              =====================
               NAV = MAI_RUIS_AVA(IR)
               IF (NAV <= 0) EXIT TRONCON
            ENDDO TRONCON
         ENDDO BAL_JOIN
      ENDDO BAL_ORDR
      END SUBROUTINE BAL_MAI_8_DIR_RUIS

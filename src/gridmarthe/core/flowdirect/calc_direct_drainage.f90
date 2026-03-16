! SPDX-License-Identifier: GPL-3.0-or-later
! Copyright 2024, BRGM
! 
! This file is part of gridmarthe.
! 
! Gridmarthe is free software: you can redistribute it and/or modify it under the
! terms of the GNU General Public License as published by the Free Software
! Foundation, either version 3 of the License, or (at your option) any later
! version.
! 
! Gridmarthe is distributed in the hope that it will be useful, but WITHOUT ANY
! WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
! PARTICULAR PURPOSE. See the GNU General Public License for more details.
! 
! You should have received a copy of the GNU General Public License along with
! Gridmarthe. If not, see <https://www.gnu.org/licenses/>.
!
!
! (from MARTHE, file : edsemi.f90, convert utf-8 )
!
! MARTHE, Copyright (c) 1990-2024 BRGM
!      
      SUBROUTINE Cal_Direct_Drainage(ITYP_DIRECT, EPS_TOP, FICH_PRESENCE, FICH_TOPO, FICH_SOR_DIRECT, FICH_SOR_TOPO, FICH_LISTING, &
         CHAMP_AUX, NKOL, NLIG, X0 , Y0, TITSEM, DX_LU,DY_LU)
!=========================================================================================
!   *********************
!   *Cal_Direct_Drainage*              BRGM     B.P. 36009
!   *********************              45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 30/01/2023
!=========================================================================================
!      Calcul des Directions de Drainage � partir de la Topographie
!      << Cette version est op�rationnelle uniquement pour les maillages Sans Gigognes >>
!=========================================================================================
!      Routines utilis�es :
!      * Ouvre_Mon_Projet
!      * Lec_Param_Cal_Dir_Drain
!      * Num_8_Voisins
!      * Corrige_Absent
!      * Detecte_Lacs
!      * Anal_Topo_0 [ Corrig_Multi_Avals(] (Appels de multiples fois)
!=========================================================================================
      IMPLICIT NONE
      
      INTEGER, PARAMETER :: NKOLMA=999, NLIGMA=999, NTOTMA=NKOLMA * NLIGMA
      REAL(KIND=8), DIMENSION(NKOLMA) :: XCOL, DX_LU
      REAL(KIND=8), DIMENSION(NLIGMA) :: YLIG, DY_LU 
      REAL(KIND=8), DIMENSION(NTOTMA) :: CHAMP_AUX
      REAL, DIMENSION(NTOTMA) :: PRESEN
      INTEGER, DIMENSION(:,:), ALLOCATABLE :: NUM_VOIS
      INTEGER, DIMENSION(:), ALLOCATABLE :: IDIRAVA, IDOMAIN, I_TROU, IDEN_LAC, NBRE_EGAL
      REAL   , DIMENSION(:), ALLOCATABLE :: TOPO, TOPO_INIT
      CHARACTER (LEN=132) :: TITSEM
      ! CHARACTER (LEN=401) :: FICH_401
      CHARACTER (LEN=20) :: CHARA20
      CHARACTER (LEN=13) :: CODTIT_13
      CHARACTER (LEN=80) :: NATUR_FICH
!     ======= Lecture
      CHARACTER (LEN=132), INTENT(IN) :: FICH_PRESENCE &
                                       , FICH_TOPO &
                                       , FICH_SOR_DIRECT &
                                       , FICH_LISTING &
                                       , FICH_SOR_TOPO
      CHARACTER (LEN=40) :: FICH_SOR_AUX
      CHARACTER (LEN=80) :: TITGEN
      CHARACTER (LEN=1)   :: CHAR_NEW = " "
      INTEGER, PARAMETER :: NITER_MAX = 100
      INTEGER, DIMENSION(0:4 , 0:NITER_MAX) :: NB_TYP_TROU
      INTEGER, DIMENSION(0:NITER_MAX) :: NBRE_VARIAT, NON_RESOLU, NEW_MINI
      REAL(KIND=8)                :: X0 , Y0
      REAL, INTENT(IN)    :: EPS_TOP
      INTEGER, INTENT(IN) :: ITYP_DIRECT
!     =======
      REAL    :: AUX, POURCENT, TOPO_ABSENT
      INTEGER :: LEC, IOU, INPCON, IOUCON, IOUCON_NUL, LISTIN, INVERS, INVY &
               , NTOT, NLIG, NKOL, NLIGP, NKOLP &
               , IEREDI, IEROLD, IERNEW, IERLEC, IERRAUX, IER, NUMERR, LIRE_DXDY, LU_DXDY, LU_XY &
               , IOUMAI &
               , ITYP, ITER, NITER, KONT_ITER, MINI_NON_DEF, MINI_OBTENU &
               , I_PASSAG, I_COR_TROU_AUX, I_COR_MULTI_AVAL_AUX, I_COR_PLAT_AUX &
               , KONT_VAR_SAUV, NB_ITER_CAL, I_CAL_DIRAVA &
               , I_CORRIG_TROU, I_CORRIG_MULTI_AVAL, I_CORRIG_PLAT, IEXE,KONT_VAR &
               , NEXE, NBRE_LACS !, ISTOP
      INTEGER :: IERR
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
      TOPO_ABSENT = 9999.

      TITGEN = "Calculation of Flow Directions based on Topography"

      OPEN(UNIT=LISTIN, FILE=FICH_LISTING, STATUS="replace", ACTION="write", IOSTAT=IERR)
      IF (IERR /= 0) THEN
         NATUR_FICH = "listing file "
         WRITE(*,*) "Problem when opening file: ", TRIM(NATUR_FICH), TRIM(FICH_LISTING)
         STOP " "
      ENDIF

      WRITE (LISTIN, "(A)", IOSTAT=IERRAUX) TRIM(TITGEN)
      WRITE (LISTIN, *)
      WRITE (LISTIN, 9002, IOSTAT=IERRAUX) TRIM(FICH_PRESENCE) &
                                         , TRIM(FICH_TOPO)
      WRITE (LISTIN, *)
      WRITE (LISTIN, 9003, IOSTAT=IERRAUX) TRIM(FICH_SOR_DIRECT) &
                                         , TRIM(FICH_SOR_TOPO) &
                                         , TRIM(FICH_LISTING)
      WRITE (LISTIN, *)
      WRITE (LISTIN, 9004, IOSTAT=IERRAUX) ITYP_DIRECT &
                                         , EPS_TOP
      WRITE (LISTIN, *)
!     ==========
!      Lectures
!     ==========
!     ==================
!      Fichier Présence
!     ==================
      NATUR_FICH = "Présence domaine de surface"
!        OPEOLD dans WinMarthe/src/Open_Fich_WinMart.f90
!        Ouverture (Open) "Old" du fichier IUL, de nom = FIC
!        IERLEC = 0 si normal
!        IERLEC = 1 si erreur
!         Version PC windows
      ! CALL OPEOLD(LEC, FICH_PRESENCE, IEROLD)
      OPEN (UNIT=LEC, FILE=FICH_PRESENCE, STATUS="old", ACTION="read", BLANK="zero", IOSTAT=IEROLD)
      IF (IEROLD /= 0) THEN
         WRITE (LISTIN, 9006, IOSTAT=IERRAUX)    TRIM(FICH_PRESENCE), TRIM(NATUR_FICH)
         WRITE(*,*) "Problem when reading file: ", TRIM(FICH_PRESENCE), TRIM(NATUR_FICH)
         STOP " "
      ENDIF
      NTOT = NTOTMA
      NLIG = NLIGMA
      NKOL = NKOLMA
      LIRE_DXDY = 1
      LU_DXDY = 1
      DX_LU(:) = -9999.
      DY_LU(:) = -9999.
      CHAMP_AUX(:) = -9999.
      ! LECSEM8_0 et LECSEM_3 dans WinMarthe/src/Lecsem.f90 
      ! gridmarthe/modgridmarth dans lecsem/READ_GRID qui utilise LECSEM_3
      ! here use gridmarthe/lecsem/Lecsem.f90 
      CALL LECSEM8_0(X0, Y0, PRESEN, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
         , IOUCON_NUL, LEC, IERLEC, NUMERR, NTOT &
         , LIRE_DXDY, LU_DXDY, LU_XY, DX_LU, DY_LU)
      CLOSE (LEC)
      ! WRITE(*,*) "X0 Y0", X0, Y0
      IF (IERLEC == 0) THEN
         WRITE (LISTIN, 9007, IOSTAT=IERRAUX) TRIM(NATUR_FICH), TRIM(TITSEM(1:68)), NKOL, NLIG
         IF (LU_DXDY <= 0) THEN
!           ===================================
!            Calcul des DX_LU,DU_LU si non lus
!           ===================================
            ! XY_DXDY dans Utimar/src/xy_dxdy.f90
            CALL XY_DXDY(X0, Y0, XCOL, YLIG, DX_LU, DY_LU, NLIG, NKOL &
             , IOUCON, INVY, IER)
         ENDIF
      ELSE
         WRITE (LISTIN, 9013, IOSTAT=IERRAUX)    TRIM(FICH_PRESENCE) &
                                               , TRIM(TITSEM(1:68)) &
                                               , TRIM(NATUR_FICH) &
                                               , NKOL, NLIG &
                                               , IERLEC, NUMERR
         STOP " "
      ENDIF
!     ================================================
!      Initialisations car on connait maintenant NTOT
!     ================================================
      ALLOCATE (NUM_VOIS(8,NTOT), STAT=IERRAUX)
      ALLOCATE (TOPO(NTOT), TOPO_INIT(NTOT) &
             , IDIRAVA(NTOT), IDOMAIN(NTOT), I_TROU(NTOT), IDEN_LAC(NTOT) &
             , NBRE_EGAL(NTOT), STAT=IERRAUX)
      IDOMAIN(1:NTOT) = 0
      WHERE ((PRESEN(1:NTOT) > 0).AND.(PRESEN(1:NTOT) /= 9999)) IDOMAIN(1:NTOT) = 1
      IDIRAVA(1:NTOT) = 0
!     ==========================
!      Topographie => TOPO_INIT
!     ==========================
      NATUR_FICH = "Topographie"

      OPEN (UNIT=LEC, FILE=FICH_TOPO, STATUS="old", ACTION="read", BLANK="zero", IOSTAT=IEROLD)
      IF (IEROLD /= 0) THEN
         WRITE (LISTIN, 9006, IOSTAT=IERRAUX)    TRIM(FICH_TOPO), TRIM(NATUR_FICH)
         STOP " "
      ENDIF
      NLIGP = NLIG
      NKOLP = NKOL
      LIRE_DXDY = 0
      CALL LECSEM8_0(X0, Y0, TOPO, XCOL, YLIG, NLIG, NKOL, INVERS, TITSEM &
         , IOUCON_NUL, LEC, IERLEC, NUMERR, NTOT &
         , LIRE_DXDY, LU_DXDY, LU_XY, DX_LU, DY_LU)
      CLOSE (LEC)
      IF (IERLEC == 3) THEN
         WRITE (LISTIN, 9014, IOSTAT=IERRAUX) TRIM(FICH_TOPO), TRIM(NATUR_FICH)
         STOP " "
      ENDIF
      IF (IERLEC == 0) THEN
         WRITE (LISTIN, 9007, IOSTAT=IERRAUX) TRIM(NATUR_FICH), TRIM(TITSEM(1:68)), NKOL, NLIG
      ELSE
         WRITE (LISTIN, 9013, IOSTAT=IERRAUX)    TRIM(FICH_TOPO) &
                                               , TRIM(TITSEM(1:68)) &
                                               , TRIM(NATUR_FICH) &
                                               , NKOL, NLIG &
                                               , IERLEC, NUMERR
         STOP " "
      ENDIF
      TOPO_INIT(:) = TOPO(:)
!     ===================================================
!      Calcul des 8 Numéros Voisins => NUM_VOIS(8 , NTOT)
!      Si Hors Limites => NUM_VOIS (IDIR,N) = 0
!     ===================================================
      CALL Num_8_Voisins(NLIG, NKOL, NTOT, IDOMAIN, NUM_VOIS)
      WRITE (LISTIN, *)
      WRITE (LISTIN, *) "First analysis Topo"
!     ====================================
!      Nouvel algorithme (Tout simultan�)
!     ====================================
!     =================
!      Calcul des Lacs
!     =================
      CALL Corrige_Absent(NTOT,IDOMAIN, NUM_VOIS, TOPO_ABSENT, TOPO)
      CALL Detecte_Lacs(NTOT, NBRE_LACS, TOPO_ABSENT, IDOMAIN, NUM_VOIS &
                            , IDEN_LAC, NBRE_EGAL, TOPO)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
         IF (NBRE_LACS > 0) THEN
            write (LISTIN, *) " Nombre de lacs = ",NBRE_LACS
            write (LISTIN, *) " NBRE_EGAL(1:NBRE_LACS) = "
            write (LISTIN,"(15I5)") NBRE_EGAL(1:NBRE_LACS)
         ENDIF
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      IF (ANY( IDEN_LAC(1:NTOT) /= 0 )) THEN
!        =====================================
!         �dition des Identificateurs de Lacs
!        =====================================
         FICH_SOR_AUX = "Zones_Lac.out"
         ! OPENEW dans WinMarthe/src/Open_Fich_WinMart.f90:342
         ! CALL OPENEW(IOUMAI, FICH_SOR_AUX, IERNEW, 1)
         OPEN (UNIT=IOUMAI, FILE=FICH_SOR_AUX, STATUS="replace", IOSTAT=IERNEW)
         IF (IERNEW /= 0) THEN
            NATUR_FICH = "Identification de Lacs"
            WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOR_DIRECT)
         ELSE
            CHAMP_AUX(1:NTOT) = REAL( IDEN_LAC(1:NTOT) )
            TITSEM = "Numéros des Identificateur de Lacs"
            CODTIT_13 = "IDENT_LAC"
            WRITE (CHARA20, "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13) , 1
            TITSEM(71:) = TRIM(CHARA20)
            ! EDSEMI7_0 dans WinMarthe/src/Edsemigl.f90 (ncouch = 0, max_couche = 0 etc.)
            CALL EDSEMI7_0(CHAMP_AUX(1:NTOT), NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
               , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
            CLOSE (IOUMAI)
            IF (IEREDI == 0) THEN
               WRITE (LISTIN, *)
               WRITE (LISTIN, *) " Identificateurs de Lacs  sauvegard�e : ", TRIM(FICH_SOR_AUX)
           ENDIF
         ENDIF
      ENDIF
      NITER = MIN(16, NITER_MAX)
      MINI_OBTENU = -1
      BAL_PASS: DO I_PASSAG=1,2
!        ========================================================================
!         Le deuxi�me passage est utilis� si on a obtenu un Optimum avant la fin
!        ========================================================================
         KONT_VAR = 0
         MINI_NON_DEF = NINT(5.E7)
         KONT_ITER = 0
!        =================
!         Passage Initial
!        =================
         I_CAL_DIRAVA = 0
         I_CORRIG_TROU = 0
         I_CORRIG_PLAT = 0
         I_CORRIG_MULTI_AVAL = 0
!        =========================================================================
!         Analyse initiale de la Topo
!         Appel avec : I_CAL_DIRAVA = 0 (=> Pas de calcul des directions aval)
!         En entr�e :
!          NUM_VOIS(K , N) = Num�ro de la maille Voisine de N dans la direction K
!                            Si Direction K impossible (Nord de Ligne n�1
!                            ou Ouest de Col=1 par ex => NUM_VOIS(K , N) = 0)
!        =========================================================================
         CALL Anal_Topo_0(NLIG,NKOL,NTOT,EPS_TOP,KONT_VAR &
                            ,I_CORRIG_TROU,I_CORRIG_MULTI_AVAL,I_CORRIG_PLAT &
                            ,I_CAL_DIRAVA &
                            ,IDOMAIN,NUM_VOIS,I_TROU,TOPO,IDIRAVA)
         ITER = 0
         DO ITYP=0,4
            NB_TYP_TROU(ITYP , ITER) = COUNT( ((IDOMAIN(1:NTOT) == 1).AND. &
                                               (I_TROU(1:NTOT) == ITYP)) )
         ENDDO
         NON_RESOLU(ITER) = SUM( NB_TYP_TROU(1:4 , ITER) )
         IF (NON_RESOLU(ITER) < MINI_NON_DEF) THEN
            MINI_NON_DEF = NON_RESOLU(ITER)
            NEW_MINI(ITER) = 1
         ELSE
            NEW_MINI(ITER) = 0
         ENDIF
         NBRE_VARIAT(ITER) = KONT_VAR
         IF (I_PASSAG <= 1) THEN
            POURCENT = 0.
            AUX = REAL( SUM( NB_TYP_TROU(0:4 , ITER) ) )
            IF (AUX > 0.) POURCENT = 100. * REAL( NON_RESOLU(ITER) ) / AUX
            WRITE (LISTIN, 9015)
            WRITE (LISTIN, 9017) NB_TYP_TROU(0:2 , ITER) &
                               , NB_TYP_TROU(4 , ITER) &
                               , NB_TYP_TROU(3 , ITER) &
                               , NON_RESOLU(ITER) &
                               , POURCENT
            WRITE (LISTIN, 9010)
            ITER = 0
            CHAR_NEW = " "
            WRITE (LISTIN, 9011) ITER, NB_TYP_TROU(0:2 , ITER) &
                                     , NB_TYP_TROU(4 , ITER) &
                                     , NB_TYP_TROU(3 , ITER) &
                                     , NON_RESOLU(ITER) &
                                     , CHAR_NEW &
                                     , NBRE_VARIAT(ITER)
         ENDIF
         NEXE = 100
         BAL_ALTERN_CORR_AAA: DO IEXE = 1,NEXE
            ! WRITE (*, *, IOSTAT=IERRAUX) "Analyse passage", IEXE, " / ", NEXE
            IF (I_PASSAG <= 1) THEN
               WRITE (LISTIN, 9012) IEXE
               WRITE (LISTIN, 9010)
            ENDIF
            DO ITER=1,NITER
               KONT_ITER = KONT_ITER + 1
               I_TROU(1:NTOT) = 0
               IF (ITER < NITER) THEN
                  I_CORRIG_TROU = 1
                  I_CORRIG_MULTI_AVAL = 1
                  I_CORRIG_PLAT = 1
               ELSE
                  I_CORRIG_TROU = 0
                  I_CORRIG_MULTI_AVAL = 0
                  I_CORRIG_PLAT = 0
               ENDIF
               CALL Anal_Topo_0(NLIG, NKOL, NTOT, EPS_TOP, KONT_VAR &
                              , I_CORRIG_TROU, I_CORRIG_MULTI_AVAL, I_CORRIG_PLAT &
                              , I_CAL_DIRAVA &
                              , IDOMAIN, NUM_VOIS, I_TROU, TOPO, IDIRAVA)
!              ========
!               Cumule
!              ========
               DO ITYP=0,4
                  NB_TYP_TROU(ITYP , ITER) = COUNT( ((IDOMAIN(1:NTOT) == 1).AND. &
                                                     (I_TROU(1:NTOT) == ITYP)) )
               ENDDO
               NON_RESOLU(ITER) = SUM( NB_TYP_TROU(1:4 , ITER) )

!!!!!!!!!!!!!!!!!!!!!!
               IF (ITER < NITER) THEN
                  KONT_VAR_SAUV = KONT_VAR
!                 ========================================
!                  On refait quand en cours de correction
!                  Soit on refait tout le temps
!                  Soit on refait quand am�lioration
!                 ========================================
                  I_COR_TROU_AUX = 0
                  I_COR_MULTI_AVAL_AUX = 0
                  I_COR_PLAT_AUX = 0
                  CALL Anal_Topo_0(NLIG, NKOL, NTOT, EPS_TOP, KONT_VAR &
                                 , I_COR_TROU_AUX, I_COR_MULTI_AVAL_AUX, I_COR_PLAT_AUX &
                                 , I_CAL_DIRAVA &
                                 , IDOMAIN, NUM_VOIS, I_TROU, TOPO, IDIRAVA)
!                 ========
!                  Cumule
!                 ========
                  DO ITYP=0,4
                     NB_TYP_TROU(ITYP , ITER) = COUNT( ((IDOMAIN(1:NTOT) == 1).AND. &
                                                        (I_TROU(1:NTOT) == ITYP)) )
                  ENDDO
                  NON_RESOLU(ITER) = SUM( NB_TYP_TROU(1:4 , ITER) )
                  KONT_VAR = KONT_VAR_SAUV
               ENDIF
!!!!!!!!!!!!!!!!!!!!!!

               IF (NON_RESOLU(ITER) < MINI_NON_DEF) THEN
!                 ==============
!                  Am�lioration
!                 ==============
                  MINI_NON_DEF = NON_RESOLU(ITER)
                  NEW_MINI(ITER) = 1
               ELSE
                  NEW_MINI(ITER) = 0
               ENDIF
               NBRE_VARIAT(ITER) = KONT_VAR
               NB_ITER_CAL = ITER
               IF (KONT_VAR == 0) EXIT
               IF (NON_RESOLU(ITER) == 0) EXIT
               IF (NON_RESOLU(ITER) <= MINI_OBTENU) EXIT
            ENDDO
            IF (I_PASSAG <= 1) THEN
!              ====================================================
!               �dition de ce passage IEXE (Ensemble de NITER_CAL)
!              ====================================================
               DO ITER =1,NB_ITER_CAL
                  CHAR_NEW = " "
                  IF (NEW_MINI(ITER) == 1) CHAR_NEW = "*"
                  WRITE (LISTIN, 9011) ITER, NB_TYP_TROU(0:2 , ITER) &
                                           , NB_TYP_TROU(4 , ITER) &
                                           , NB_TYP_TROU(3 , ITER) &
                                           , NON_RESOLU(ITER) &
                                           , CHAR_NEW &
                                           , NBRE_VARIAT(ITER)
               ENDDO
            ENDIF
            IF ((KONT_VAR == 0).AND.(NB_ITER_CAL < NITER)) EXIT
            IF (NON_RESOLU(NB_ITER_CAL) == 0) EXIT
            IF (NON_RESOLU(NB_ITER_CAL) <= MINI_OBTENU) EXIT
         ENDDO BAL_ALTERN_CORR_AAA
         IF ((I_PASSAG == 1).AND.(MINI_NON_DEF > 0).AND. &
             (NON_RESOLU(NB_ITER_CAL) > MINI_NON_DEF)) THEN
            WRITE (LISTIN, *)
            WRITE (LISTIN, *)" Nombre total de passages =", KONT_ITER
            WRITE (LISTIN, *)
!           ============================================================
!            M�morise le Mini obtenu pour s'y arr�ter au 2 �me passage,
!            et reprend l'�tat initial
!           ============================================================
            MINI_OBTENU = MINI_NON_DEF
            IF (.NOT. ALLOCATED(TOPO_INIT)) THEN
               STOP "TOPO_INIT not allocated before assignment"
            ENDIF
            TOPO = TOPO_INIT
!           ==================
!            Retour passage 2
!           ==================
            WRITE (LISTIN, 9018) MINI_NON_DEF
         ELSE
!           ======================================================
!            * Soit c'est le 2�me Passage
!            * Soit on a obtenu 0 non d�finis
!            * Soit on a obtenu l'Optimum � la fin du 1er Passage
!            => Fini
!           ======================================================
!!!!            IF (NB_ITER_CAL < NITER) THEN
!              ===================================================
!               Contr�le car n'�dite pas au cours du 2�me passage
!              ===================================================
               I_CORRIG_TROU = 0
               I_CORRIG_MULTI_AVAL = 0
               I_CORRIG_PLAT = 0
               I_TROU(1:NTOT) = 0
               CALL Anal_Topo_0(NLIG, NKOL, NTOT, EPS_TOP, KONT_VAR &
                              , I_CORRIG_TROU, I_CORRIG_MULTI_AVAL, I_CORRIG_PLAT &
                              , I_CAL_DIRAVA &
                              , IDOMAIN, NUM_VOIS, I_TROU, TOPO, IDIRAVA)
!              ========
!               Cumule
!              ========
               ITER = NB_ITER_CAL
               DO ITYP=0,4
                  NB_TYP_TROU(ITYP , ITER) = COUNT( ((IDOMAIN(1:NTOT) == 1).AND. &
                                                     (I_TROU(1:NTOT) == ITYP)) )
               ENDDO
               NON_RESOLU(ITER) = SUM( NB_TYP_TROU(1:4 , ITER) )
               CHAR_NEW = " "
               NBRE_VARIAT(ITER) = 0
               WRITE (LISTIN, 9010)
               WRITE (LISTIN, 9011) KONT_ITER, NB_TYP_TROU(0:2 , ITER) &
                                             , NB_TYP_TROU(4 , ITER) &
                                             , NB_TYP_TROU(3 , ITER) &
                                             , NON_RESOLU(ITER) &
                                             , CHAR_NEW &
                                             , NBRE_VARIAT(ITER)
!!!!            ENDIF
            WRITE (LISTIN, 9019)
            POURCENT = 0.
            AUX = REAL( SUM( NB_TYP_TROU(0:4 , NB_ITER_CAL) ) )
            IF (AUX > 0.) POURCENT = 100. * REAL( NON_RESOLU(NB_ITER_CAL) ) / AUX
            WRITE (LISTIN, 9016)
            WRITE (LISTIN, 9017) NB_TYP_TROU(0:2 , NB_ITER_CAL) &
                               , NB_TYP_TROU(4 , NB_ITER_CAL) &
                               , NB_TYP_TROU(3 , NB_ITER_CAL) &
                               , NON_RESOLU(NB_ITER_CAL) &
                               , POURCENT
            WRITE (LISTIN, *)
            WRITE (LISTIN, *)" Nombre total de passages =",KONT_ITER
            WRITE (LISTIN, *)
            EXIT
         ENDIF
      ENDDO BAL_PASS
      IF (FICH_SOR_DIRECT /= " ") THEN
!        ===================================================================
!         � la fin des corrections : Calcul des Directions Aval : 1001:1008
!        ===================================================================
         I_CORRIG_TROU = 0
         I_CORRIG_MULTI_AVAL = 0
         I_CORRIG_PLAT = 0
         I_CAL_DIRAVA = 1
!        =====================================================================
!         Analyse de la Topo : Passage Final
!         Appel avec : I_CAL_DIRAVA = 1 (Calcul des Directions Aval)
!         En entr�e :
!          NUM_VOIS(K , N) = Num de la Voisine de N dans la direction K
!                            Si Direc K impossible (Nord de Ligne n�1
!                            ou Ouest de Col=1 par ex => NUM_VOIS(K , N) = 0)
!        =====================================================================
         CALL Anal_Topo_0(NLIG, NKOL, NTOT, EPS_TOP, KONT_VAR &
                        , I_CORRIG_TROU, I_CORRIG_MULTI_AVAL, I_CORRIG_PLAT &
                        , I_CAL_DIRAVA &
                        , IDOMAIN, NUM_VOIS, I_TROU, TOPO,IDIRAVA)
         ! ArcGis D8 flow directions               
         IF (ITYP_DIRECT == 1) THEN
            WHERE (IDIRAVA(1:NTOT) == 1002) IDIRAVA(1:NTOT) = 1
            WHERE (IDIRAVA(1:NTOT) == 1003) IDIRAVA(1:NTOT) = 4
            WHERE (IDIRAVA(1:NTOT) == 1004) IDIRAVA(1:NTOT) = 16
            WHERE (IDIRAVA(1:NTOT) == 1001) IDIRAVA(1:NTOT) = 64
            WHERE (IDIRAVA(1:NTOT) == 1006) IDIRAVA(1:NTOT) = 2
            WHERE (IDIRAVA(1:NTOT) == 1007) IDIRAVA(1:NTOT) = 8
            WHERE (IDIRAVA(1:NTOT) == 1008) IDIRAVA(1:NTOT) = 32
            WHERE (IDIRAVA(1:NTOT) == 1005) IDIRAVA(1:NTOT) = 128
            WHERE (IDIRAVA(1:NTOT) == 9999) IDIRAVA(1:NTOT) = 0
         ENDIF
         ! Qgis D8 flow directions
         IF (ITYP_DIRECT == 2) THEN
            WHERE (IDIRAVA(1:NTOT) == 1002) IDIRAVA(1:NTOT) = 1
            WHERE (IDIRAVA(1:NTOT) == 1003) IDIRAVA(1:NTOT) = 7
            WHERE (IDIRAVA(1:NTOT) == 1004) IDIRAVA(1:NTOT) = 5
            WHERE (IDIRAVA(1:NTOT) == 1001) IDIRAVA(1:NTOT) = 3
            WHERE (IDIRAVA(1:NTOT) == 1006) IDIRAVA(1:NTOT) = 8
            WHERE (IDIRAVA(1:NTOT) == 1007) IDIRAVA(1:NTOT) = 6
            WHERE (IDIRAVA(1:NTOT) == 1008) IDIRAVA(1:NTOT) = 4
            WHERE (IDIRAVA(1:NTOT) == 1005) IDIRAVA(1:NTOT) = 2
            WHERE (IDIRAVA(1:NTOT) == 9999) IDIRAVA(1:NTOT) = 0
         ENDIF         
      ENDIF
      IF (FICH_SOR_TOPO /= " ") THEN
!        =============================
!         �dition de la Topo corrig�e
!        =============================
         OPEN (UNIT=IOUMAI, FILE=FICH_SOR_TOPO, STATUS="replace", IOSTAT=IERNEW)
         IF (IERNEW /= 0) THEN
!           ========
!            Erreur
!           ========
            NATUR_FICH = "Topographie corrigée"
            WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOR_TOPO)
         ELSE
            TITSEM = "Topographie corrigée"
            CODTIT_13 = "H_TOPOGR"
            WRITE (CHARA20, "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13) , 1
            TITSEM(71:) = TRIM(CHARA20)
            CALL EDSEMI7_0(TOPO, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
               , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
            CLOSE (IOUMAI)
            IF (IEREDI == 0) THEN
               WRITE (LISTIN, *)
               WRITE (LISTIN, *) " Topographie corrigée sauvegardée : ", TRIM(FICH_SOR_TOPO)
            ENDIF
         ENDIF
      ENDIF
      IF (FICH_SOR_DIRECT /= " ") THEN
!        ====================================
!         �dition des Directions de Drainage
!        ====================================
         ! CALL OPENEW(IOUMAI, FICH_SOR_DIRECT, IERNEW, 1)
         OPEN (UNIT=IOUMAI, FILE=FICH_SOR_DIRECT, STATUS="replace", IOSTAT=IERNEW)
         IF (IERNEW /= 0) THEN
!           ========
!            Erreur
!           ========
            NATUR_FICH = "Directions Aval"
            WRITE (LISTIN   , 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
                                                  , TRIM(FICH_SOR_DIRECT)
            ! WRITE (WINT_200_BUFF, 9001, IOSTAT=IERRAUX) TRIM(NATUR_FICH) &
            !                                       , TRIM(FICH_SOR_DIRECT)
            ! CALL Dial_Message_Wait(WINT_200_BUFF, 0, 900)
         ELSE
            CHAMP_AUX(1:NTOT) = REAL( IDIRAVA(1:NTOT) )
            CODTIT_13 = "DIRECT_AVAL"
            WRITE (CHARA20 , "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13) , 1

            SELECT CASE (ITYP_DIRECT)
            CASE (0)
               TITSEM = "Directions Aval (1001:1008)"
            CASE (1)
               TITSEM = "Directions Aval (1:128) ArcGis"
            CASE (2)
               TITSEM = "Directions Aval (1:8) Qgis"                             
            END SELECT

            TITSEM(71:) = TRIM(CHARA20) 

            CALL EDSEMI7_0(CHAMP_AUX(1:NTOT), NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
               , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
            CLOSE (IOUMAI)
            ! WRITE(*,*) "X0 Y0", X0, Y0
            IF (IEREDI == 0) THEN
               WRITE (LISTIN, *)
               WRITE (LISTIN, *) " Directions Aval  sauvegardée : ", TRIM(FICH_SOR_DIRECT)
               CLOSE (LISTIN)
           ENDIF
         ENDIF
      ENDIF
! !     ===========================
! !      �dition des �tats (Trous)
! !     ===========================
!       CHAMP_AUX(1:NTOT) = REAL( I_TROU(1:NTOT) )
!       ! CALL OPENEW(IOUMAI, "Code_Singul.out", IERNEW, 1)
!       OPEN (UNIT=IOUMAI, FILE="Code_Singul.out", STATUS="replace", IOSTAT=IERNEW)
!       TITSEM = "Singularités"
!       CODTIT_13 = "SINGULARI"
!       WRITE (CHARA20 , "(1X,A,1X,I2)", IOSTAT=IERRAUX) TRIM(CODTIT_13), 1
!       TITSEM(71:) = TRIM(CHARA20)
!       CALL EDSEMI7_0(CHAMP_AUX, NKOL, NLIG, XCOL, YLIG, X0, Y0, INVY &
!          , TITSEM, IEREDI, IOUMAI, DX_LU, DY_LU)
!     ======
!      Fini
!     ======
 9001 FORMAT (" Impossible d'ouvrir un fichier ",A," :" &
             /" de nom : ",A)
 9002 FORMAT (" Fichiers d'entr�e :" &
             /" Pr�sence domaine surface       =",1X,A &
             /" Topographie                    =",1X,A)
 9003 FORMAT (" Fichiers de sortie :" &
             /" Direct. de drainage Calc.      =",1X,A &
             /" Topographie Corrig�e           =",1X,A &
             /" Listing                        =",1X,A)
 9004 FORMAT (" Param�tres :" &
             /" Type de directions (0=MARTHE)  =",1X,I10 &
             /" Correction d'altitude unitaire =",1X,F12.3)
 9006 FORMAT (//" *** Le fichier de nom '",A,"'",T77,"***" &
               /" *** n'a pas �t� trouv�",T77,"***" &
               /" *** pour les donn�es de '",A,"'",T77,"***"/)
 9007 FORMAT (/" Lecture du fichier ",A," effectu�e" &
              /" Titre descriptif = ",A &
              /" Nombre de colonnes = ",I0 &
              /" Nombre de lignes   = ",I0)
 9010 FORMAT (/" It�rat   1 Aval     Puits   + Avals    1 Plat   + Plats" &
              ,"  Non-R�solu  Nb_Variat")
 9011 FORMAT (I6,6I10," ",A," (",I8,")")
 9012 FORMAT (/" Passage n� ",I0)
 9013 FORMAT (/" Erreur dans la lecture du fichier ",A," :" &
              /" Titre descriptif = ",A &
              /" pour les donn�es de ",A &
              /" Nombre de colonnes = ",I0," ; Nombre de lignes  = ",I0 &
              /" (IERLEC = ",I0," Maille NUMERR= ",I0,")")
 9014 FORMAT (/" Erreur dans la lecture du fichier ",A," :" &
              /" pour les donn�es de ",A &
              /" Dimensions (colonnes , lignes) incorrectes")
 9015 FORMAT (/" Au d�part :")
 9016 FORMAT (/" Apr�s corrections :")
 9017 FORMAT ( " Fin de calcul : R�capitulation des Nombres de Mailles :" &
             //I8," Mailles : Bien d�finies" &
              /I8," Puits (d�pressions sans sortie)" &
              /I8," Mailles avec : Plusieurs sorties" &
              /I8," Mailles avec : 1 aval plat unique" &
              /I8," Mailles avec : Plusieurs avals plats" &
              /8X," =======================================" &
              /I8," = Nombre Total de mailles Non-R�solues (soit : ",F0.3," %)")
 9018 FORMAT (/80("/") &
             //" Deuxi�me passage pour s'arr�ter � l'optimum : ",I0," Non-r�solus")
 9019 FORMAT (/" Note : une '*' indique une am�lioration, c-�-d une diminution du nombre des non-r�solus")
      END SUBROUTINE Cal_Direct_Drainage
      SUBROUTINE Corrige_Absent(NTOT, IDOMAIN, NUM_VOIS, TOPO_ABSENT, TOPO)
!=======================================================================
!   ****************
!   *Corrige_Absent*                   BRGM     B.P. 36009
!   ****************                   45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 30/01/2023
!==============================================================================
!      En Entr�e :
!      NTOT        = Nombre de Mailles
!      TOPO_ABSENT = Valeur code de Topographie inconnue dans le domaine
!      IDOMAIN(NTOT) = 0 � l'ext�rieur du domaine
!      TOPO(NTOT) = Altitude Topo dans le domaine
!      NUM_VOIS(K , N) = Num de la Voisine de N dans la direction K
!                        Si Direc K impossible (Nord de Ligne n�1
!                        ou Ouest de Col=1 par ex => NUM_VOIS(K , N) = 0)
!      En Sortie :
!      TOPO(NTOT) = Altitude Topo corrig�e quand +-TOPO_absent dans le domaine
!==============================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NTOT
      INTEGER, DIMENSION(NTOT), INTENT(IN)  :: IDOMAIN
      INTEGER, DIMENSION(8 , NTOT), INTENT(IN)  :: NUM_VOIS
      REAL   , DIMENSION(NTOT), INTENT(IN OUT) :: TOPO
      REAL   , INTENT(IN) :: TOPO_ABSENT
!     ========
!      Locaux
!     ========
      REAL    :: SQRT_2
      REAL    :: TOP_CEN, SOM_POND, SOM_TOP
      INTEGER :: N, K, NUM_VOIS_K
!     =======
!      D�but
!     =======
      SQRT_2 = SQRT(2.)
      DO N = 1,NTOT
         IF (IDOMAIN(N) <= 0) CYCLE
         TOP_CEN = TOPO(N)
         IF (ABS(TOP_CEN) == TOPO_ABSENT) THEN
!           ================================================================
!            Corrige les Topo non d�finies (+-TOPO_Absent) (souvent +-9999)
!           ================================================================
            SOM_POND = 0.
            SOM_TOP  = 0.
            DO K=1,8
               NUM_VOIS_K = NUM_VOIS(K , N)
               IF (NUM_VOIS_K == 0) CYCLE
               IF (ABS(TOPO(NUM_VOIS_K)) == TOPO_ABSENT) CYCLE
               SELECT CASE (K)
               CASE (1:4)
                  SOM_POND = SOM_POND + 1
               CASE (5:8)
                  SOM_POND = SOM_POND + 1. / SQRT_2
               END SELECT
               SOM_TOP = SOM_TOP + TOPO(NUM_VOIS_K)
            ENDDO
            IF (SOM_POND > 0.) THEN
!              =========
!               Corrige
!              =========
               TOPO(N) = SOM_TOP / SOM_POND
               TOP_CEN = TOPO(N)
            ENDIF
         ENDIF
      ENDDO
      END SUBROUTINE Corrige_Absent
      SUBROUTINE Detecte_Lacs(NTOT, NBRE_LACS, TOPO_ABSENT, IDOMAIN, NUM_VOIS &
                            , IDEN_LAC, NBRE_EGAL, TOPO)
!=========================================================================
!   **************
!   *Detecte_Lacs*                     BRGM     B.P. 36009
!   **************                     45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 30/01/2023
!=========================================================================
!      D�tection des Lacs
!=========================================================================
!      En Entr�e :
!      NTOT        = Nombre de Mailles
!      TOPO_ABSENT = Valeur code de Topo inconnue dans le domaine
!      IDOMAIN(NTOT)   = 0 � l'ext�rieur du domaine
!      NUM_VOIS(K , N) = Num de la Voisine de N dans la direction K
!                        Si Direc K impossible (Nord de Ligne n�1
!                        ou Ouest de Col=1 par ex => NUM_VOIS(K , N) = 0)
!      En Sortie :
!      IDEN_LAC(NTOT) = Num�ro du Lac (0 quand pas de Lac)
!      NBRE_LACS      = Nombre de Lacs
!      NBRE_EGAL(NBRE_LACS) = Nombre de Mailles de chaque Lac
!=========================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: NTOT
      REAL   , INTENT(IN)  :: TOPO_ABSENT
      INTEGER, INTENT(OUT) :: NBRE_LACS
      INTEGER, DIMENSION(NTOT), INTENT(IN)  :: IDOMAIN
      INTEGER, DIMENSION(NTOT), INTENT(OUT) :: IDEN_LAC, NBRE_EGAL
      INTEGER, DIMENSION(8 , NTOT), INTENT(IN)  :: NUM_VOIS
      REAL   , DIMENSION(NTOT), INTENT(IN) :: TOPO
!     ========
!      Locaux
!     ========
      INTEGER, DIMENSION(NTOT) :: MEME_QUE
      REAL    :: TOP_CEN
      INTEGER :: N, K, K2, NUM_VOIS_K, KONT, NUMLAC, NUMLAC_CEN, IEXE, NEXE, IMODI &
               , LACMIN, LACMAX, LAC_AUTRE
      INTEGER, DIMENSION(8) :: NUM_VOIS_LOC
      INTEGER, DIMENSION(8) :: NUM_VOIS_EGA
!     =======
!      D�but
!     =======
      NBRE_LACS = 0
      IDEN_LAC = 0
      NBRE_EGAL = 0
      DO N = 1,NTOT
         IF (IDOMAIN(N) <= 0) CYCLE
         TOP_CEN = TOPO(N)
         IF (TOP_CEN == TOPO_ABSENT) CYCLE
!        ======================================
!         On charge les voisins de la maille N
!        ======================================
         NUM_VOIS_LOC(1:8) = NUM_VOIS(1:8 , N)
         NUM_VOIS_EGA(1:8) = 0
         KONT = 0
         NUMLAC = IDEN_LAC(N)
         DO K=1,8
!           =============================
!            Balayage des 8 voisins de N
!           =============================
            NUM_VOIS_K = NUM_VOIS_LOC(K)
            IF (NUM_VOIS_K == 0) CYCLE
!           =====================
!            Voisin hors domaine
!           =====================
            IF (IDOMAIN(NUM_VOIS_K) == 0) CYCLE
            IF (TOPO(NUM_VOIS_K) == TOP_CEN) THEN
               KONT = KONT + 1
               NUMLAC = MAX(IDEN_LAC(NUM_VOIS_K), NUMLAC)
               NUM_VOIS_EGA(K) = 1
            ENDIF
         ENDDO
         IF (KONT == 0) CYCLE
!        ============================================================
!         On a trouv� KONT mailles voisines avec une cote topo �gale
!        ============================================================
         IF (NUMLAC == 0) THEN
!           =============
!            Nouveau Lac
!           =============
            NBRE_LACS = NBRE_LACS + 1
            NUMLAC = NBRE_LACS
            NBRE_EGAL(NUMLAC) = 1
         ENDIF
         IDEN_LAC(N) = NUMLAC
         NBRE_EGAL(NUMLAC) = NBRE_EGAL(NUMLAC) + KONT
         DO K=1,8
!           =============================
!            Balayage des 8 voisins de N
!           =============================
            IF (NUM_VOIS_EGA(K) == 0) CYCLE
!           =======================================================
!            Une des mailles � cote topo �gale => Mise de IDEN_LAC
!           =======================================================
            IDEN_LAC(NUM_VOIS_LOC(K)) = NUMLAC
         ENDDO
      ENDDO
      IF (NBRE_LACS > 0) THEN
!        ===============
!         Regroupements
!        ===============
         NEXE = 15
         DO IEXE=1,NEXE
            MEME_QUE(1:NBRE_LACS) = 0
            IMODI = 0
            DO N = 1,NTOT
               IF (IDOMAIN(N) <= 0) CYCLE
               TOP_CEN = TOPO(N)
               IF (TOP_CEN == TOPO_ABSENT) CYCLE
!              ======================================
!               On charge les voisins de la maille N
!              ======================================
               NUM_VOIS_LOC(1:8) = NUM_VOIS(1:8 , N)
               NUM_VOIS_EGA(1:8) = 0
               NUMLAC_CEN = IDEN_LAC(N)
               DO K=1,8
!                 =============================
!                  Balayage des 8 voisins de N
!                 =============================
                  NUM_VOIS_K = NUM_VOIS_LOC(K)
                  IF (NUM_VOIS_K == 0) CYCLE
!                 =====================
!                  Voisin hors domaine
!                 =====================
                  IF (IDOMAIN(NUM_VOIS_K) == 0) CYCLE
                  IF (TOPO(NUM_VOIS_K) == TOP_CEN) THEN
                     NUMLAC = IDEN_LAC(NUM_VOIS_K)
                     IF (NUMLAC == NUMLAC_CEN) CYCLE
!                    ==========================================================
!                     2 Num�ros de Lacs diff�rents => Plus grand => Plus petit
!                     Mais ne pas �craser
!                    ==========================================================
                     IMODI = 1
                     IF ((MEME_QUE(NUMLAC) == 0).AND.(MEME_QUE(NUMLAC_CEN) == 0)) THEN
                        LACMIN = MIN(NUMLAC, NUMLAC_CEN)
                        LACMAX = MAX(NUMLAC, NUMLAC_CEN)
                        MEME_QUE(LACMAX) = LACMIN
                     ELSE IF (MEME_QUE(NUMLAC) == 0) THEN
                        LAC_AUTRE = MEME_QUE(NUMLAC_CEN)
!                       =================================================================
!                        => MEME_QUE(NUMLAC_CEN) > 0 c-�-d NUMLAC_CEN est m�me LAC_AUTRE
!                           car les 2 MEME_QUE() ne sont pas nuls.
!                        => NUMLAC va �tre "m�me que" LAC_AUTRE
!                       =================================================================
                        MEME_QUE(NUMLAC) = LAC_AUTRE
                        DO K2=1,NBRE_LACS
!                          ===========
!                           Transitif
!                          ===========
                           LAC_AUTRE = MEME_QUE(LAC_AUTRE)
                           IF (LAC_AUTRE == 0) THEN
                              EXIT
                           ELSE
                              MEME_QUE(NUMLAC) = LAC_AUTRE
                           ENDIF
                        ENDDO
                     ELSE IF (MEME_QUE(NUMLAC_CEN) == 0) THEN
                        LAC_AUTRE = MEME_QUE(NUMLAC)
!                       =============================================================
!                        => MEME_QUE(NUMLAC) > 0 c-�-d NUMLAC est m�me que LAC_AUTRE
!                           car les 2 MEME_QUE() ne sont pas nuls
!                        => NUMLAC_CEN va �tre "m�me que" LAC_AUTRE
!                       =============================================================
                        MEME_QUE(NUMLAC_CEN) = LAC_AUTRE
                        DO K2=1,NBRE_LACS
!                          ===========
!                           Transitif
!                          ===========
                           LAC_AUTRE = MEME_QUE(LAC_AUTRE)
                           IF (LAC_AUTRE == 0) THEN
                              EXIT
                           ELSE
                              MEME_QUE(NUMLAC_CEN) = LAC_AUTRE
                           ENDIF
                        ENDDO
                     ELSE
!                       =====================================================
!                        => MEME_QUE(NUMLAC) > 0  + MEME_QUE(NUMLAC_CEN) > 0
!                           On laisse ... (v�rifier)
!                       =====================================================
                     ENDIF
                  ENDIF
               ENDDO
            ENDDO
            IF (IMODI == 0) EXIT
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    write (7,*) " IEXE=",IEXE
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!           ==========
!            Regroupe
!           ==========
!           =================
!            V�rif Transitif
!           =================
            DO K = 1,NBRE_LACS
               NUMLAC = MEME_QUE(K)
               IF (NUMLAC == 0) CYCLE
!              =========================================================
!               Le Lac n�K => devient NUMLAC
!               => On v�rifie si NUMLAC devient autre chose : LAC_AUTRE
!              =========================================================
               LAC_AUTRE = NUMLAC
               DO K2=1,NBRE_LACS
!                 ===========
!                  Transitif
!                 ===========
                  LAC_AUTRE = MEME_QUE(LAC_AUTRE)
                  IF (LAC_AUTRE == 0) THEN
                     EXIT
                  ELSE
                     MEME_QUE(K) = LAC_AUTRE
                  ENDIF
               ENDDO
            ENDDO
            DO N = 1,NTOT
               NUMLAC = IDEN_LAC(N)
               IF (NUMLAC == 0) CYCLE
!              ===========================
!               Maille N => Lac n� NUMLAC
!              ===========================
               K = MEME_QUE(NUMLAC)
               IF (K == 0) CYCLE
!              ==================================
!               Lac n� NUMLAC => devient Lac n�K
!              ==================================
               IDEN_LAC(N) = K
            ENDDO
         ENDDO
!        =============
!         On recompte
!        =============
         NBRE_EGAL = 0
         DO N = 1,NTOT
            NUMLAC = IDEN_LAC(N)
            IF (NUMLAC == 0) CYCLE
!           =============================
!            Maille n�N => Lac n� NUMLAC
!           =============================
            NBRE_EGAL(NUMLAC) = NBRE_EGAL(NUMLAC) + 1
         ENDDO
!        ===================
!         Seuil NB_MINI
!         10 pour l'instant
!        ===================
         NBRE_LACS = 0
         DO K = 1,NTOT
            IF (NBRE_EGAL(K) < 10) THEN
!              ===============
!               Annulle Lac K
!              ===============
               MEME_QUE(K) = 0
               NBRE_EGAL(K) = 0
            ELSE
               NBRE_LACS = NBRE_LACS + 1
!              =====================
!              Provisoirement n� -K
!              =====================
               MEME_QUE(K) = -NBRE_LACS
               NBRE_EGAL(NBRE_LACS) = NBRE_EGAL(K)
            ENDIF
         ENDDO
         DO N = 1,NTOT
            NUMLAC = IDEN_LAC(N)
            IF (NUMLAC == 0) CYCLE
!           ===========================
!            Maille N => Lac n� NUMLAC
!           ===========================
            K = MEME_QUE(NUMLAC)
!           ==================================
!            Lac n� NUMLAC => devient Lac n�K
!            Att : M�me si K = 0
!           ==================================
            IDEN_LAC(N) = K
         ENDDO
         IDEN_LAC(1:NTOT) = -IDEN_LAC(1:NTOT)
      ENDIF
      END SUBROUTINE Detecte_Lacs 

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
      SUBROUTINE Anal_Topo_0(NLIG, NKOL, NTOT, EPS_TOP, KONT_VAR &
                           , I_CORRIG_TROU, I_CORRIG_MULTI_AVAL, I_CORRIG_PLAT &
                           , I_CAL_DIRAVA &
                           , IDOMAIN, NUM_VOIS, I_TROU, TOPO, IDIRAVA)
!=========================================================================
!   *************
!   *Anal_Topo_0*                      BRGM     B.P. 36009
!   *************                      45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=========================================================================
!      Analyse initiale de la Topo
!=========================================================================
!      I_CAL_DIRAVA = 1 => Passage Final
!                       => On calcule les Directions Aval
!      NUM_VOIS(K , N) = Num de la Voisine de N dans la direction K
!                        Si Direc K impossible (Nord de Ligne n�1
!                        ou Ouest de Col=1 par ex => NUM_VOIS(K , N) = 0)
!=========================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NLIG, NKOL, NTOT &
                           , I_CORRIG_TROU, I_CORRIG_MULTI_AVAL, I_CORRIG_PLAT &
                           , I_CAL_DIRAVA
      INTEGER, INTENT(IN OUT) :: KONT_VAR
      REAL   , INTENT(IN) :: EPS_TOP
      INTEGER, DIMENSION(NTOT), INTENT(IN)  :: IDOMAIN
      INTEGER, DIMENSION(NTOT), INTENT(IN OUT)  :: I_TROU, IDIRAVA
      INTEGER, DIMENSION(8 , NTOT), INTENT(IN)  :: NUM_VOIS
      REAL   , DIMENSION(NTOT), INTENT(IN OUT) :: TOPO
!     ========
!      Locaux
!     ========
      INTEGER :: LIG, INDLIG, KOL, N, K, NUM_MIN, K_MIN &
               , NUM_VOIS_K, NUM_VOIS_MIN, NUM_AVANT_MIN &
               , K_MIN_DU_CEN, K_AVANT_MIN, I_SORTIE, K_G_MIN
      REAL   , DIMENSION(8) :: GRADIENT, GRAD_LOC
      REAL    :: TOP_CEN, TOP_MIN, TOP_AVANT_MIN
      REAL    :: SOM_POND, SOM_TOP, GRAD_MIN, SQRT_2, FACT_EPS
!     =======
!      D�but
!     =======
      SQRT_2 = SQRT(2.)
      FACT_EPS = 2.
      FACT_EPS = 2.07
      KONT_VAR = 0
      IF (I_CAL_DIRAVA == 1) THEN
         IDIRAVA(1:NTOT) = 0
      ENDIF
      DO LIG=1,NLIG
         INDLIG = (LIG - 1) * NKOL
         DO KOL = 1,NKOL
            N = (LIG - 1) * NKOL + KOL
            IF (IDOMAIN(N) <= 0) CYCLE
            TOP_CEN = TOPO(N)
            IF (ABS(TOP_CEN) == 9999.) THEN
!              ========================================
!               Corrige les topo non d�finies (+-9999)
!              ========================================
               SOM_POND = 0.
               SOM_TOP  = 0.
               DO K=1,8
                  NUM_VOIS_K = NUM_VOIS(K , N)
                  IF (NUM_VOIS_K == 0) CYCLE
                  IF (ABS(TOPO(NUM_VOIS_K)) == 9999.) CYCLE
                  SELECT CASE (K)
                  CASE (1:4)
                     SOM_POND = SOM_POND + 1
                  CASE (5:8)
                     SOM_POND = SOM_POND + 1. / SQRT_2
                  END SELECT
                  SOM_TOP = SOM_TOP + TOPO(NUM_VOIS_K)
               ENDDO
               IF (SOM_POND > 0.) THEN
                  TOPO(N) = SOM_TOP / SOM_POND
                  TOP_CEN = TOPO(N)
               ENDIF
            ENDIF
!           ========================
!            Calcul des 8 gradients
!           ========================
            NUM_MIN = 0
            K_MIN   = 0
            DO K=1,8
               GRADIENT(K) = 9999.
               IF (ABS(TOP_CEN) == 9999.) CYCLE
               NUM_VOIS_K = NUM_VOIS(K , N)
               IF (NUM_VOIS_K == 0) CYCLE
               IF (ABS(TOPO(NUM_VOIS_K)) == 9999.) CYCLE
               IF (IDOMAIN(NUM_VOIS_K) == 0) THEN
!                 =================================================
!                  Voisin Hors Domaine
!                  On l'accepte mais : Si bloque => On sortira ...
!                  ... Mais si Topo inconnue ... Pas pris en compte
!                 =================================================
               ENDIF
               GRADIENT(K) = TOPO(NUM_VOIS_K) - TOP_CEN
               IF (K >= 5) GRADIENT(K) = GRADIENT(K) / SQRT_2
            ENDDO
!           ========================================================
!            Donc Gradient = +9999. Dans les directions impossibles
!           ========================================================
            GRAD_MIN   = MINVAL(GRADIENT)
            K_G_MIN    = MINLOC(GRADIENT, DIM=1)
            K_MIN_DU_CEN = K_G_MIN
            NUM_VOIS_MIN = NUM_VOIS(K_MIN_DU_CEN , N)
            IF (NUM_VOIS_MIN == 0) CYCLE
            TOP_MIN = TOPO(NUM_VOIS_MIN)
            IF (GRAD_MIN > 0.) THEN
!              ====================================================
!               Trou total (Puits)
!               Mais s'il reste 1 direction avec ext�rieur => Sort
!              ====================================================
               I_SORTIE = 0
               IF (ABS(TOP_CEN) /= 9999.) THEN
!                 =============================================================
!                  Examen s'il y a 1 direction hors domaine avec Topo Inconnue
!                  ou bien vers ext�rieur du cadre
!                 =============================================================
                  DO K=1,8
                     NUM_VOIS_K = NUM_VOIS(K , N)
                     IF (NUM_VOIS_K == 0) I_SORTIE = 1
                     IF ((I_SORTIE == 0).AND.(NUM_VOIS_K /= 0)) THEN
                        IF ((IDOMAIN(NUM_VOIS_K) == 0).AND. &
                            (ABS(TOPO(NUM_VOIS_K)) == 9999.)) THEN
!                          ==================================================
!                           Voisin hors domaine avec topo inconnue
!                           => Sort avec cette direction K
!                           N.B. Si TOPO(NUM_VOIS_K) est connu il est > Mini
!                                Mais on pourrait sortir quand m�me ...
!                                car risque que ... TOPO = 0 si non def
!                          ==================================================
                           I_SORTIE = 1
                        ENDIF
                     ENDIF
                     IF (I_SORTIE == 1) THEN
                        I_TROU(N) = 0
                        IF (I_CAL_DIRAVA == 1) THEN
                           IDIRAVA(N) = 1000 + K
                        ENDIF
                        EXIT
                     ENDIF
                  ENDDO
               ENDIF
               IF (I_SORTIE == 0) THEN
                  I_TROU(N) = 1
                  IF (I_CORRIG_TROU == 1) THEN
                     IF (TOP_MIN /= 9999.) THEN
                        TOP_CEN = TOP_MIN + FACT_EPS * EPS_TOP
                        TOPO(N) = TOP_CEN
                        KONT_VAR = KONT_VAR + 1
                     ENDIF
                  ENDIF
               ENDIF
            ELSE IF (GRAD_MIN < 0.) THEN
!              ===========================================================
!               Au moins 1 sortie => Voir si plusieurs Sorties Identiques
!                1 seule sortie => ITROU = 0
!               2: Sorties      => ITROU = 2
!               Si au moins 1 sortie vers ext�rieur => OK 1 seule sortie
!              ===========================================================
               I_TROU(N) = 0
               IF (I_CAL_DIRAVA == 1) THEN
                  IDIRAVA(N) = 1000 + K_MIN_DU_CEN
               ENDIF
               IF (IDOMAIN(NUM_VOIS_MIN) == 0) THEN
!                 ==========================================
!                  Voisin hors domaine => Sort (I_TROU = 0)
!                 ==========================================
               ELSE
!                 ==================================
!                  Examen si autres mini identiques
!                 ==================================
                  DO K=1,8
                     IF (K == K_MIN_DU_CEN) CYCLE
                     IF (GRADIENT(K) == GRAD_MIN) THEN
!                       =============================
!                        C'est un autre �gal au mini
!                       =============================
                        NUM_VOIS_K = NUM_VOIS(K , N)
                        IF (IDOMAIN(NUM_VOIS_K) == 0) THEN
!                          ==========================================
!                           Voisin hors domaine => Sort (I_TROU = 0)
!                           => Direction K
!                          ==========================================
                           I_TROU(N) = 0
                           IF (I_CAL_DIRAVA == 1) THEN
                              IDIRAVA(N) = 1000 + K
                           ENDIF
                           EXIT
                        ENDIF
                        I_TROU(N) = 2
                        IF (I_CAL_DIRAVA == 1) THEN
                           IDIRAVA(N) = 0
                        ENDIF
!                       ==============================================================
!                        On ne sort pas pour voir si rencontre 1 mini => Hors domaine
!                       ==============================================================
                     ENDIF
                  ENDDO
               ENDIF
            ELSE
!              ===================================================
!               GRAD_MIN = 0.
!               Le fond est Plat => Voir si plusieurs Plats �gaux
!                 1 Seul Plat => ITROU = 4
!                2: Plats     => ITROU = 3
!              ===================================================
               I_TROU(N) = 4
               DO K=1,8
                  IF (K == K_MIN_DU_CEN) CYCLE
                  IF (GRADIENT(K) == GRAD_MIN) THEN
!                    ===============================
!                     C'est un autre �gal au Centre
!                    ===============================
                     I_TROU(N) = 3
                     EXIT
                  ENDIF
               ENDDO
            ENDIF
            IF ((I_TROU(N) == 0).OR.(I_TROU(N) == 2)) THEN
!              ========================================================
!               1 Aval [I_TROU = 0] ou ou Plusieurs Avals [I_TROU = 2]
!              ========================================================
               IF ((I_CORRIG_TROU == 1).OR. &
                   (I_CORRIG_MULTI_AVAL == 1).OR. &
                   (I_CORRIG_PLAT == 1)) THEN
!                 ===========================================================
!                  S'il y a un autre voisin �gal au centre (Gradient = 0)
!                  => On baisse un peu le centre pour limiter les Plateaux
!                     Car on sait qu'il y a un Aval => Donc sans consequence
!                 ===========================================================
                  IF (ANY(GRADIENT == 0.)) THEN
                     TOPO(N) = TOPO(N) - 0.47 * (TOPO(N) - TOP_MIN)
                     KONT_VAR = KONT_VAR + 1
                  ENDIF
               ENDIF
            ENDIF
            IF (I_TROU(N) == 2) THEN
               IF (I_CORRIG_MULTI_AVAL == 1) THEN
!                 =============================================
!                  [I_TROU = 2] Correction des Multiples Avals
!                 =============================================
                  CALL Corrig_Multi_Avals(NTOT, EPS_TOP &
                            , IDOMAIN, NUM_VOIS, TOPO &
                            , N, SQRT_2, TOP_MIN, KONT_VAR)
               ENDIF
            ELSE IF (I_TROU(N) == 4) THEN
               IF (I_CORRIG_PLAT == 1) THEN
!                 =================================================
!                  [I_TROU = 4] Correction des Fonds Plats Uniques
!                 =================================================
!                 =========================================================================
!                  On sait qu'il existe des Voisins Plus Haut (sauf si G�om�trie sp�ciale)
!                  => On se place entre le Plus Bas Autre Voisin
!                  * On ne prend pas en compte la direction du Grad Mini = 0.
!                    => On la neutralise
!                  * On prend alors la direction du mini restant (qui est > 0)
!                 =========================================================================
                  GRAD_LOC(:) = GRADIENT(:)
                  WHERE (GRAD_LOC == 0.) GRAD_LOC = 9999.
                  K_G_MIN = MINLOC(GRAD_LOC , DIM=1)
                  K_AVANT_MIN = K_G_MIN
                  NUM_AVANT_MIN = NUM_VOIS(K_AVANT_MIN , N)
                  IF (NUM_AVANT_MIN > 0) THEN
                     TOP_AVANT_MIN = TOPO(NUM_AVANT_MIN)
                     TOPO(N) = TOPO(N) + 0.47 * (TOP_AVANT_MIN - TOPO(N))
                     KONT_VAR = KONT_VAR + 1
                  ENDIF
               ENDIF
            ELSE IF (I_TROU(N) == 3) THEN
               IF (I_CORRIG_PLAT == 1) THEN
!                 =============================================================
!                  [I_TROU = 3] Correction de (quelques) Fonds Plats Multiples
!                 =============================================================
                  DO K=1,8
                     IF (GRADIENT(K) == GRAD_MIN) THEN
                        NUM_VOIS_K  = NUM_VOIS(K , N)
                        IF (NUM_VOIS_K  == 0) CYCLE
                        IF (IDOMAIN(NUM_VOIS_K) == 0) THEN
!                          ====================================================
!                           Voisin hors domaine : De M�me Topo
!                           => Sans cons�quence => Baisse la topo Hors Domaine
!                           => 1 Aval => Sort (I_TROU = 0)
!                           N.B. Au lieu de choisir le premier ext�rieur
!                                on pourrait choisir ...
!                          ====================================================
                           TOPO(NUM_VOIS_K) = TOPO(NUM_VOIS_K) - 0.67 * EPS_TOP
                           KONT_VAR = KONT_VAR + 1
                           I_TROU(N) = 0
                           EXIT
                        ENDIF
                     ENDIF
                  ENDDO
               ENDIF
            ENDIF
         ENDDO
      ENDDO
      END SUBROUTINE Anal_Topo_0
      SUBROUTINE Corrig_Multi_Avals(NTOT, EPS_TOP &
                            , IDOMAIN, NUM_VOIS, TOPO &
                            , N, SQRT_2, TOP_MIN, KONT_VAR)
!=======================================================================
!   ********************
!   *Corrig_Multi_Avals*               BRGM     B.P. 36009
!   ********************               45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      Correction des Avals Multiples
!=======================================================================
!      En Entr�e :
!      TOP_MIN = Topogr. des Avals Multiples
!      EPS_TOP = Variation unitaire de Topogr.
!      TOPO() = Altitude Topogr.
!      En Retour :
!      TOPO() = Altitude Topogr. modifi�e par endroits
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NTOT, N
      REAL   , INTENT(IN) :: EPS_TOP, TOP_MIN, SQRT_2
      INTEGER, INTENT(IN OUT) :: KONT_VAR
      INTEGER, DIMENSION(NTOT), INTENT(IN) :: IDOMAIN
      INTEGER, DIMENSION(8 , NTOT), INTENT(IN) :: NUM_VOIS
      REAL   , DIMENSION(NTOT), INTENT(IN OUT) :: TOPO
!     ========
!      Locaux
!     ========
      REAL   , DIMENSION(8) :: GRAD_LOC, GRAD_MULT
      INTEGER, DIMENSION(8) :: NUM_VOIS_LOC
      REAL    :: GRAD_MUL_MIN, TOP_MULT_MIN
      INTEGER :: K, K_MULT_MIN, MULT, NUM_VOIS_K, NUM_MULT_MIN, K_G_MIN
!     =======
!      D�but
!     =======
!     ============================================
!      On examine les Voisins des Multiples Avals
!      et si Topo = 9999 !
!     ============================================
      GRAD_MULT(:) = 9999.
      BAL_MUL: DO MULT=1,8
!        ==============================
!         Balayage des Multiples Avals
!        ==============================
         NUM_VOIS_K = NUM_VOIS(MULT , N)
         IF (NUM_VOIS_K == 0) CYCLE
!        ==============================
!         Voisin Hors Domaine
!         N.B. => On pourrait sortir !
!        ==============================
         IF (IDOMAIN(NUM_VOIS_K) == 0) CYCLE
         IF (TOPO(NUM_VOIS_K) /= TOP_MIN) CYCLE
!        =========================================================
!         On a trouv� un des Multiples
!         => On va examiner les Voisins de cette direction : MULT
!            Cad les voisins de la maille : NUM_VOIS_K
!        =========================================================
!        ===============================================
!         On charge les Voisins de la maille NUM_VOIS_K
!         (1 des mailles Multiples)
!        ===============================================
         NUM_VOIS_LOC(1:8) = NUM_VOIS(1:8 , NUM_VOIS_K)
!        ==========================================================
!         On annule les directions :
!         Maille n� N elle m�me, et ses voisines : NUM_VOIS(: , N)
!        ==========================================================
         GRAD_LOC(:) = 9999.
         DO K=1,8
!           =========================================
!            Balayage des 8 voisins du Multiple MULT
!           =========================================
            IF (NUM_VOIS_LOC(K) == 0) CYCLE
!           =====================
!            Voisin hors domaine
!           =====================
            IF (NUM_VOIS_LOC(K) == N) THEN
!              ====================
!               Ignore la maille N
!              ====================
               NUM_VOIS_LOC(K) = 0
               EXIT
            ENDIF
            IF (ANY( NUM_VOIS(1:8 , N) == NUM_VOIS_LOC(K) )) THEN
!              ===================================
!               Ignore les Voisins de la maille N
!              ===================================
               NUM_VOIS_LOC(K) = 0
               EXIT
            ENDIF
            GRAD_LOC(K) = TOPO(NUM_VOIS_LOC(K)) - TOP_MIN
            IF (K >= 5) GRAD_LOC(K) = GRAD_LOC(K) / SQRT_2
         ENDDO
         GRAD_MUL_MIN = MINVAL(GRAD_LOC)
         GRAD_MULT(MULT) = GRAD_MUL_MIN
!        ===========================================================
!         Gradient le Plus Bas du multiple MULT => GRAD_MULT(MULT)
!         S'il est > 0 => Bloqu�
!         S'il est = 0 => MULT arrive sur plat
!         S'il est < 0 => MULT a au moins 1 Sortie
!                         Il faudra voir quelle MULT � la meilleure
!        ===========================================================
      ENDDO BAL_MUL
!     ============================
!      Selection du meilleur MULT
!     ============================
      K_G_MIN = MINLOC(GRAD_MULT, DIM=1)
      K_MULT_MIN = K_G_MIN
      NUM_MULT_MIN = NUM_VOIS(K_MULT_MIN , N)
      TOP_MULT_MIN = TOPO(NUM_MULT_MIN)
!     ========================================================
!      On a trouv� K_MULT_MIN et NUM_MULT_MIN
!      => * Si TOP_MULT_MIN <= TOP_MIN - 1.2 * EPS_TOP
!           => Baisse cette direction de EPS_TOP (Favorise)
!      => * Si TOP_MULT_MIN >  TOP_MIN - 1.2 * EPS_TOP
!           => Remonte les autres de EPS_TOP
!     ========================================================
      IF (TOP_MULT_MIN <= TOP_MIN - 1.2 * EPS_TOP) THEN
!        =================================================
!         Possible de baisser NUM_MULT_MIN de 1 * EPS_TOP
!        =================================================
         IF (TOPO(NUM_MULT_MIN) /= 9999.) THEN
            TOPO(NUM_MULT_MIN) &
          = TOPO(NUM_MULT_MIN) - 1.07 * EPS_TOP
            KONT_VAR = KONT_VAR + 1
         ENDIF
      ELSE
!        =====================================================
!         Pas possible de baisser NUM_MULT_MIN de 1 * EPS_TOP
!         => On remonte tous les autres
!        =====================================================
!           =======================================================================
!            ### Au lieu de chercher les autres avec la m�me TOP_MIN
!            ### il faudrait chercher les autres MULT avec le m�me gradient
!            ### mais compte tenu de 1.414 peu probable que m�me grad si diff topo
!           =======================================================================
!         N.B. => Pas s�r qu'on a trouv� un NUM_MULT_MIN
!        =====================================================
         DO MULT=1,8
!           ========
!            Autres
!           ========
            IF (MULT == K_MULT_MIN) CYCLE
            NUM_VOIS_K = NUM_VOIS(MULT , N)
            IF (NUM_VOIS_K == 0) CYCLE
!           =====================
!            Voisin hors domaine
!           =====================
            IF (TOPO(NUM_VOIS_K) /= TOP_MIN) CYCLE
!           ==============================================
!            C'est un voisin avec m�me Topo => Le remonte
!            (Pas trop pour ne pas cr�er de Puits)
!           ==============================================
            TOPO(NUM_VOIS_K) = TOP_MIN + 0.67 * EPS_TOP
         ENDDO
         KONT_VAR = KONT_VAR + 1
      ENDIF
      END SUBROUTINE Corrig_Multi_Avals

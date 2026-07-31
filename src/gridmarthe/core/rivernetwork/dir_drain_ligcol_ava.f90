      SUBROUTINE Dir_Drain_LigCol_Ava(KOLCEN, LIGCEN, IANGL, KOLAVA, LIGAVA)
!=======================================================================
!   **********************
!   *Dir_Drain_LigCol_Ava*             BRGM     B.P. 36009
!   **********************             45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      Calcule KOLAVA , LIGAVA avals de la maille (KOLCEN , LIGCEN)
!      à partir de IANGL = 1001 à 1008
!      KOLAVA = 9999  &  LIGAVA = 9999 si Direction Incorrecte
!                                      par ex 9999 ou 0 ...
!      IANGL => (KOLAVA , LIGAVA)
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN)  :: KOLCEN, LIGCEN, IANGL
      INTEGER, INTENT(OUT) :: KOLAVA, LIGAVA
!     ========
!      Locaux
!     ========
!     =======
!      Début
!     =======
!     ==================================================
!      1001-1004 => Sens aiguilles montre : N-E-S-W
!      1005-1008 => Directions Obliques   : NE-SE-SW-NW
!     ==================================================
      IF (ABS(IANGL) == 9999) THEN
!        ================================
!         Direction non définie => +9999
!        ================================
         KOLAVA = 9999
         LIGAVA = 9999
      ELSE
!        =============
!         Cas général
!        =============
         KOLAVA = KOLCEN
         LIGAVA = LIGCEN
!        ==================================================
!         1001-1004 => Sens aiguilles montre : N-E-S-W
!         1005-1008 => Directions Obliques   : NE-SE-SW-NW
!        ==================================================
         SELECT CASE (IANGL)
         CASE (1001)
!           ======
!            Nord
!           ======
            LIGAVA = LIGCEN - 1
         CASE (1002)
!           =====
!            Est
!           =====
            KOLAVA = KOLCEN + 1
         CASE (1003)
!           =====
!            Sud
!           =====
            LIGAVA = LIGCEN + 1
         CASE (1004)
!           =======
!            Ouest
!           =======
            KOLAVA = KOLCEN - 1
         CASE (1005)
!           ==========
!            Nord_Est
!           ==========
            KOLAVA = KOLCEN + 1
            LIGAVA = LIGCEN - 1
         CASE (1006)
!           =========
!            Sud_Est
!           =========
            KOLAVA = KOLCEN + 1
            LIGAVA = LIGCEN + 1
         CASE (1007)
!           ===========
!            Sud_Ouest
!           ===========
            KOLAVA = KOLCEN - 1
            LIGAVA = LIGCEN + 1
         CASE (1008)
!           ============
!            Nord_Ouest
!           ============
            KOLAVA = KOLCEN - 1
            LIGAVA = LIGCEN - 1
         CASE DEFAULT
!           ===========================
!            Incorrect => Angle = 9999
!           ===========================
            KOLAVA = 9999
            LIGAVA = 9999
         END SELECT
      ENDIF
      END SUBROUTINE Dir_Drain_LigCol_Ava

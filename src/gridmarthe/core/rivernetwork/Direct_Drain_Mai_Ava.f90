      SUBROUTINE Direct_Drain_Mai_Ava(NTOT, NKOL, NLIG, ORIENT, NMAI_AVAL)
!=======================================================================
!   **********************
!   *Direct_Drain_Mai_Ava*             BRGM     B.P. 36009
!   **********************             45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      Calcule le numéro NMAI_AVAL(1:NTOT) de la maille Aval
!      à partir des orientations 1001 à 1008
!      NMAI_AVAL =     0 si orientation incorrecte
!      NMAI_AVAL = -9999 si sort du rectangle
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NTOT, NKOL, NLIG
      REAL   , DIMENSION(NTOT), INTENT(IN)  :: ORIENT
      INTEGER, DIMENSION(NTOT), INTENT(OUT) :: NMAI_AVAL
!     ========
!      Locaux
!     ========
      INTEGER :: N, IANGL, LIGCEN, KOLCEN, LIGAVA, KOLAVA, NUAVA
!     =======
!      Début
!     =======
      NMAI_AVAL(1:NTOT) = 0
      DO N=1,NTOT
         IANGL = NINT(ORIENT(N))
!        ==================================================
!         1001-1004 => Sens aiguilles montre : N-E-S-W
!         1005-1008 => Directions Obliques   : NE-SE-SW-NW
!        ==================================================
         IF (ABS(IANGL) == 9999) CYCLE
         LIGCEN = (N - 1) / NKOL + 1
         KOLCEN = N - (LIGCEN - 1) * NKOL
!        ==============================================
!         IANGL => (KOLAVA , LIGAVA)
!         *** Att : Routine appelée plusieurs fois ***
!        ==============================================
         CALL Dir_Drain_LigCol_Ava(KOLCEN, LIGCEN, IANGL, KOLAVA, LIGAVA)
         IF ((KOLAVA == 9999).AND.(LIGAVA == 9999)) THEN
!           ===========================
!            Incorrect => Angle = 9999
!            => Laisse NMAI_AVAL = 0
!           ===========================
            CYCLE
         ENDIF
!        ========================================
!         Vérif si sort du rectangle du maillage
!        ========================================
         IF ((KOLAVA < 1).OR.(KOLAVA > NKOL).OR. &
             (LIGAVA < 1).OR.(LIGAVA > NLIG)) THEN
!           =======================================================================
!            Sort du rectangle du maillage (ennuyeux mais doit être vérifié avant)
!            => Met NMAI_AVAL = -9999
!           =======================================================================
            NMAI_AVAL(N) = -9999
            CYCLE
         ENDIF
!        =====================
!         NUAVA = Maille Aval
!        =====================
         NUAVA = (LIGAVA - 1) * NKOL + KOLAVA
         NMAI_AVAL(N) = NUAVA
      ENDDO
      END SUBROUTINE Direct_Drain_Mai_Ava

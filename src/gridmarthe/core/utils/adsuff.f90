      PURE SUBROUTINE Ajout_Toujours_Extens(NOMENT , NOMSOR , EXT)
!=======================================================================
!   ***********************
!   *Ajout_Toujours_Extens*            BRGM     B.P. 36009
!   ***********************            45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 07/11/2017
!=======================================================================
!     Addition d'une Extension EXT au nom NOMENT pour former NOMSOR
!     Entrée :
!      NOMENT = nom avec ou sans Extension
!      EXT    = Extension
!     Sortie :
!      NOMSOR = RACINE[NOMENT] // EXT  *Toujours ajout*
!     N.B. Remplace : Adsuff(NOMENT , NOMSOR , EXT)
!=======================================================================
      IMPLICIT NONE
      CHARACTER (LEN=*), INTENT(IN)  :: NOMENT, EXT
      CHARACTER (LEN=*), INTENT(IN OUT) :: NOMSOR
!     ========
!      Locaux
!     ========
      INTEGER :: LONG, ICROCH, IPOINT
!     =======
!      Début
!     =======
!     ========================================================
!      "]" pour séparer les directories sur certains systèmes
!     ========================================================
      LONG   = LEN_TRIM(NOMENT)
      ICROCH = INDEX(NOMENT, "]")
!     ==================================================================
!      Position du "." de l'extension (sans compter ce qui précède "]")
!     ==================================================================
      IPOINT = INDEX(NOMENT(ICROCH+1:LONG), ".", BACK=.TRUE.)
      IF (IPOINT <= 0) THEN
!        ==========================
!         Il n'y a pas d'extension
!        ==========================
         IPOINT = LEN_TRIM(NOMENT) + 1
      ELSE
!        ======================
!         Il y a une extension
!        ======================
         IPOINT = IPOINT + ICROCH
      ENDIF
!     =====================
!      Rajoute l'extension
!     =====================
      NOMSOR = NOMENT(1:IPOINT-1)//"."//EXT
      END SUBROUTINE Ajout_Toujours_Extens

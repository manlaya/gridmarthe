      SUBROUTINE XY_DXDY(X0, Y0, XCENLU, YCENLU, DXLU, DYLU, NLIG, NKOL &
          , IOUCON, INVY, IER)
!===========================================================================
!   **********
!   *XY_DXDY *                         BRGM     B.P. 36009
!   **********                         45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 30/01/2023
!===========================================================================
!     NLIG, NKOL = Nombre maxi de Lignes et de Colonnes (de XCENLU , YCENLU)
!     XCENLU = Tableau des Abscisses des noeuds
!     YCENLU = Tableau des Ordonnees des noeuds
!     X0     = Abscisse de l'Origine
!     Y0     = Ordonnee de l'Origine
!     NLIG   = Nombre de Lignes
!     NKOL   = Nombre de Colonnes
!     INVY = 0 Si les DY sont donn�s de Haut en Bas (cf mod�les)
!            1 Si les DY sont donn�s de Bas en Haut
!     IER  = Code : Si > = 0 Messages d'erreurs
!                   Si   < 0 Pas de messages d'erreurs
!       En Retour
!     DXLU = Tableau des Largeurs DX des NKOL Colonnes
!     DYLU = Tableau des Hauteurs DY des NLIG Lignes
!     IER  = Nombre d'erreurs
!
!     X0  X1      X2          X3
!      I--O--I----O----I------O------I
!      I     I         I             I
!      <-DX1-><--DX2---><----DX3----->
!===========================================================================
      IMPLICIT NONE
      REAL, DIMENSION(*) :: XCENLU, YCENLU, DXLU, DYLU
      ! CHARACTER (LEN=200), DIMENSION(25) :: WINT_200_BUFF
      ! COMMON/WINT_200_WRITE/WINT_200_BUFF
      INTEGER, INTENT(IN OUT) :: IER
      INTEGER, INTENT(IN) :: NLIG, NKOL, INVY, IOUCON
      REAL   , INTENT(IN) :: X0, Y0
!     ========
!      Locaux
!     ========
      INTEGER :: MUET, IERDX, IERDY, I, IND, IERR
      REAL    :: XCEN_P, XCEN_PP, DX, XDEB &
               , YCEN_P, YCEN_PP, DY, YDEB
!     =======
!      D�but
!     =======
      MUET = MERGE(1, 0,(IER < 0))
      IER = 0
!     ================================================
!      V�rification des X et Y  et calcul des DX , DY
!     ================================================
!     ======================================
!      V�rification des X et calcul des DX
!     ======================================
      IERDX = 0
      XCEN_P = XCENLU(1) - ABS(XCENLU(1) - X0)
      XDEB = X0
      DO I=1,NKOL
         XCEN_PP = XCENLU(I)
         DX = 2. * (XCENLU(I) - XDEB)
         IF (DX <= 0.) THEN
!           ========
!            Erreur
!           ========
            IER = IER + 1
            IF ((IERDX == 0).AND.(MUET == 0).AND.(IOUCON >= 0)) THEN
            !    WRITE (WINT_200_BUFF, 9001, IOSTAT=IERR) I, XDEB, XCENLU(I)
               WRITE(*, 9001, IOSTAT=IERR) I, XDEB, XCENLU(I)
            !    CALL WRIT_ECR(IOUCON,WINT_200_BUFF,0)
            ENDIF
            IERDX = IERDX + 1
            DXLU(I) = ABS(XCENLU(I) - XCEN_P)
            DX      = DXLU(I)
         ELSE
            DXLU(I) = DX
         ENDIF
         XDEB   = XDEB + DX
         XCEN_P = XCEN_PP
      ENDDO
!     ====================================================================
!      V�rification des Y et calcul des DY
!      INVY = 0 si les DY sont donn�s de Haut en Bas (cf mod�les)
!      INVY = 1 si les DY sont donn�s de Bas en Haut (Interpolations ...)
!     ====================================================================
      IERDY = 0
      YDEB  = Y0
      IND = MERGE(NLIG, 1, (INVY == 0))
      YCEN_P = YCENLU(IND) - ABS(YCENLU(IND) - Y0)
      DO I=1,NLIG
         IND = MERGE(NLIG - I + 1, I, (INVY == 0))
         YCEN_PP = YCENLU(IND)
         DY = 2. * (YCENLU(IND) - YDEB)
         IF (DY <= 0.) THEN
!           ========
!            Erreur
!           ========
            IER = IER + 1
            IF ((IERDY == 0).AND.(MUET == 0).AND.(IOUCON >= 0)) THEN
            !    WRITE (WINT_200_BUFF, 9002, IOSTAT=IERR) I, YDEB, YCENLU(IND)
                WRITE(*, 9002, IOSTAT=IERR) I, YDEB, YCENLU(IND)
            !    CALL WRIT_ECR(IOUCON,WINT_200_BUFF,0)
            ENDIF
            
            IERDY = IERDY + 1
            DYLU(IND) = ABS(YCENLU(IND) - YCEN_P)
            DY        = DYLU(I)
         ELSE
            DYLU(IND) = DY
         ENDIF
         YDEB = YDEB + DY
         YCEN_P = YCEN_PP
      ENDDO
#ifndef ENGLISH
 9001 FORMAT (" ** Erreur dimension Colonne",I4 &
             ," X Gauche=",ES10.3," X Centre=",ES10.3,T77," **")
 9002 FORMAT (" ** Erreur dimension Ligne  ",I4 &
             ," Y Bas   =",ES10.3," Y Centre=",ES10.3,T77," **")
#else
9001 FORMAT (" ** Dimension error, Column ",I4 &
            ," X Left=",ES10.3," X Center=",ES10.3,T77," **")
9002 FORMAT (" ** Dimension error, Row    ",I4 &
            ," Bottom=",ES10.3," Center=",ES10.3,T77," **")
#endif
      END SUBROUTINE XY_DXDY

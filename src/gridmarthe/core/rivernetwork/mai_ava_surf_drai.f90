      SUBROUTINE Mai_Ava_Surf_Drai(SURF_DRA,PRESEN,NMAI_AVAL &
              ,NLIG,NKOL,NTOT,LISTIN,DX_LU,DY_LU)
!=======================================================================
!   *******************                PROGRAMMATHEQUE HYDROGEOLOGIE
!   *Mai_Ava_Surf_Drai*                BRGM     B.P. 6009
!   *******************                45060 ORLEANS CEDEX
!   AUTEUR(S):THIERY D.
!   DATE: 29/05/2005
!=======================================================================
!      CALCULE LA SURFACE DRAINEE
!      A PARTIR DE :
!      * PRESENCE
!      * NUMERO DE LA NMAI_AVAL (1:NTOT) DE LA MAILLE AVAL
!=======================================================================
      IMPLICIT NONE
      INTEGER ,INTENT(IN) :: NLIG,NKOL,NTOT,LISTIN
      INTEGER ,DIMENSION(NTOT) ,INTENT(IN)  :: NMAI_AVAL
      REAL    ,DIMENSION(NTOT) ,INTENT(IN)  :: PRESEN
      REAL    ,DIMENSION(NKOL) ,INTENT(IN)  :: DX_LU
      REAL    ,DIMENSION(NLIG) ,INTENT(IN)  :: DY_LU
      REAL    ,DIMENSION(NTOT) ,INTENT(OUT) :: SURF_DRA
!     ============
!      INTERFACES
!     ============
        INTERFACE
         SUBROUTINE PEEK_4_MES(ISTOP,IMMEDIAT)
          INTEGER ,INTENT(IN)  :: IMMEDIAT
          INTEGER ,INTENT(OUT) :: ISTOP
         END SUBROUTINE PEEK_4_MES
        END INTERFACE
!     ========
!      LOCAUX
!     ========
      CHARACTER (LEN=80) :: TITAUX
      REAL    :: POURC,REALIS
      INTEGER ,DIMENSION(NTOT) :: IPASSE
      INTEGER :: LIG,KOL,N,NAVA,LIGAVA,KOLAVA,NCEN,LIGCEN,KOLCEN,KONT_MAIL &
                ,KONT,KONT_AUX,IPOURC,IERRAUX,ISTOP
      REAL    :: SURFMAI
!     =======
!      DEBUT
!     =======
      SURF_DRA(1:NTOT) = 0.
      KONT_MAIL = COUNT((PRESEN <= 0.).OR.(ABS(PRESEN) == 9999.))
      IF (KONT_MAIL <= 50000) THEN
         POURC = 0.05
      ELSE IF (KONT_MAIL <= 100000) THEN
         POURC = 0.01
      ELSE IF (KONT_MAIL <= 500000) THEN
         POURC = 0.001
      ELSE
         POURC = 0.0001
      ENDIF
      KONT = 0
      KONT_AUX = 0
      DO LIG=1,NLIG
         BAL_1: DO KOL=1,NKOL
            N = (LIG - 1) * NKOL + KOL
            IF ((PRESEN(N) <= 0.).OR.(ABS(PRESEN(N)) == 9999.)) CYCLE
            KONT = KONT + 1
            KONT_AUX = KONT_AUX + 1
            IF (KONT_AUX >= NINT(POURC * KONT_MAIL)) THEN
               KONT_AUX = 0
               IF (POURC >= 0.01) THEN
                  IPOURC = NINT(100. * REAL(KONT) / KONT_MAIL)
                  WRITE (TITAUX,*,IOSTAT=IERRAUX) "Calcul des surfaces drainées",IPOURC," %"
               ELSE
                  REALIS = 100. * REAL(KONT) / KONT_MAIL
                  WRITE (TITAUX,"(A,F8.2,A)",IOSTAT=IERRAUX) "Calcul des surfaces drainées",REALIS," %"
               ENDIF
               CALL WRIT_STATUS_BAR(TRIM(TITAUX) , 0 , 0)
               CALL PEEK_4_MES(ISTOP , 1)
            ENDIF
            IPASSE(1:NTOT) = 0
            SURFMAI = DX_LU(KOL) * DY_LU(LIG)
            SURF_DRA(N) = SURF_DRA(N) + SURFMAI
!           ===============
!            INIT DES *AVA
!           ===============
            NAVA = N
!           ====================
!            BALAYAGE DES AVALS
!           ====================
            DO WHILE (.TRUE.)
               NCEN = NAVA
               NAVA = NMAI_AVAL(NCEN)
               IF ((NAVA <= 0).OR.(NAVA == -9999)) CYCLE BAL_1
               LIGCEN = (NCEN - 1) / NKOL + 1
               KOLCEN = NCEN - (LIGCEN - 1) * NKOL
!              ===========================
!               VERIF SI SORT DU MAILLAGE
!              ===========================
               IF (NAVA > NTOT) THEN
                  IF (LISTIN > 0) THEN
                     WRITE (LISTIN,*) ' MAILLE LIG=',LIG,' KOL=',KOL
                     WRITE (LISTIN,*) ' LIGCEN,KOLCEN=',LIGCEN,KOLCEN
                     WRITE (LISTIN,*) " => SORT (NAVA=",NAVA," > NTOT)"
                   ENDIF
                  CYCLE BAL_1
               ENDIF
               IF (PRESEN(NAVA) <= 0) CYCLE BAL_1
               LIGAVA = (NAVA - 1) / NKOL + 1
               KOLAVA = NAVA - (LIGAVA - 1) * NKOL
               IF (IPASSE(NAVA) > 0) THEN
!                 ===================
!                  ERREUR DEJA PASSE
!                 ===================
                  IF (LISTIN > 0) THEN
                     WRITE (LISTIN,*) ' ## MAILLE LIG=',LIG,' KOL=',KOL
                     WRITE (LISTIN,*) '    LIGCEN,KOLCEN=',LIGCEN,KOLCEN
                     WRITE (LISTIN,*) '    => DEJA PASSE EN NAVA =',NAVA
                     WRITE (LISTIN,*) '       CAD EN LIGAVA,KOLAVA =',LIGAVA,KOLAVA
                  ENDIF
                  CYCLE BAL_1
               ENDIF
               SURF_DRA(NAVA) = SURF_DRA(NAVA) + SURFMAI
               IPASSE(NAVA) = 1
            ENDDO
         ENDDO BAL_1
      ENDDO
      END SUBROUTINE Mai_Ava_Surf_Drai

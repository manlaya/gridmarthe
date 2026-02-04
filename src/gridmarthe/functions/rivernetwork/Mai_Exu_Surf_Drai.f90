      SUBROUTINE Mai_Exu_Surf_Drai(SURF_DRA,PRESEN,ORIENT,HYDRO,NMAI_AVAL &
              ,NTOT,NKOL,LISTIN)
!=======================================================================
!   *******************
!   *Mai_Exu_Surf_Drai*                BRGM     B.P. 6009
!   *******************                45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 02/04/2018
!=======================================================================
!      Analyse des mailles hors Réseau Hydrographique
!      Détection des mailles Sortant du Domaine ou Non Définies
!      À partir de :
!      * Présence Domaine : PRESEN
!      * Présence Rivière : HYDRO
!      * Numéro de la NMAI_AVAL (1:NTOT) de la maille Aval
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NTOT,NKOL,LISTIN
      INTEGER, DIMENSION(NTOT), INTENT(IN)  :: NMAI_AVAL
      REAL   , DIMENSION(NTOT), INTENT(IN)  :: PRESEN,HYDRO,ORIENT
      REAL   , DIMENSION(NTOT), INTENT(IN)  :: SURF_DRA
!     ========
!      Locaux
!     ========
      CHARACTER (LEN=10), DIMENSION(8), PARAMETER :: CHAR_LIST_DIR = &
        (/"Nord      ","Est       ","Sud       ","Ouest     " &
         ,"Nord_Est  ","Sud_Est   ","Sud_Ouest ","Nord_Ouest"/)
      CHARACTER (LEN=10) , PARAMETER :: CHAR_UNKN = "Inconnu"
      CHARACTER (LEN=10) :: CHAR_DIR
      INTEGER :: N, NAVA, NBRE_EXUT, NBRE_UNDEF, IERRAUX, I_EXUT, LIG, KOL, IANGL
      REAL    :: SURF_EXUT, SURF_UNDEF
!     =======
!      Début
!     =======
      WRITE (LISTIN, 9002, IOSTAT=IERRAUX)
      NBRE_EXUT  = 0
      NBRE_UNDEF = 0
      SURF_EXUT  = 0.
      SURF_UNDEF = 0.
      DO N=1,NTOT
         IF ((PRESEN(N) <= 0.).OR.(ABS(PRESEN(N)) == 9999.)) CYCLE
         IF ((HYDRO(N) == 1.).OR.(ABS(HYDRO(N)) == 9999.)) CYCLE
!        =============================
!         Donc ici maille Non Rivière
!        =============================
         I_EXUT = 0
         NAVA = NMAI_AVAL(N)
         SELECT CASE (NAVA)
         CASE (0)
!           ===========
!            Incorrect
!           ===========
            NBRE_UNDEF = NBRE_UNDEF + 1
            SURF_UNDEF = SURF_UNDEF + SURF_DRA(N)
         CASE (-9999)
!           =============================================
!            Sort du rectangle
!            Att : Plus différencié (0 au lieu de -9999)
!           =============================================
            I_EXUT = 1
            NBRE_EXUT = NBRE_EXUT + 1
            SURF_EXUT = SURF_EXUT + SURF_DRA(N)
         CASE DEFAULT
!           =============
!            Cas général
!           =============
            IF ((PRESEN(NAVA) <= 0.).OR.(ABS(PRESEN(NAVA)) == 9999.)) THEN
!              ================
!               Sort du Domaine
!              ================
               I_EXUT = 1
               NBRE_EXUT = NBRE_EXUT + 1
               SURF_EXUT = SURF_EXUT + SURF_DRA(N)
            ENDIF
         END SELECT
         IF ((I_EXUT == 1).AND.(NBRE_EXUT <= 50)) THEN
            LIG = (N - 1) / NKOL + 1
            KOL = N - (LIG - 1) * NKOL
            IANGL = NINT(ORIENT(N))
            SELECT CASE (IANGL)
            CASE (1001:1008)
               CHAR_DIR = CHAR_LIST_DIR(IANGL - 1000)
            CASE DEFAULT
               CHAR_DIR = CHAR_UNKN
            END SELECT
            WRITE (LISTIN, 9003, IOSTAT=IERRAUX) N, KOL, LIG, IANGL, TRIM(CHAR_DIR)
         ENDIF
      ENDDO
      IF ((NBRE_UNDEF > 0).OR.(NBRE_EXUT > 0)) THEN
         IF ((ABS(SURF_UNDEF) <= 9e6).AND.(ABS(SURF_EXUT) <= 9e6)) THEN
            WRITE (LISTIN, 9001, IOSTAT=IERRAUX) NBRE_UNDEF, SURF_UNDEF, NBRE_EXUT, SURF_EXUT
         ELSE
            WRITE (LISTIN, 9000, IOSTAT=IERRAUX) NBRE_UNDEF, SURF_UNDEF, NBRE_EXUT, SURF_EXUT
         ENDIF
      ENDIF
 9000 FORMAT (/" Analyse des mailles Hors Réseau riviéres" &
             //I7," Mailles à direction indéfinie                  ; Surface drainée =",ES12.5 &
              /I7," Mailles à direction hors du domaine de surface ; Surface drainée =",ES12.5)
 9001 FORMAT (/" Analyse des mailles Hors Réseau riviéres" &
             //I7," Mailles à direction indéfinie                  ; Surface drainée =",F12.3 &
              /I7," Mailles à direction hors du domaine de surface ; Surface drainée =",F12.3)
 9002 FORMAT (/" Détection des mailles Hors Réseau riviéres"/)
 9003 FORMAT (/" Maille Num_Ordre n° ",I0," : Colonne = ",I0," , Ligne = ",I0 &
              /" => Direction (angle) = ",I0," (",A,")"," => Hors domaine surface")
      END SUBROUTINE Mai_Exu_Surf_Drai

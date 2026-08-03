      SUBROUTINE Convert_Direct_Drain(ITYP_DIRECT, NTOT, ORIENT)
!=======================================================================
!   **********************
!   *Convert_Direct_Drain*             BRGM     B.P. 36009
!   **********************             45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      Pre-traitement des Directions de Drainages : Met en 1001:1008
!      * ITYP_DIRECT = 0 => Angles ou 1001:1008 => Transforme => 1001:1008
!      * ITYP_DIRECT = 1 => ArcView 1:128       => Transforme => 1001:1008
!      Si 9999   => Laisse 9999
!      1001-1004 => Sens aiguilles Montre : N-E-S-W
!      1005-1008 => Directions Obliques   : NE-SE-SW-NW
!      1,2,4,8,16,32,64,128 = est à est sens aiguilles montre de 45° en 45°
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: ITYP_DIRECT, NTOT
      REAL   , DIMENSION(NTOT), INTENT(IN OUT) :: ORIENT
!     ========
!      Locaux
!     ========
      INTEGER :: N, IANGL
!     =======
!      Début
!     =======
      SELECT CASE (ITYP_DIRECT)
      CASE (1)
!        ===============
!         Arcview 1:128
!        ===============
         WHERE (ORIENT(1:NTOT) ==   1.) ORIENT(1:NTOT) = 1002.
         WHERE (ORIENT(1:NTOT) ==   2.) ORIENT(1:NTOT) = 1006.
         WHERE (ORIENT(1:NTOT) ==   4.) ORIENT(1:NTOT) = 1003.
         WHERE (ORIENT(1:NTOT) ==   8.) ORIENT(1:NTOT) = 1007.
         WHERE (ORIENT(1:NTOT) ==  16.) ORIENT(1:NTOT) = 1004.
         WHERE (ORIENT(1:NTOT) ==  32.) ORIENT(1:NTOT) = 1008.
         WHERE (ORIENT(1:NTOT) ==  64.) ORIENT(1:NTOT) = 1001.
         WHERE (ORIENT(1:NTOT) == 128.) ORIENT(1:NTOT) = 1005.
         WHERE (ORIENT(1:NTOT) ==   0.) ORIENT(1:NTOT) = 9999.
      CASE (0)
!        ======================
!         Angle ou 1001 à 1008
!        ======================
         DO N=1,NTOT
            IANGL = NINT(ORIENT(N))
!           ==================================================
!            1001-1004 => Sens aiguilles Montre : N-E-S-W
!            1005-1008 => Directions Obliques   : NE-SE-SW-NW
!           ==================================================
            SELECT CASE (IANGL)
            CASE (-22:22 , 338:360)
!              ======
!               Nord
!              ======
               IANGL = 1001
            CASE (68:112)
!              =====
!               Est
!              =====
               IANGL = 1002
            CASE (-180:-158 , 158:202)
!              =====
!               Sud
!              =====
               IANGL = 1003
            CASE (-112:-68 , 248:292)
!              =======
!               Ouest
!              =======
               IANGL = 1004
            CASE (23:67)
!              ==========
!               Nord_Est
!              ==========
               IANGL = 1005
            CASE (113:157)
!              =========
!               Sud_Est
!              =========
               IANGL = 1006
            CASE (-157:-113 , 203:247)
!              ===========
!               Sud_Ouest
!              ===========
               IANGL = 1007
            CASE (-67:-23 , 293:337)
!              ============
!               Nord_Ouest
!              ============
               IANGL = 1008
            CASE DEFAULT
!              ================================
!               En particulier : Valeur = 9999
!               => Laisse 9999
!              ================================
               CYCLE
            END SELECT
            ORIENT(N) = REAL(IANGL)
         ENDDO
      END SELECT
      END SUBROUTINE Convert_Direct_Drain

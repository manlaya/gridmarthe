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
      SUBROUTINE Num_8_Voisins(NLIG, NKOL, NTOT, IDOMAIN, NUM_VOIS)
!=======================================================================
!   ***************
!   *Num_8_Voisins*                    BRGM     B.P. 36009
!   ***************                    45060 Orl�ans C�dex
!   Auteur(s):THIERY D.
!   Date: 05/11/2022
!=======================================================================
!      Calcul des 8 Num�ros Voisins : NUM_VOIS(8 , NTOT)
!      Si Hors Limites NUM_VOIS (IDIR,N) = 0
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN) :: NLIG, NKOL, NTOT
      INTEGER, DIMENSION(NTOT), INTENT(IN) :: IDOMAIN
      INTEGER, DIMENSION(8 , NTOT), INTENT(OUT) :: NUM_VOIS
!     ========
!      Locaux
!     ========
      INTEGER :: LIG, KOL, N, K, INDLIG, LIGVOI, KOLVOI, NVOIS
!     =======
!      D�but
!     =======
      NUM_VOIS(: , 1:NTOT) = 0
      DO LIG=1,NLIG
         INDLIG = (LIG - 1) * NKOL
         DO KOL = 1,NKOL
            N = (LIG - 1) * NKOL + KOL
            IF (IDOMAIN(N) <= 0) CYCLE
            NUM_VOIS(: , N) = 0
            DO K=1,8
               LIGVOI = LIG
               KOLVOI = KOL
!              ============================================
!               1-4 => Sens Aiguilles montre : N-E-S-W
!               5-8 => Directions Obliques   : NE-SE-SW-NW
!              ============================================
               SELECT CASE (K)
               CASE (1)
!                 ======
!                  Nord
!                 ======
                  IF (LIG <= 1) CYCLE
                  LIGVOI = LIG - 1
               CASE (2)
!                 =====
!                  Est
!                 =====
                  IF (KOL >= NKOL) CYCLE
                  KOLVOI = KOL + 1
               CASE (3)
!                 =====
!                  Sud
!                 =====
                  IF (LIG >= NLIG) CYCLE
                  LIGVOI = LIG + 1
               CASE (4)
!                 =======
!                  Ouest
!                 =======
                  IF (KOL <= 1) CYCLE
                  KOLVOI = KOL - 1
               CASE (5)
!                 ==========
!                  Nord_Est
!                 ==========
                  IF (LIG <= 1) CYCLE
                  IF (KOL >= NKOL) CYCLE
                  LIGVOI = LIG - 1
                  KOLVOI = KOL + 1
               CASE (6)
!                 =========
!                  Sud_Est
!                 =========
                  IF (LIG >= NLIG) CYCLE
                  IF (KOL >= NKOL) CYCLE
                  LIGVOI = LIG + 1
                  KOLVOI = KOL + 1
               CASE (7)
!                 ===========
!                  Sud_Ouest
!                 ===========
                  IF (LIG >= NLIG) CYCLE
                  IF (KOL <= 1) CYCLE
                  LIGVOI = LIG + 1
                  KOLVOI = KOL - 1
               CASE (8)
!                 ============
!                  Nord_Ouest
!                 ============
                  IF (LIG <= 1) CYCLE
                  IF (KOL <= 1) CYCLE
                  LIGVOI = LIG - 1
                  KOLVOI = KOL - 1
               END SELECT
               NVOIS = (LIGVOI - 1) * NKOL + KOLVOI
               NUM_VOIS(K , N) = NVOIS
            ENDDO
         ENDDO
      ENDDO
      END SUBROUTINE Num_8_Voisins

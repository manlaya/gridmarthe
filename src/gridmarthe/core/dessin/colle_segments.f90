      PURE SUBROUTINE Colle_Segments(XD, YD, XF, YF, NBSEGM, COTEST, NPOINT, XM, YM, IER)
!=======================================================================
!   ****************
!   *Colle_Segments*                   BRGM     B.P. 6009
!   ****************                   45060 Orléans Cédex
!   Auteur(s):THIERY D.
!   Date: 04/08/2020
!=======================================================================
!     Re-colle les segments de Masque ou d'Isovaleur
!     Supprime les éventuels segments jumeaux
!      En Entrée :
!     NBSEGM = Nombre de segments [(XD,YD) - (XF,YF)]
!              Attention NBSEGM sera modifié
!     COTEST = Coté d'un segment (ou valeur moyenne)
!              => Sert à définir un test de précision
!      En sortie :
!     NPOINT Points (XM,YM)
!     XM et YM doivent avoir NBSEGM+1 places mini
!     NBSEGM = Nombre de segments restants
!              Attention NBSEGM est donc modifié
!     [(XD,YD) - (XF,YF)] des segments restants
!     IER = 0 si normal ... Sinon = 1
!=======================================================================
      IMPLICIT NONE
      INTEGER, INTENT(IN OUT) :: NBSEGM
      REAL   , DIMENSION(NBSEGM), INTENT(IN OUT) :: XD, YD, XF, YF
      REAL   , DIMENSION(*), INTENT(IN OUT) :: XM, YM
      REAL   , INTENT(IN) :: COTEST
      INTEGER, INTENT(OUT) :: IER, NPOINT
!     ========
!      Locaux
!     ========
      INTEGER, DIMENSION(NBSEGM+2) :: IUTIL
      REAL   , DIMENSION(NBSEGM+2) :: XTRAV, YTRAV
      INTEGER :: IDIMXX
      REAL    :: COTE, EPSI, XTEST, YTEST, XAUX, YAUX
      INTEGER :: I, ID, INIT, IAUX, KONT, KONT1, KONT2, KONUTI, NUM, NDEMI, ITROUVE
!     =======
!      Début
!     =======
      IDIMXX = NBSEGM + 2
      IER = 0
      IF (NBSEGM <= 0) THEN
         NPOINT = 0
         GO TO 999
      ENDIF
      COTE = COTEST
      IF (COTE <= 0.) COTE = 1.
      EPSI = COTE / 2000.
!     ======================
!      Départ Premier Point
!     ======================
      IUTIL(1:NBSEGM) = 0
      ID    = 1
      INIT  = ID
      KONT2 = 0
      XTRAV(1) = XD(ID)
      YTRAV(1) = YD(ID)
      KONT1 = 2
      XTRAV(KONT1) = XF(ID)
      YTRAV(KONT1) = YF(ID)
      XTEST = XF(ID)
      YTEST = YF(ID)
      BAL_SEGM1: DO WHILE (.TRUE.)
         KONUTI = 0
         BAL_I: DO I=1,NBSEGM
            IF (I == ID) CYCLE BAL_I
            IF (IUTIL(I) == 1) CYCLE BAL_I
            KONUTI = 1
            ITROUVE = 0
            IF ((XD(I) >= XTEST-EPSI).AND.(XD(I) <= XTEST+EPSI)) THEN
               IF ((YD(I) >= YTEST-EPSI).AND.(YD(I) <= YTEST+EPSI)) THEN
!                 ================
!                  Contact trouvé
!                 ================
                  ITROUVE = 1
               ENDIF
            ENDIF
            IF (ITROUVE == 1) THEN
!              ========================================================
!               Le Début du segment I touche la Fin du segment ID
!               Vérification que les 2 segments ne sont pas identiques
!              ========================================================
               IF ((XF(I) >= XD(ID)-EPSI).AND.(XF(I) <= XD(ID)+EPSI)) THEN
                  IF ((YF(I) >= YD(ID)-EPSI).AND.(YF(I) <= YD(ID)+EPSI)) THEN
!                    ===========================
!                     Les segments sont jumeaux
!                     => Pas trouvé
!                    ===========================
                     IUTIL(I) = 1
                     ITROUVE = 0
                  ENDIF
               ENDIF
            ENDIF
            IF (ITROUVE == 1) THEN
               NUM = I
               IUTIL(I) = 1
               IF (KONT1+1 > IDIMXX) THEN
!                 ========
!                  Erreur
!                 ========
                  IER = 1
                  GO TO 999
               ENDIF
               IF (I /= INIT) THEN
                  KONT1 = KONT1 + 1
                  XTRAV(KONT1) = XF(I)
                  YTRAV(KONT1) = YF(I)
                  XTEST = XF(I)
                  YTEST = YF(I)
               ENDIF
!              =======================================
!               On a trouvé le segment NUM qui touche
!              =======================================
               ID = NUM
               CYCLE BAL_SEGM1
            ENDIF
!           =================================================================
!            Pas trouvé :
!            => On essaie l'autre extrémité de I, c'est à dire à la Fin de I
!           =================================================================
            IF ((XF(I) < XTEST-EPSI).OR.(XF(I) > XTEST+EPSI)) CYCLE BAL_I
            IF ((YF(I) < YTEST-EPSI).OR.(YF(I) > YTEST+EPSI)) CYCLE BAL_I
!           ========================================================
!            La Fin du segment I touche la Fin du segment ID
!            Vérification que les 2 segments ne sont pas identiques
!           ========================================================
            IF ((XD(I) >= XD(ID)-EPSI).AND.(XD(I) <= XD(ID)+EPSI)) THEN
               IF ((YD(I) >= YD(ID)-EPSI).AND.(YD(I) <= YD(ID)+EPSI)) THEN
!                 ===========================
!                  Les segments sont jumeaux
!                 ===========================
                  IUTIL(I) = 1
                  CYCLE BAL_I
               ENDIF
            ENDIF
            NUM = I
            IUTIL(I) = 1
            IF (KONT1+1 > IDIMXX) THEN
!              ========
!               Erreur
!              ========
               IER = 1
               GO TO 999
            ENDIF
            IF (I /= INIT) THEN
               KONT1 = KONT1 + 1
               XTRAV(KONT1) = XD(I)
               YTRAV(KONT1) = YD(I)
               XTEST = XD(I)
               YTEST = YD(I)
            ENDIF
!           =======================================
!            On a trouvé le segment NUM qui touche
!           =======================================
            ID = NUM
            CYCLE BAL_SEGM1
         ENDDO BAL_I
         EXIT BAL_SEGM1
      ENDDO BAL_SEGM1
!     =========================================
!      On n'a pas trouvé de segment qui touche
!      On essaie de l'autre coté de INIT
!      Si (KONUTI == 0) plus de segments
!     =========================================
      IF (KONUTI /= 0) THEN
         ID = INIT
         KONT2 = 1
         XM(KONT2) = XD(ID)
         YM(KONT2) = YD(ID)
         XTEST = XD(ID)
         YTEST = YD(ID)
         BAL_SEG: DO WHILE (.TRUE.)
            KONUTI = 0
            BAL_I_2: DO I=1,NBSEGM
               IF (I == ID) CYCLE BAL_I_2
               IF (IUTIL(I) == 1) CYCLE BAL_I_2
               KONUTI = 1
               ITROUVE = 0
               IF ((XD(I) >= XTEST-EPSI).AND.(XD(I) <= XTEST+EPSI)) THEN
                  IF ((YD(I) >= YTEST-EPSI).AND.(YD(I) <= YTEST+EPSI)) THEN
                     ITROUVE = 1
                  ENDIF
               ENDIF
               IF (ITROUVE == 1) THEN
!                 ========================================================
!                  Le Début du segment I touche le Début du segment ID
!                  Vérification que les 2 segments ne sont pas identiques
!                 ========================================================
                  IF ((XF(I) >= XF(ID)-EPSI).AND.(XF(I) <= XF(ID)+EPSI)) THEN
                     IF ((YF(I) >= YF(ID)-EPSI).AND.(YF(I) <= YF(ID)+EPSI)) THEN
!                       ===========================
!                        Les segments sont jumeaux
!                        => Pas trouvé
!                       ===========================
                        IUTIL(I) = 1
                        ITROUVE = 0
                     ENDIF
                  ENDIF
               ENDIF
               IF (ITROUVE == 1) THEN
                  NUM = I
                  IUTIL(I) = 1
                  KONT2 = KONT2 + 1
                  IF (KONT2 > IDIMXX) THEN
!                    ========
!                     Erreur
!                    ========
                     IER = 1
                     GO TO 999
                  ENDIF
                  XM(KONT2) = XF(I)
                  YM(KONT2) = YF(I)
                  XTEST = XF(I)
                  YTEST = YF(I)
!                 =======================================
!                  On a trouvé le segment NUM qui touche
!                 =======================================
                  ID = NUM
                  CYCLE BAL_SEG
               ENDIF
!              ================================
!               Pas trouvé :
!               => On essaie l'autre extrémité
!              =================================
               IF ((XF(I) < XTEST-EPSI).OR.(XF(I) > XTEST+EPSI)) CYCLE BAL_I_2
               IF ((YF(I) < YTEST-EPSI).OR.(YF(I) > YTEST+EPSI)) CYCLE BAL_I_2
!              ========================================================
!               La Fin du segment I touche le Début du segment ID
!               Vérification que les 2 segments ne sont pas identiques
!              ========================================================
               IF ((XD(I) >= XF(ID)-EPSI).AND.(XD(I) <= XF(ID)+EPSI)) THEN
                  IF ((YD(I) >= YF(ID)-EPSI).AND.(YD(I) <= YF(ID)+EPSI)) THEN
!                    ===========================
!                     Les segments sont jumeaux
!                    ===========================
                     IUTIL(I) = 1
                     CYCLE BAL_I_2
                  ENDIF
               ENDIF
               NUM = I
               IUTIL(I) = 1
               KONT2 = KONT2 + 1
               IF (KONT2 > IDIMXX) THEN
!                 ========
!                  Erreur
!                 ========
                  IER = 1
                  GO TO 999
               ENDIF
               XM(KONT2) = XD(I)
               YM(KONT2) = YD(I)
               XTEST = XD(I)
               YTEST = YD(I)
!              =======================================
!               On a trouvé le segment NUM qui touche
!              =======================================
               ID = NUM
               CYCLE BAL_SEG
            ENDDO BAL_I_2
            EXIT BAL_SEG
         ENDDO BAL_SEG
!        ====================================================
!         On a trouvé aucun segment qui touche le segment ID
!        ====================================================
      ENDIF
!     ==============================================
!      Fin pour ce morceau de courbe
!       On occulte le premier numéro (car pas fait)
!       On inverse XM et on recolle les 2 bouts
!     ==============================================
      IUTIL(INIT) = 1
      IF (KONT2 <= 0) THEN
         KONT2 = 1
         XM(1) = XTRAV(1)
         YM(1) = YTRAV(1)
      ENDIF
      NDEMI = KONT2 / 2
      IF (NDEMI >= 1) THEN
         DO I=1,NDEMI
            IAUX = KONT2 - I + 1
            IF (IAUX > IDIMXX) THEN
!              ========
!               Erreur
!              ========
               IER = 1
               GO TO 999
            ENDIF
            XAUX = XM(I)
            YAUX = YM(I)
            XM(I) = XM(IAUX)
            YM(I) = YM(IAUX)
            XM(IAUX) = XAUX
            YM(IAUX) = YAUX
         ENDDO
      ENDIF
      IF (KONT1 >= 2) THEN
         DO I=2,KONT1
            IAUX = I + KONT2 - 1
            IF (IAUX > IDIMXX) THEN
!              ========
!               Erreur
!              ========
              IER = 1
              GO TO 999
            ENDIF
            XM(IAUX) = XTRAV(I)
            YM(IAUX) = YTRAV(I)
         ENDDO
      ENDIF
      NPOINT = KONT2 + KONT1 - 1
!     =================================================================
!      Fin pour ce morceau de courbe
!      On supprime les segments déjà utilisés (c_à-d avec IUTIL() = 1)
!      KONUTI = 1 s'il reste des segments
!      << Et on réajuste NBSEGM >>
!     =================================================================
      IF (KONUTI == 1) THEN
         KONT = 0
         DO I=1,NBSEGM
            IF (IUTIL(I) /= 1) THEN
               KONT = KONT + 1
               XD(KONT) = XD(I)
               YD(KONT) = YD(I)
               XF(KONT) = XF(I)
               YF(KONT) = YF(I)
            ENDIF
         ENDDO
         NBSEGM = KONT
      ELSE
         NBSEGM = 0
      ENDIF
  999 CONTINUE
      END SUBROUTINE Colle_Segments

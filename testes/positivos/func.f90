PROGRAM TESTFUN
      INTEGER X, R, DOBRO
      X = 7
      R = DOBRO(X)
      PRINT *, 'dobro=', R
      END

      INTEGER FUNCTION DOBRO(N)
      INTEGER N
      DOBRO = N * 2
      RETURN
      END

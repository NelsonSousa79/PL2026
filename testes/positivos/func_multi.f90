PROGRAM FMULT
      INTEGER A, B, R, SOMA
      A = 4
      B = 6
      R = SOMA(A, B)
      PRINT *, 'resultado=', R
      END

      INTEGER FUNCTION SOMA(X, Y)
      INTEGER X, Y
      SOMA = X + Y
      RETURN
      END

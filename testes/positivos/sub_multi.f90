PROGRAM SUBMULT
      INTEGER A, B
      A = 3
      B = 7
      CALL SOMAR(A, B)
      END

      SUBROUTINE SOMAR(X, Y)
      INTEGER X, Y, R
      R = X + Y
      PRINT *, 'soma=', R
      RETURN
      END

PROGRAM FEXPR
      INTEGER R, QUAD
      R = QUAD(3) + QUAD(4)
      PRINT *, 'soma quadrados=', R
      END

      INTEGER FUNCTION QUAD(N)
      INTEGER N
      QUAD = N * N
      RETURN
      END

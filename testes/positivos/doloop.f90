PROGRAM DOLOOP
      INTEGER I, SOMA
      SOMA = 0
      DO 10 I = 1, 10, 2
         SOMA = SOMA + I
10    CONTINUE
      PRINT *, 'soma=', SOMA
      END

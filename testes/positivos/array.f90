PROGRAM ARRAY
      INTEGER V(3)
      INTEGER I
      V(1) = 10
      V(2) = 20
      V(3) = 30
      DO 10 I = 1, 3
         PRINT *, 'V(', I, ')=', V(I)
10    CONTINUE
      END

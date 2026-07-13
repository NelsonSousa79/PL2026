PROGRAM LOGOP
      LOGICAL A, B, R
      A = .TRUE.
      B = .FALSE.
      R = A .AND. .NOT. B
      IF (R) THEN
         PRINT *, 'verdade'
      ENDIF
      END

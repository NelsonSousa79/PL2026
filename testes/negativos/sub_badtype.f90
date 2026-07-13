PROGRAM SUBBT
      LOGICAL B
      B = .TRUE.
      CALL DOBRA(B)
      END

      SUBROUTINE DOBRA(X)
      INTEGER X
      PRINT *, X * 2
      RETURN
      END

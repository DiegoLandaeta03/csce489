sqrt(Target, Root) :-
    Target >= 0,
    Tolerance is 0.0000000001,
    CurrentEst is Target,
    sqrt(Target, CurrentEst, Tolerance, Root).

% Base case: close enough
sqrt(Target, CurrentEst, Tolerance, CurrentEst) :-
    Error is abs(CurrentEst*CurrentEst - Target),
    Error < Tolerance.

% Recursive case
sqrt(Target, CurrentEst, Tolerance, FinalAnswer) :-
    Error is abs(CurrentEst*CurrentEst - Target),
    Error >= Tolerance,
    NewEst is (CurrentEst + Target/CurrentEst) / 2,
    sqrt(Target, NewEst, Tolerance, FinalAnswer).
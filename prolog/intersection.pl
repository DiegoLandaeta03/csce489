% base case for when there is an empty list 
intersection([], _, []).

% case for when Head is in List2
intersection([H|T], L2, [H|R]) :- member(H, L2), intersection(T, L2, R).

% case for when Head is not in List2
intersection([H|T], L2, R) :- \+ member(H, L2), intersection(T, L2, R).

% how to run - use prolog and do: consult('intersection.pl'). 
% then do: intersection([1,2,3,4], [2,4,6], X).
(:action pickup
  :parameters (?a ?b)
  :precondition (and (on ?a ?b) (clear ?a) (hand-empty))
  :effect (and
    (holding ?a)
    (clear ?b)
    (not (on ?a ?b))
    (not (clear ?a))
    (not (hand-empty))
  )
)

(:action puton
  :parameters (?a ?b)
  :precondition (and (holding ?a) (clear ?b))
  :effect (and
    (on ?a ?b)
    (clear ?a)
    (hand-empty)
    (not (holding ?a))
    (not (clear ?b))
  )
)
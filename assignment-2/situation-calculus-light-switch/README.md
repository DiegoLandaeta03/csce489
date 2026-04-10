# Situation Calculus for a Light Switch

This is a very small Situation Calculus example with one light and one action.
The light can either be on or off, and the action flips the switch.

## Fluent

`On(s)` means the light is on in situation `s`.

If `On(s)` is false, then the light is off.

## Action

`FlipSwitch` means flipping the switch.

## Initial Situation

The initial situation is `S0`, and the light starts off:

$$\neg On(S_0)$$

## Situation Calculus Axioms

### Precondition Axiom

The switch can always be flipped:

$$\forall s ; Poss(FlipSwitch, s)$$

### Successor State Axiom

Flipping the switch changes the state of the light:

$$\forall s ; On(do(FlipSwitch, s)) \leftrightarrow \neg On(s)$$

This means that if the light was off, it becomes on, and if it was on, it becomes off.

## Frame Axiom

The fluent `On` only changes when `FlipSwitch` happens. For any other action, the value of `On` stays the same:

$$\forall a \forall s ; (a \neq FlipSwitch \rightarrow (On(do(a,s)) \leftrightarrow On(s)))$$

## Explanation

The precondition axiom says that flipping the switch is always possible.
The successor state axiom says that flipping the switch toggles the light.
The frame axiom says that no other action changes whether the light is on or off.

## Example

Let

$$S_1 = do(FlipSwitch, S_0)$$

Since the initial state is

$$\neg On(S_0)$$

then by the successor state axiom:

$$On(S_1) \leftrightarrow \neg On(S_0)$$

So the light is on in `S1`.

Now let

$$S_2 = do(FlipSwitch, S_1)$$

Since `On(S1)` is true, then:

$$On(S_2) \leftrightarrow \neg On(S_1)$$

So the light is off again in `S2`.

## Conclusion

This example shows a simple Situation Calculus model with one fluent and one action. The action `FlipSwitch` is always possible, and each time it happens, it changes the light from on to off or from off to on.

# Opabinia - circuit layout

This page details a little how the circuit was made to fit
onto a 27 x 52 mm prototype pcb and soldered to become a
board ready to plug on the RPi's 20x2 GPIO pin set.

The pcb is sawed off to achieve the desired dimension, with
20x10 holes. Two sets of breakout pins will be soldered to
the board: a 20x2 female block for the RPi GPIO, and an
8x1 male set for the two proximity sensors.

The female block faces "downwards" and the male block "upward",
as in the following sketch:

<img src="schematics/breakout.png" alt="Breakout sketch" width="50%"/>

The precise location of each pin, each connection and each blob of tin
is detailed here below. One should be careful to think carefully the right order
when soldering (e.g. first the ground row, then the echo resistors, then the LED
sets, then the male breakout and finally the female breakout).

<img src="schematics/pcb.png" alt="PCB Schematics" width="80%"/>

## The result

Soldered board:

<img src="photos/board_front.jpg" alt="PCB Schematics" width="80%"/>

<img src="photos/board_back.jpg" alt="PCB Schematics" width="80%"/>

Plugged on the RPi:

<img src="photos/mounted_1.jpg" alt="PCB Schematics" width="80%"/>

<img src="photos/mounted_2.jpg" alt="PCB Schematics" width="80%"/>

<img src="photos/mounted_3.jpg" alt="PCB Schematics" width="80%"/>

## Further suggestion

One could restructure the above layout to make the board still
fit as an add-on to the RPi, but inward-facing, i.e. almost completely
hidden into the Raspberry case (except for the sensor pins and the LEDs).

This exercise is left to the reader (_because that was the original plan,
but due to a major overlooking I ended up with the board orientation as
shown and now I will happily stick to it_).

import rp2
from machine import Pin

@rp2.asm_pio(set_init=(rp2.PIO.IN_HIGH, rp2.PIO.IN_HIGH), push_thresh=26,
             autopush=True, in_shiftdir=rp2.PIO.SHIFT_LEFT,
             out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def wiegand_rx():
    """Implements a Wiegand received.
    I've tested it to work with frequencies of 50kHz (freq=50000) and higher.
    """
    mov(x, null)
    label('start')
    set(y, 1)
    # Actively wait for one pin to drop
    label('wait_drop')
    mov(osr, invert(pins))  # Use OSR because invert will make 3 MSBs = 1.
    out(x, 2)               # We keep only the 2 LSBs in x.
    jmp(not_x, 'wait_drop')
    # Now check if it was a one and save the appropriate value in ISR.
    # Wiegand data is transmitted MSB first, but we shift OSR right, so
    # a zero (OSR: 01) will be reflected in x as 10, and a one (OSR: 10)
    # will be reflected in X as 01 (which is the value stored in y)
    jmp(x_not_y, 'one')
    in_(null, 1)   # It was a 0, shift '0' into ISR
    jmp('wait_raise')
    label('one')
    in_(y, 1)      # It was a 1, shift y which has '1' into ISR
    label('wait_raise')  # wait until both pins raise to restart
    mov(osr, invert(pins))
    out(x, 2)
    jmp(x_dec, 'wait_raise') # if one pin is down, x > 0, keep waiting

sm = rp2.StateMachine(0, prog=wiegand_rx, freq=50000, in_base=Pin(0))
sm.active(1)
while True:
    n = sm.get()
    facility  = (n >> 17) & 0xff
    card_n = (n >> 1) & 0xffff
    print(f'{facility},{card_n}')

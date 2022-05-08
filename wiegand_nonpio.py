# Implements a Wiegand reader with IRQs and a circular queue
# Prints the received binary values (26 bit) on stdout
import machine
from machine import Pin

class Queue:
  def __init__(self, capacity=10):
    self.capacity = capacity
    self.queue = [0] * self.capacity
    self.r_pos = 0
    self.w_pos = 0

  def add(self, v):
    self.queue[self.w_pos] = v
    self.w_pos += 1
    if self.w_pos == self.capacity:
      self.w_pos = 0

  def remove(self):
    v = self.queue[self.r_pos]
    self.r_pos += 1
    if self.r_pos == self.capacity:
      self.r_pos = 0
    return v

  def size(self):
    if self.w_pos >= self.r_pos:
      return self.w_pos - self.r_pos
    return self.capacity - self.r_pos + self.w_pos

queue = Queue()
running = True

def printer():
  global queue
  while running:
    if queue.size() > 0:
      n = queue.remove()
      facility  = (n >> 17) & 0xff
      card_n = (n >> 1) & 0xffff
      print(f'{facility},{card_n}')
      #print(f'{queue.remove():026b}')

class FeedBack:
  def __init__(self):
      self.led = Pin(2, Pin.OUT, value=0)
      self.beep = Pin(3, Pin.OUT, value=0)
      self.count = 0

  def signal(self):
      self.count = 6
      def stop(t):
          self.led.toggle()
          self.beep.toggle()
          self.count -= 1
          if not self.count:
              t.deinit()
      pass
      self.led.toggle()
      self.beep.toggle()
      machine.Timer(mode=machine.Timer.ONE_SHOT, period=500, callback=stop)

p1 = Pin(2, Pin.OUT, value=0)
p2 = Pin(3, Pin.OUT, value=0)

class Word:
  """Stores the temporary 26 bit word being received and, once finished,
      writes it to the passed queue and starts anew."""
  def __init__(self, queue):
    self.value = 0
    self.bits = 0
    self.queue = queue
    self.fb = FeedBack()

  def add_bit(self, bit):
    #self.led.blink()
    self.value = (self.value << 1) | bit
    self.bits += 1
    if self.bits == 26:
      self.queue.add(self.value)
      self.value = 0
      self.bits = 0
      self.fb.signal()


word = Word(queue)

d0pin = machine.Pin(0, machine.Pin.IN)
d0pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=lambda x: word.add_bit(0))

d1pin = machine.Pin(1, machine.Pin.IN)
d1pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=lambda x: word.add_bit(1))

printer()

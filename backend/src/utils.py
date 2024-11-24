class Vec2:
  def __init__(self, x: int, y: int):
    self.x = x
    self.y = y

  def __str__(self):
    return f"Position({self.x}, {self.y})"

  def __eq__(self, other):
    return self.x == other.x and self.y == other.y

  def __hash__(self):
    return hash((self.x, self.y))

  def __add__(self, other):
    return Vec2(self.x + other.x, self.y + other.y)

  def __sub__(self, other):
    return Vec2(self.x - other.x, self.y - other.y)

  def __mul__(self, other):
    return Vec2(self.x * other, self.y * other)

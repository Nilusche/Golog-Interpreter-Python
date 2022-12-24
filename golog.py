# Implementing a golog interpreter

class S:
    def __init__(self, atoms, universe):
        self.atoms = atoms
        self.universe = universe


class Seq:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return str(self.left) + " : " + str(self.right)

class Test:
    def __init__(self, pred):
        self.pred = pred

    def __str__(self):
        return "?(" + str(self.pred) + ")"

class NonDet:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return str(self.left) + " # " + str(self.right)

class If:
    def __init__(self, cond, then, else_):
        self.cond = cond
        self.then = then
        self.else_ = else_

    def __str__(self):
        return "if (" + str(self.cond) + ") then " + str(self.then) + " else " + str(self.else_)

class While:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def __str__(self):
        return "while (" + str(self.cond) + ") do " + str(self.body)

class Star:
    def __str__(self):
        return "*"

class Pi:
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def __str__(self):
        return "pi " + self.var + " (" + str(self.expr) + ")"

class Proc:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def __str__(self):
        return "proc " + self.name + " = " + str(self.expr)

class PrimitiveAction:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name




class And:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return "(" + str(self.left) + " and " + str(self.right) + ")"

class Or:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return "(" + str(self.left) + " or " + str(self.right) + ")"

class Implies:  
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return "(" + str(self.left) + " -> " + str(self.right) + ")"

class Iff:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return "(" + str(self.left) + " <-> " + str(self.right) + ")"

class Not:
    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return "not (" + str(self.arg) + ")"

class ForAll:
    def __init__(self, var, pred):
        self.var = var
        self.pred = pred

    def __str__(self):
        return "forall " + str(self.var) + " (" + str(self.pred) + ")"

class Exists:
    def __init__(self, var, pred):
        self.var = var
        self.pred = pred

    def __str__(self):
        return "exists " + str(self.var) + " (" + str(self.pred) + ")"

    def substitute(self, var, val):
        if var == self.var:
            return self.pred
        else:
            return Exists(self.var, self.pred.substitute(var, val))

def do(E, S, S1):
    if(isinstance(E, Seq)):
        s2 = do(E.left, S, S1)
        if(s2 != None):
            return do(E.right, s2, S1)
        else:
            return None
    elif(isinstance(E, Test)):
        #check if holds
        if(holds(E.pred, S)):
            return S
        else:
            return None
    elif(isinstance(E, NonDet)):
        s2 = do(E.left, S, S1)
        if(s2 != None):
            return s2
        else:
            return do(E.right, S, S1)
    elif(isinstance(E, If)):
        if(E.cond(S)):
            return do(E.then, S, S1)
        else:
            return do(E.else_, S, S1)
    elif(isinstance(E, While)):
        if(E.cond(S)):
            s2 = do(E.body, S, S1)
            if(s2 != None):
                return do(E, s2, S1)
            else:
                return None
        else:
            return S
    elif(isinstance(E, Star)):
        return S
    elif(isinstance(E, Pi)):
        return S1
    elif(isinstance(E, Proc)):
        return do(E.expr, S, S1)
    elif(isinstance(E, PrimitiveAction)) and poss(E, S):
        return S
    else:
        return S1


def holds(P, S):
    if isinstance(P, And):
        return holds(P.left, S) and holds(P.right, S)
    elif isinstance(P, Or):
        return holds(P.left, S) or holds(P.right, S)
    elif isinstance(P, Implies):
        return not holds(P.left, S) or holds(P.right, S)
    elif isinstance(P, Iff):
        return (holds(Implies(P.left, P.right), S) and
                holds(Implies(P.right, P.left), S))
    elif isinstance(P, Not):
        return not holds(P.arg, S)
    elif isinstance(P, ForAll):
        return not holds(Exists(P.var, Not(P.pred)), S)
    elif isinstance(P, Exists):
        return any(holds(P.pred.substitute(P.var, val), S)
                   for val in S.universe)
    else:
        return P in S.atoms


### Example program

atoms = {"at_floor_1", "at_floor_2", "at_floor_3", "door_open", "door_closed", "elevator_up", "elevator_down"}
universe = {"floor_1", "floor_2", "floor_3", "elevator"}

# Define the primitive actions for your program
open_door = PrimitiveAction("open_door")
close_door = PrimitiveAction("close_door")
move_up = PrimitiveAction("move_up")
move_down = PrimitiveAction("move_down")

# Define your Golog program
def go_to_floor(n):
    if n == 1:
        return Test("at_floor_1")
    elif n == 2:
        return Test("at_floor_2")
    elif n == 3:
        return Test("at_floor_3")
    else:
        return Test(False)

def move_elevator(n):
    return Seq(close_door, Seq(If("at_floor_1", move_up, If("at_floor_3", move_down, Star())), go_to_floor(n)))

def open_close_door():
    return Seq(open_door, close_door)

def pickup_passenger():
    return NonDet(open_close_door(), Star())

def dropoff_passenger():
    return NonDet(open_close_door(), Star())

def serve_passenger(n):
    return Seq(move_elevator(n), NonDet(pickup_passenger(), dropoff_passenger()))

def serve_all_passengers(floors):
    if not floors:
        return Test(True)
    else:
        return Seq(serve_passenger(floors[0]), serve_all_passengers(floors[1:]))

def poss(action, state):
    if action == open_door:
        return "door_closed" in state.atoms and "at_floor_1" in state.atoms
    elif action == close_door:
        return "door_open" in state.atoms
    elif action == move_up:
        return "elevator_down" in state.atoms
    elif action == move_down:
        return "elevator_up" in state.atoms
    else:
        return False

#Define the initial state of your program
init_atoms = {"at_floor_1", "door_open"}
init_state = S(init_atoms, universe)

#Execute the program
final_state = do(universe, init_state, S(serve_passenger(2), universe))



print(final_state.atoms)


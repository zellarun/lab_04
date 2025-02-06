class VcdEntry:
    def __init__(self, time:int, state: str, width: int):
        self.time = time
        self.state = state
        self.width = width
        pass
    
    def as_binary_array(self):
        lower = self.state.lower()
        if lower[0] == "b":
            ret = [None] * self.width
            idx = 0
            for x in reversed(lower[1:]):
                ret[idx] = bool(int(x)) if x.isdigit() else None
                idx += 1
            return ret
        else:
            raise Exception("Cannot convert real to binary array")

class VcdSample:
    def __init__(self, time:int):
        self.time = time
        self.entries: list[VcdEntry] = {}

class VcdVar:
    def __init__(self, finish = None):
        self.type: str = None
        self.width: int = None
        self.marker: str = None
        self.name: str = None
        self.vector: str = None
        self.index: int = None
        self.states: list[VcdEntry] = []
        self.finish = finish
        pass
    
    def feed(self, bit):
        if self.type is None:
            self.type = bit
        elif self.width is None:
            self.width = int(bit)
        elif self.marker is None:
            self.marker = bit
        elif self.name is None:
            self.name = bit
        elif self.vector is None:
            self.vector = bit
    
    def feed_val(self, time:int, val: str):
        self.states.append(VcdEntry(time, val))
    
    def end(self):
        if self.finish is not None:
            self.finish()
        pass

class VcdScope:
    def __init__(self, parent = None):
        self.type: str = None
        self.name: str = None
        self.vars: list[VcdVar] = []
        self.parent: VcdScope = parent
        self.subscopes: list[VcdScope] = []
        pass

    def add_scope(self):
        sub = VcdScope(self)
        self.subscopes.append(sub)
        return sub
    
    def add_var(self, var):
        self.vars.append(var)
        if self.parent is not None:
            self.parent.add_var(var)
    
    def feed(self, content: str):
        if self.type is None:
            self.type = content
        elif self.name is None:
            self.name = content
    
    def end(self):
        pass

class VcdDate:
    def __init__(self):
        self.dateString = ""
        pass

    def feed(self, bit):
        self.dateString += " " + bit

    def end(self):
        self.dateString = self.dateString.strip()

class VcdTimescale:
    def __init__(self):
        self.timescale:str = ""
        self.actualTimescale:int = 1
    
    def feed(self, bit):
        self.timescale = bit
    
    def end(self):
        pass
        
class VcdSkip:
    def __init__(self, onDeath = None):
        self.onDeath = onDeath
        pass
    
    def feed(self, bit):
        pass

    def end(self):
        if self.onDeath is not None:
            self.onDeath()


class VcdFile:
    def add_date(self):
        self.date = VcdDate()
        return self.date

    def add_timescale(self):
        self.timescale = VcdTimescale()
        return self.timescale
    
    def add_scope(self):
        newscope = self.current_scope.add_scope()
        self.current_scope = newscope
        return newscope

    def go_upscope(self):
        self.current_scope = self.current_scope.parent
        return VcdSkip()

    def end_definitions(self):
        self.vars = list(self.var_ref.values())
        idx = 0
        for var in self.vars:
            var.index = idx
            idx += 1
        
        self.defining = False
        return VcdSkip()

    def add_var(self):
        newvar = VcdVar()
        def finish_var():
            nonlocal newvar
            if newvar.marker in self.var_ref:
                newvar = self.var_ref[newvar.marker]
            else:
                self.var_ref[newvar.marker] = newvar
            self.current_scope.add_var(newvar)
        newvar.finish = finish_var
        return newvar

    chunks = {
        "$date": lambda self: self.add_date(), 
        "$timescale": lambda self: self.add_timescale(),
        "$scope": lambda self: self.add_scope(),
        "$upscope": lambda self: self.go_upscope(),
        "$enddefinitions": lambda self: self.end_definitions(),
        "$dumpvars": lambda self: self,
        "$var": lambda self: self.add_var()
    }

    def __init__(self):
        self.scope = VcdScope()
        self.current_scope = self.scope
        self.vars: list[VcdVar] = []
        self.var_ref: dict[str, VcdVar] = {}
        
        self.timescale: VcdTimescale = None
        self.date: VcdDate = None
        self.defining = True
        self.time: int = 0
        self.samples: list[VcdSample] = []
        self.current_sample: VcdSample = None

    def feed_state(self, bit: str):
        if (bit[0] == "$"): return

        if (bit[0] == "#"):
            self.time = int(bit[1:])
            if self.current_sample is not None:
                self.samples.append(self.current_sample)
                self.current_sample = VcdSample(self.time)
            else:
                self.current_sample = VcdSample(self.time)

            self.current_sample.entries = [None] * len(self.vars)
            self.current_sample.time = self.time
        else:
            if bit[0].lower() == 'b' or bit[0].lower() == 'r':
                bits = bit.split()
                val = bits[0]
                var = bits[1]
                idx = self.var_ref[var].index
                width = self.vars[idx].width
                self.current_sample.entries[idx] = VcdEntry(self.time, val, width)
            else:
                state = str(bit[0])
                var = bit[1]
                idx = self.var_ref[var].index
                width = self.vars[idx].width
                self.current_sample.entries[idx] = VcdEntry(self.time, state, width)


    def feed(self, bit: str):
        if (bit in VcdFile.chunks):
            return VcdFile.chunks[bit](self)
        else:
            if bit.startswith("$"):
                return VcdSkip()
            else:
                if self.defining == False:
                    self.feed_state(bit)

    def end(self):
        pass

    def get_marker(self, name):
        for var in self.vars:
            if var.name == name:
                return var.index
        
        return None

    def load(self, fname):
        self.defining = True
        self.dump_started = False
        self.dump_complete = False
        with open(fname) as f:
            stack = []
            sp = self
            content = f.readlines()
            for line in content:
                if self.defining:
                    for bit in line.split():
                        if (bit == "$end"):
                            sp.end()
                            if (len(stack) == 0): break
                            sp = stack.pop()
                            continue

                        newsp = sp.feed(bit)
                        if (newsp is not None):
                            stack.append(sp)
                            sp = newsp
                else:
                    self.feed_state(line)

class VcdCursor:
    def __init__(self, file: VcdFile):
        self.file = file
        self.pos = 0
        self.values: list[VcdEntry] = [None] * len(self.file.vars)
        self.time: int = 0
        self.update()
    
    def update(self):
        idx = 0
        self.time = self.file.samples[self.pos].time
        for val in self.file.samples[self.pos].entries:
            self.values[idx] = val or self.values[idx]
            idx += 1
    
    def end(self):
        if self.pos >= len(self.file.samples) - 1:
            return True
        return False

    def rend(self):
        if self.pos == 0:
            return True
        return False

    def next(self):
        check = self.end()
        if not check:
            self.pos += 1
            self.update()
        return check
    
    def prev(self):
        check = self.rend()
        if not check:
            self.pos -= 1
            self.update()
        return check
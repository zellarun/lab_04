#!/usr/bin/env python3

from dataclasses import dataclass
import subprocess
from pathlib import Path
import sys
import vcd
import os

IVL_PATH = "iverilog"
VVP_PATH = "vvp"
GTK_PATH = "gtkwave"

if os.name == "nt":
    IVL_PATH = "C:\\iverilog\\bin\\" + IVL_PATH
    VVP_PATH = "C:\\iverilog\\bin\\" + VVP_PATH
    GTK_PATH = "C:\\iverilog\\gtkwave\\bin\\" + GTK_PATH

@dataclass
class SigInterest:
    bitmask: list[int]
    expected_index: int = -1
    actual_index: int = -1

SIGNALS_OF_INTEREST : dict[str, SigInterest] = {
    "led": SigInterest([0, 1, 2]),
    "sw": SigInterest([0, 1, 2, 3]),
}

def check_signal(name: str, sig: SigInterest, expected: vcd.VcdCursor, actual: vcd.VcdCursor):
    e = expected.values[sig.expected_index].as_binary_array()
    a = actual.values[sig.actual_index].as_binary_array()

    def print_fail_header(name, time):
        print(f"FAILURE: in signal {name} at {time}:")

    passed = True
    for mask in sig.bitmask:
        check = e[mask] == a[mask]
        if not check:
            if passed:
                print_fail_header(name, expected.time)
            print(f"\tBit {mask} should be {e[mask]} but is {a[mask]}")
        passed = passed and check
    
    return passed


def check_dumps(expected: vcd.VcdCursor, actual: vcd.VcdCursor):
    run = True
    passed = True
    while run:
        for name, sig in SIGNALS_OF_INTEREST.items():
            check = check_signal(name, sig, expected, actual)
            passed = passed and check

        run = run and not expected.next()
        run = run and not actual.next()
    
    return passed

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def execute_test():
    verilog_files = Path(".").glob("*.v")
    out = subprocess.run([IVL_PATH] + [f"{x}" for x in verilog_files], capture_output=True, text=True)
    if (out.returncode != 0):
        print(out.stderr)
        exit(out.returncode)
    subprocess.run([VVP_PATH, "a.out"], capture_output=True)

def grade_test():
    expected = vcd.VcdFile()
    expected.load("expected_output.vcd")
    actual = vcd.VcdFile()
    actual.load("dump.vcd")

    # Map signals to index
    for name, sig in SIGNALS_OF_INTEREST.items():
        sig.actual_index = actual.get_marker(name)
        sig.expected_index = expected.get_marker(name)

    ecurs = vcd.VcdCursor(expected)
    acurs = vcd.VcdCursor(actual)

    passed = check_dumps(ecurs, acurs)
    
    print(f"{'Passed' if passed else 'Failed'}")

def view_dump():
    subprocess.run([GTK_PATH, "dump.vcd"])

if __name__ == "__main__":
    execute_test()
    grade_test()
    # Uncomment this line to view your waveform!
    # view_dump()
from pyteal import *
from crowdfunding import approval_program, clear_program
import os

def compile_teal():
    approval = compileTeal(approval_program(), mode=Mode.Application, version=8)
    clear = compileTeal(clear_program(), mode=Mode.Application, version=8)
    os.makedirs("build", exist_ok=True)
    with open("build/approval.teal", "w") as f:
        f.write(approval)
    with open("build/clear.teal", "w") as f:
        f.write(clear)
    print("Wrote build/approval.teal and build/clear.teal")

if __name__ == "__main__":
    compile_teal()

import argparse
import clingo
import os

facts_file = "facts.txt"
solver_file = "asp_program.txt"
parser = argparse.ArgumentParser(prog="Tents", description="Solve a Tents & Trees puzzle in txt format")
parser.add_argument("filename", help="The name and path of the input file")
parser.add_argument("-s", "--solver", help="Allows to specify the name of a file with a different solver program", dest="solver", default=solver_file)
parser.add_argument("-f", "--facts", help="Allows to specify the name of the file to use to store facts", dest="facts", default=facts_file)
parser.add_argument("--graphic", help="Print the solution graphically (tents are indicated with the letter A)", action="store_true", dest="graphic", default=False)
parser.add_argument("--to-file", help="Print the (graphical) solution to the specified filepath", dest="to_file", default=None)
parser.add_argument("--pretty", help="Prettify the graphical output (if enabled) by placing sums for rows and columns before the grid and spacing out cells so that they line up with the respective column", action="store_true", dest="pretty", default=False)

args = parser.parse_args()

if not os.path.exists(args.filename):
    print("The specified input file could not be found.")

if not os.path.exists(args.solver):
    print("The specified solver could not be found.")

facts = []
graphical = []
with open(args.filename, "r") as fin:
    rows, columns = fin.readline().split()
    facts.append(f"lines({rows}).\n")
    facts.append(f"columns({columns}).\n")
    i = 1
    j = 1
    trees = 0
    for line in fin.readlines():
        if line.startswith("T") or line.startswith("."):
            graphical.append([])
            j = 1
            line, sum = line.strip().split(" ", 1)
            for c in line:
                if c == ".":
                    facts.append(f"free({i},{j}).\n")
                    if args.pretty: c += " "
                elif c == "T":
                    facts.append(f"tree({i},{j}).\n")
                    trees += 1
                    if args.pretty: c += " "
                elif c == " ":
                    pass
                graphical[i-1].append(c)
                j += 1
            facts.append(f"rowsum({i},{int(sum)}).\n")
            graphical[i-1].append(sum + " " if args.pretty else " " + sum)
        else:
            graphical.append([])
            j = 1
            sums = line.strip().split(" ")
            for sum in sums:
                facts.append(f"colsum({j},{int(sum)}).\n")
                graphical[i-1].append(" " + sum)
                j += 1
        i += 1
    facts.append(f"totaltrees({trees}).\n")

with open(facts_file, "w+") as fout:
    fout.writelines(facts)

def model_solution(model):
    if not args.graphic and not args.to_file:
        print(f"Answer: {model}")
    elif args.graphic or args.to_file:
        for symbol in model.symbols(shown=True):
            i, j = symbol.arguments[0].number, symbol.arguments[1].number
            graphical[i-1][j-1] = "A " if args.pretty else "A"
        if args.pretty: 
            graphical.insert(0, graphical.pop(-1))
            for line in graphical[1:]:
                line.insert(0, line.pop(-1))
        if args.graphic:
            print(" ", end="")
            for line in graphical:
                print("".join(line))
        if args.to_file:
            try:
                with open(args.to_file, "w+") as fout:
                    fout.writelines(["".join(line) + "\n" for line in graphical])
            except OSError as err:
                print("Could not open solution destination file for writing.")
                print(f"Error: {err}")

def sat_check(result):
    if result.unsatisfiable:
        print("UNSATISFIABLE")
    elif result.unknown:
        print("UNKNOWN SATISFIABILITY")

ctl = clingo.Control()
ctl.load(args.facts)
ctl.load(args.solver)
ctl.ground([("base", [])])
ctl.solve(on_model=model_solution, on_finish=sat_check)
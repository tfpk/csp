from mip import *

CLASS_AMOUNT = {
    'mon13a': [1, 1],
    'mon13b': [1, 1],
    'tue13a': [1, 1],
    'tue13b': [1, 1],
    'wed13a': [1, 1],
    'wed13b': [1, 1],
}
CLASSES = CLASS_AMOUNT.keys()

# Name: [CLASSES[n] for n in range(len(CLASSES))]
TUTOR_AVAIL = {
    "Andrew": [2, 3, 0, 3, 0, 0],
    "Tom":    [3, 3, 0, 0, 3, 0],
    "Alvin":  [0, 0, 3, 3, 0, 0],
    "Sabine": [3, 0, 0, 0, 0, 3],
    "Anosua": [0, 0, 0, 0, 3, 0],
    "Tanya":  [0, 3, 3, 0, 0, 0]
}
MAX_AVAIL = 3

# Name: [AT, TT]
TUTOR_AMOUNT = {
    "Tom": [0,2],
    "Andrew": [0,2],
    "Alvin": [1,1],
    "Sabine": [1,1],
    "Anosua": [2,0],
    "Tanya": [2,0]
}
TUTORS = TUTOR_AVAIL.keys()

problem = Model(sense=MAXIMIZE)

tt_alloc = [[problem.add_var(f't({t}, {c})', var_type=BINARY) for c in range(len(CLASSES))] for t in range(len(TUTORS))]
at_alloc = [[problem.add_var(f'at({t}, {c})', var_type=BINARY) for c in range(len(CLASSES))] for t in range(len(TUTORS))]

# A tutor's allocations must be equal to "however many we assign them in the tutor_rating"
for t, tutor_name in enumerate(TUTORS):
    problem += xsum(at_alloc[t][c] for c in range(len(CLASSES))) == TUTOR_AMOUNT[tutor_name][0], f"at_max_alloc({t})"
    problem += xsum(tt_alloc[t][c] for c in range(len(CLASSES))) == TUTOR_AMOUNT[tutor_name][1], f"tt_max_alloc({t})"

# A class may only have however many tutors/ats we said you could.
for c, class_name in enumerate(CLASSES):
    print(class_name, CLASS_AMOUNT[class_name])
    problem += xsum(at_alloc[t][c] for t in range(len(TUTORS))) == CLASS_AMOUNT[class_name][0], f"at_class_max_alloc({c})"
    problem += xsum(tt_alloc[t][c] for t in range(len(TUTORS))) == CLASS_AMOUNT[class_name][1], f"tt_class_max_alloc({c})"

for t, tutor_name in enumerate(TUTORS):
    for c, class_name in enumerate(CLASSES):
        for clash_c, clash_class_name in enumerate(CLASSES):
            # if they're similar but different, only one can be taken.
            if class_name[:5] == clash_class_name[:5] and class_name != clash_class_name:
                problem += at_alloc[t][c] + tt_alloc[t][c] + at_alloc[t][clash_c] + tt_alloc[t][clash_c] <= 1, f"at_tt_not_possible({t}, {c})"
            if class_name == clash_class_name:
                problem += at_alloc[t][c] + tt_alloc[t][c] <= 1, f"at_tt_not_possible({t}, {c})"

problem.objective = maximize(xsum([[TUTOR_AVAIL[tutor_name][c] for t, tutor_name in enumerate(TUTORS) if at_alloc[t][c] + tt_alloc[t][c] >= 1] for c, class_name in enumerate(CLASSES)]))

problem.write('model')
problem.optimize()

print(problem.num_solutions)
if problem.num_solutions:
    print("           | ", end="")
    for c, class_name in enumerate(CLASSES):
        print(f"{class_name:8} | ", end="")
    print("")
    for t, tutor_name in enumerate(TUTORS):
        print(f"{tutor_name:10} | ", end="")
        for c, class_name in enumerate(CLASSES):
            did_print = False
            if tt_alloc[t][c].x > 0.99:
                print(f"{'TUTOR':8} | ", end="")
                did_print = True
            if at_alloc[t][c].x > 0.99:
                print(f"{'ASSIST':8} | ", end="")
                did_print = True
            if not did_print:
                print(' '*8 + ' | ', end="")
        print()

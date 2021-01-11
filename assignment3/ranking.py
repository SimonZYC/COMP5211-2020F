from z3 import *

# define 4 people
Bob, Jim, Lisa, Mary = Ints('Bob Jim Lisa Mary')
People = [Bob, Jim, Lisa, Mary]
PeopleName = ['Bob', 'Jim', 'Lisa', 'Mary']

# whether they are bio major: 1 for yes; 0 for no
isBobBM, isJimBM, isLisaBM, isMaryBM = Bools('isBobBM isJimBM isLisaBM isMaryBM') 
PeopleBM = [isBobBM, isJimBM, isLisaBM, isMaryBM]

s = Solver()
 
# The rank of one student must be in range of [1,4]
for person in People:
    s.add(person <= 4, person >= 1) 

# 1. Lisa is not next to Bob in the ranking
s.add(Lisa != Bob - 1, Lisa != Bob + 1)

# 2. Jim is ranked immediately ahead of a biology major
stat2 = []
for index, person in enumerate(People):
    if person.sexpr() != Jim.sexpr():
        stat2.append(And(Jim == person - 1, PeopleBM[index] == True))
        # stat2.append(Jim == person - 1)

s.add(Or([*stat2]))

# 3. Bob is ranked immediately ahead of Jim
s.add(Bob == Jim - 1)

# 4. One of the women (Lisa and Mary) is a biology major
s.add(Or(isLisaBM == True, isMaryBM == True))

# 5. One of the women is ranked first
s.add(Or(Lisa == 1, Mary == 1))

# no one share the same rank
s.add(Distinct(*People))

# Solve the model
s.check()
mdl = s.model()

# Output results as required
results = []
for d in mdl.decls():
    if d.name() in PeopleName:
        results.append((d.name(), mdl[d].as_long()))

nameSorted, _ = zip(*sorted(results, key=lambda x : x[1]))

print(list(nameSorted))

# print(mdl)
from z3 import *

# room 1, 2, 3; true if there is a lady; false if there is a tiger
l1, l2, l3 = Bools('l1 l2 l3')
roomVar = ['l1', 'l2', 'l3']

# sign 1, 2, 3; true if it was true; otherwise false
s1, s2, s3 = Bools('s1 s2 s3')

s = Solver()

s.add(
	If(s1, 1, 0) + If(s2, 1, 0) + If(s3, 1, 0) <= 1, # At most one of the three signs is true.
	If(l1, 1, 0) + If(l2, 1, 0) + If(l3, 1, 0) == 1, # There is one lady.
	If(l1, 0, 1) + If(l2, 0, 1) + If(l3, 0, 1) == 2, # There are two tigers.
	s1 == Not(l1), # Room I: Tiger is in this room.
	s2 == l2, # Room II : Lady is in this room.
	s3 == Not(l2) # Room III: A tiger is in Room II.
)

s.check()
mdl = s.model()
outputMap = {'l1': 'I', 'l2': 'II', 'l3': 'III'}

# print(mdl)
for d in mdl.decls():
	if d.name() in roomVar:
		if mdl[d]:
			print(outputMap[d.name()])
		

'''
Model:
[l2 = False,
 l1 = True,
 l3 = False,
 s3 = True,
 s2 = False,
 s1 = False]
'''
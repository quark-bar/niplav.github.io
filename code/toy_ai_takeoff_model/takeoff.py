#!/usr/bin/env python3

# Can't be used for terrain generation because of recursiveness,
# which makes some diamond values lack seed values

import random
import numpy as np

def fill_space(space, dim, size, minval, maxval):
	"""Fill a dim-dimensional discrete space of ℕ^{size} with
	some random hyperplane with values ranging from minval to
	maxval. Returns a ℕ^{size} array. Changes space in-place."""

	offset=np.array([0]*dim)
	n_diam_square_rec(space, dim, offset, size, minval, maxval)
	return space

def n_diam_square_rec (space, dim, offset, size, minval, maxval):
	if size==1:
		return

	center=np.array([size//2]*dim)
	center=offset+center

	if size==len(space):
		b=1
	else:
		b=0

	cornerspos=[('{0:0'+str(dim)+'b}').format(i) for i in range(2**dim)]
	cornerspos=[list(i) for i in cornerspos]
	cornerspos=list(map((lambda x: list(map(int, x))), cornerspos))
	cornerspos=np.array(cornerspos)
	corners=np.array([(i*(size-b))+offset for i in cornerspos])

	cornersum=0
	for corner in corners:
		cornersum=cornersum+space[tuple(corner)]

	val=(cornersum/len(corners))+random.randint(minval, maxval)
	space[tuple(center)]=val

	nsize=size//2

	# Recursive diamond step here (dim times)
	explored=np.array([False]*dim)

	for i in range(0,dim):
		explored[i]=True
		ncenter1=np.array(center)
		ncenter2=np.array(center)
		ncenter1[i]=ncenter1[i]+nsize
		ncenter2[i]=ncenter2[i]-nsize
		diamond_rec(space, ncenter1, dim-1, nsize, explored, round(minval*extrfact), round(maxval*extrfact))
		diamond_rec(space, ncenter2, dim-1, nsize, explored, round(minval*extrfact), round(maxval*extrfact))
		explored[i]=False

	# Recursive square step
	for pos in cornerspos:
		noffset=(pos*nsize)+offset
		n_diam_square_rec(space, dim, noffset, nsize, round(minval*extrfact), round(maxval*extrfact))

# TODO: using len(explored) to mean the dimension is questionable

def diamond_rec(space, center, dim, size, explored, minval, maxval):
	# Field already assigned or dimension is 0
	# Only a heuristic, use {True, False}^dim instead?
	if dim==0 or space[tuple(center)]!=0:
		return

	# Actually assign diamond-based values
	counter=0
	diamondsum=0
	diamondpos=np.array(center)

	for i in range(0, len(explored)):
		tmp=diamondpos[i]
		ndp1=diamondpos[i]+size
		ndp2=diamondpos[i]-size
		if 0<=ndp1<len(space):
			diamondpos[i]=ndp1
			diamondsum+=space[tuple(diamondpos)]
			counter+=1
		if 0<=ndp2<len(space):
			diamondpos[i]=ndp2
			diamondsum+=space[tuple(diamondpos)]
			counter+=1
		diamondpos[i]=tmp

	val=(diamondsum/counter)+random.randint(minval, maxval)
	space[tuple(center)]=val

	# Recurse
	for i in range(0, len(explored)):
		if not explored[i]:
			explored[i]=True

			# Possibly beware by-reference passing here!

			ncenter1=np.array(center)
			ncenter2=np.array(center)
			ncv1=ncenter1[i]+size
			ncv2=ncenter2[i]-size
			if ncv1>=0:
				ncenter1[i]=ncv1
				diamond_rec(space, ncenter1, dim-1, size, explored, round(minval*extrfact), round(maxval*extrfact))
			if ncv2>=0:
				ncenter2[i]=ncv2
				diamond_rec(space, ncenter2, dim-1, size, explored, round(minval*extrfact), round(maxval*extrfact))
			explored[i]=False

def climb(space, pos, size, dim):
	"""At position pos in space, do some kind of climbing."""

	return climb_dim(space, pos, size, dim)

def climb_dim(space, pos, size, dim):
	"""Look in direction of each dimension (not two dimensions at
	once), then choose maximum spot."""

	maxpos=np.array(pos)
	for i in range(0, dim):
		pos[i]+=1
		if 0<=pos[i]<size:
			if space[tuple(pos)]>space[tuple(maxpos)]:
				maxpos=np.array(pos)
		pos[i]-=2
		if 0<=pos[i]<size:
                        if space[tuple(pos)]>space[tuple(maxpos)]:
                                maxpos=np.array(pos)
		pos[i]+=1
	return maxpos

def climb_hypcub(space, pos):
	"""Look one unit-hypercube around, choose maximum."""

	return pos

def search_around(space, pos, size, dim, intelligence):
	"""At position pos in space, dependent on current optimization
	power, search around in the neighbouring space to find the
	minimum in the subspace searched. This subspace can be an n-ball
	or an n-cube."""

	step=round(intelligence**(1/dim))
	subpos=[slice(0,0)]*dim
	for i in range(0, dim):
		subpos[i]=slice(max(0,pos[i]-step), min(size-1, pos[i]+step))
	subspace=space[tuple(subpos)]
	mp=np.where(subspace == np.amax(subspace))
	pos=np.array([list(mp[i])[0]+subpos[i].start for i in range(0, dim)])
	return pos

extrfact=0.5

dim=5
size=33
minval=0
maxval=255
lognormm=2
lognormvar=5
space=np.zeros([size]*dim)

fill_space(space, dim, size, minval, maxval)

pos=[random.randint(0, size-1) for i in range(0, dim)]

rounds=4096
growth=1.001

factor=1

for i in range(0,rounds):
	factor*=growth
	intelligence=max(1, space[tuple(pos)])*factor
	print(space[tuple(pos)])
	print(intelligence)
	print("------------")
	pos=climb(space, pos, size, dim)
	pos=search_around(space, pos, size, dim, intelligence)


import csv
from pyplasm import *
from numpy import *

def ggpl_multistore_house(folderPath):


	def get_positionXYZ(hpcObj):
		
		bx,by,bz = SIZE([1,2,3])(hpcObj)
		c = CUBOID([.1,.1,.1])
		box = STRUCT([c,hpcObj])
		box = BOX([1,2,3])(box)
		distance = SIZE([1,2,3])(box)
		position = [distance[0]-bx,distance[1]-by,distance[2]-bz]
		
		return position

	def ggpl_create_house(folderPath): 
		
		def get_lines_from_csv(filename):
			lines = [] #[[x1,y1,x2,y2],[...]]

			file = open(folderPath + filename,'rt')
			try:
				reader = csv.reader(file)
				for row in reader:
					line = []
					for n in row:
						line.append(float(n))
					lines.append(line)
			finally:
				file.close()

			polyline = []

			for line in lines:
				polyline.append(POLYLINE([[line[0],line[1]],[line[2],line[3]]]))

			return STRUCT(polyline)    

		#muri esterni -----------------------
		extWalls = get_lines_from_csv('muriEsterni.lines')
		extWalls = PROD([OFFSET([4,4])(extWalls), Q(40)])

		#muri interni -----------------------
		intWalls = get_lines_from_csv('muriInterni.lines')
		intWalls = PROD([OFFSET([3,3])(intWalls), Q(40)]) #3d
		intWalls = DIFFERENCE([intWalls, extWalls])

		#buchi porte ------------------------
		doors = get_lines_from_csv('porte.lines')
		doors = SOLIDIFY(doors)
		doors = PROD([doors, Q(30)]) #3d

		#buchi finestre ---------------------
		windows1 = get_lines_from_csv('finestre.lines')
		windows1 = SOLIDIFY(windows1)
		windows1 = T(3)(10)(PROD([windows1, Q(20)])) #3d

		#pavimenti legno --------------------
		woodFloors = get_lines_from_csv('pavLegno.lines')
		woodFloors = TEXTURE("textures/parquet.jpg")(SOLIDIFY(woodFloors))

		#pavimenti piastrelle ----------------
		wcFloors = get_lines_from_csv('pavPiastrelle.lines')
		wcFloors = TEXTURE(['textures/piastr.jpg',True, False, 1, 1, PI/2., 5,5])(SOLIDIFY(wcFloors))

		#unisco pavimenti
		floors = STRUCT([woodFloors, wcFloors])
		frame = STRUCT([extWalls, intWalls])
		frameWithHoles = DIFFERENCE([frame, windows1, doors, floors]) #creo buchi per porte e finestre
		home = (STRUCT([frameWithHoles, floors]))
		
		windowsStruct = build_windows(frame, folderPath + 'finestre.lines')
		doorsStruct = build_doors(frame, folderPath + 'porte.lines')

		#scale
		x = 20/SIZE([1])(home)[0]
		y = 16/SIZE([2])(home)[0]
		z = 4/SIZE([3])(home)[0]
		
		home = S([1,2,3])([x,y,z])(STRUCT([COLOR(YELLOW)(frameWithHoles), floors]))
		home = STRUCT([home, windowsStruct, doorsStruct])
		
		return home


	# Si appoggia a due funzioni ausiliarie citate in precedenza:
	# * build_windows()
	# * build_doors()

	def build_windows(frame, windowsFilePath): 
		
		#DATI FINESTRE DI TIPO 1
		X = [0.1,0.05,0.5,0.05,0.05,0.5,0.05,0.1]
		Z = [0.1,0.05,0.8,0.05,0.8,0.05,0.1]
		Y = [0.04,0.02,0.04]
		occupancy = [[[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]], 
				[[1,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,1]], 
				[[1,0,0,0,0,0,0,1],[1,1,0,1,1,0,1,1],[1,0,0,0,0,0,0,1]],
				[[1,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,1]],
				[[1,0,0,0,0,0,0,1],[1,1,0,1,1,0,1,1],[1,0,0,0,0,0,0,1]],
				[[1,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,1]],
				[[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]]]
		
		windowsList = []
		
		#scale factors
		x = 20/SIZE([1])(frame)[0]
		y = 16/SIZE([2])(frame)[0]
		z = 4/SIZE([3])(frame)[0]
		
		file = open(windowsFilePath, 'rt')
		lines = [] #[[x1,y1,x2,y2],[...]]
		try:
			reader = csv.reader(file)
			for row in reader:
				line = []
				for n in row:
					line.append(float(n))
				lines.append(line)
		finally:
			file.close()
			
		nWindows = len(lines)/4 #numero di finestre
		
		#per ogni finestra calcolo dimensione e posizione
		for i in range(nWindows):
			windowPol = []
			for line in lines[:4]:
				windowPol.append(POLYLINE([[line[0],line[1]],[line[2],line[3]]]))
			lines = lines[4:]
			window = STRUCT(windowPol)
			window = T(3)(10)(PROD([SOLIDIFY(window), Q(20)]))
			frameWithHole = DIFFERENCE([frame, window])
			window = DIFFERENCE([frame, frameWithHole])
			window = S([1,2,3])([x,y,z])(window)
			bx,by,bz = SIZE([1,2,3])(window)
			if (bx<by):
				px,py,pz = get_positionXYZ(window)
				window = R([1,2])(PI/2)(ggpl_window(X,Y,Z,occupancy)(by,bx,bz))
				window = T([1,2,3])([px+bx,py,pz])(window)
			else:
				window = T([1,2,3])(get_positionXYZ(window))(ggpl_window(X,Y,Z,occupancy)(bx,by,bz))
			
			windowsList.append(window)
		
		windows = STRUCT(windowsList)
		return windows


	#funzione del workshop_07 relativa alle finestre ----------------------------------------------

	def ggpl_window(X,Y,Z, occupancy):
		
		def window_builder(dx,dy,dz):

			glassW = 0.006 #glass width
			window = []
			for y in range(0,len(Y)):

				for z in range(0,len(Z)):

					for x in range(0,len(X)):

						if (occupancy[z][y][x] == 1):
							window.append(CUBOID([X[x],Y[y],Z[z]]))
							window.append(T(1)(X[x]))
						else:
							if (y == 1):
								window.append(T(2)(Y[y]/2 - glassW/2))
								window.append(COLOR(CYAN)(CUBOID([X[x],glassW,Z[z]])))
								window.append(T(2)(-Y[y]/2 + glassW/2))
							window.append(T(1)(X[x]))

					window.append(T([1,3])([-sum(X),Z[z]]))

				window.append(T([2,3])([Y[y],-sum(Z)]))
			
			#maniglia--------------------
			handle = STRUCT([T([1,2])([-0.01,-0.05]),CUBOID([0.1,0.02,0.02]),
							 T(2)(0.02),CUBOID([0.02,0.03,0.02])])
			handlePos =  [sum(X[:(len(X)/2)+1])-X[len(X)/2]/2, Y[0], sum(Z[:(len(Z)/2)+1])-Z[len(Z)/2]/2]
			handle = STRUCT([T([1,2,3])(handlePos),handle])
			
			window = STRUCT(window)
			window = STRUCT([COLOR([102./255.,51./255,0])(window),
							 COLOR([111./255,94./255.,62./255.])(handle)])
			scaleDim = [dx/SIZE(1)(window),dy/SIZE(2)(window),dz/SIZE(3)(window)]
			return STRUCT([S([1,2,3])(scaleDim),window])
		return window_builder


	def build_doors(frame, doorsFilePath): 
		
		#DATI PORTE
		X = [0.1,0.08,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.08,0.1]
		Z = [0.08,0.15,0.05,0.25,0.05,0.25,0.05,0.15,0.08,0.1]
		Y = [0.01,0.03,0.01]
		occupancy = [[[1,0,0,0,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,0,0,0,1]],
					[[1,0,0,0,0,0,0,0,0,0,1],[1,1,0,0,0,1,0,0,0,1,1],[1,0,0,0,0,0,0,0,0,0,1]], 
					[[1,0,0,0,0,0,0,0,0,0,1],[1,1,0,1,1,1,1,1,0,1,1],[1,0,0,0,0,0,0,0,0,0,1]], 
					[[1,0,0,0,0,0,0,0,0,0,1],[1,1,0,1,0,0,0,1,0,1,1],[1,0,0,0,0,0,0,0,0,0,1]],
					[[1,0,0,0,0,0,0,0,0,0,1],[1,1,1,1,0,0,0,1,1,1,1],[1,0,0,0,0,0,0,0,0,0,1]],
					[[1,0,0,0,0,0,0,0,0,0,1],[1,1,0,1,0,0,0,1,0,1,1],[1,0,0,0,0,0,0,0,0,0,1]],
					[[1,0,0,0,0,0,0,0,0,0,1],[1,1,0,1,1,1,1,1,0,1,1],[1,0,0,0,0,0,0,0,0,0,1]], 
					[[1,0,0,0,0,0,0,0,0,0,1],[1,1,0,0,0,1,0,0,0,1,1],[1,0,0,0,0,0,0,0,0,0,1]], 
					[[1,0,0,0,0,0,0,0,0,0,1],[1,1,1,1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,0,0,0,1]],
					[[1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1]]] 

		doorsList = []
		
		#scale factors
		x = 20/SIZE([1])(frame)[0]
		y = 16/SIZE([2])(frame)[0]
		z = 4/SIZE([3])(frame)[0]
		
		file = open(doorsFilePath, 'rt')
		lines = [] #[[x1,y1,x2,y2],[...]]
		try:
			reader = csv.reader(file)
			for row in reader:
				line = []
				for n in row:
					line.append(float(n))
				lines.append(line)
		finally:
			file.close()
			
		nDoors = len(lines)/4 #numero di porte
		
		#per ogni porta calcolo dimensione e posizione
		for i in range(nDoors):
			doorPol = []
			for line in lines[:4]:
				doorPol.append(POLYLINE([[line[0],line[1]],[line[2],line[3]]]))
			lines = lines[4:]
			door = STRUCT(doorPol)
			door = PROD([SOLIDIFY(door), Q(30)])
			frameWithHole = DIFFERENCE([frame, door])
			door = DIFFERENCE([frame, frameWithHole])
			door = S([1,2,3])([x,y,z])(door)
			bx,by,bz = SIZE([1,2,3])(door)
			if (bx<by):
				px,py,pz = get_positionXYZ(door)
				door = R([1,2])(PI/2)(ggpl_door(X,Y,Z,occupancy)(by,bx,bz))
				door = T([1,2,3])([px+bx,py,pz])(door)
			else:
				door = T([1,2,3])(get_positionXYZ(door))(ggpl_door(X,Y,Z,occupancy)(bx,by,bz))
			
			doorsList.append(door)
		
		doors = STRUCT(doorsList)
		return doors

	#funzione del workshop_07 relativa alle porte ----------------------------------------------

	def ggpl_door(X,Y,Z, occupancy):
		
		def door_builder(dx,dy,dz):

			thinW = 0.006 #spessore delle parti piu sottili della porta
			door = []
			#costruisco la porta in base all'array di booleani occupancy
			for y in range(0,len(Y)):

				for z in range(0,len(Z)):

					for x in range(0,len(X)):

						if (occupancy[z][y][x] == 1):
							door.append(CUBOID([X[x],Y[y],Z[z]]))
							door.append(T(1)(X[x]))
						else:
							if (y == 1):
								door.append(T(2)(Y[y]/2 - thinW/2))
								door.append(COLOR([188./255,159./255.,100./255.])
											(CUBOID([X[x],thinW,Z[z]])))
								door.append(T(2)(-Y[y]/2 + thinW/2))
							door.append(T(1)(X[x]))

					door.append(T([1,3])([-sum(X),Z[z]]))

				door.append(T([2,3])([Y[y],-sum(Z)]))
			
			#maniglia----------------
			handle = STRUCT([T([1,2])([-0.01,-0.05]),CUBOID([0.1,0.02,0.02]),
							 T(2)(0.02),CUBOID([0.02,0.03,0.02])])
			handlePos =  [sum(X[:2])-X[1]/2, Y[0], sum(Z[:5])-Z[4]/2]
			handle = STRUCT([T([1,2,3])(handlePos),handle])
			
			door = STRUCT(door)
			door = STRUCT([COLOR([102./255.,51./255,0])(door),
						   COLOR([128./255.,0,0])(handle)])
			scaleDim = [dx/SIZE(1)(door),dy/SIZE(2)(door),dz/SIZE(3)(door)]
			return STRUCT([S([1,2,3])(scaleDim),door])
		return door_builder



	# #### Creazione delle scale interne tramite utilizzo del workshop_03
	# Utilizzo della funzione ausiliaria citata in precedenza:
	# * build_stairs()

	def build_stairs(wallsFilePath,stairFilePath):
		
		def get_lines_from_csv(filePath):
			lines = [] #[[x1,y1,x2,y2],[...]]

			file = open(filePath,'rt')
			try:
				reader = csv.reader(file)
				for row in reader:
					line = []
					for n in row:
						line.append(float(n))
					lines.append(line)
			finally:
				file.close()

			polyline = []

			for line in lines:
				polyline.append(POLYLINE([[line[0],line[1]],[line[2],line[3]]]))

			return STRUCT(polyline) 
		
		#frame -----------------------
		extWalls = get_lines_from_csv(wallsFilePath)
		extWalls = PROD([OFFSET([4,4])(extWalls), Q(40)])
		frame = STRUCT([extWalls])
		fx,fy,fz = get_positionXYZ(frame)
		
		#SCALE FACTORS
		x = 20/SIZE([1])(frame)[0]
		y = 16/SIZE([2])(frame)[0]
		z = 4/SIZE([3])(frame)[0]
		
		#stairs -----------------------
		stair = get_lines_from_csv(stairFilePath)
		stair = SOLIDIFY(stair)
		stair = PROD([stair, Q(40)])
		stair = S([1,2,3])([x,y,z])(stair)
		
		#DIMENSIONI
		dx,dy,dz = SIZE([1,2,3])(stair)
		px,py,pz = get_positionXYZ(stair)
		stair = R([1,2])(-PI/2)(ggpl_suspended_straight_stairs(dy,dx,dz))
		
		return STRUCT([T([1,2,3])([fx+px,py+dy,pz])(stair)])

#funzione del workshop_03 relativa alle scale ----------------------------------------------
	def ggpl_suspended_straight_stairs(dx,dy,dz):
		
		#AUX
		def suspended_straight_stair(sx,sy,sz,nsteps):
			
			step = DIFFERENCE([CUBOID([sx,sy,sz]),CUBOID([sx,sy,sz/2])]) 
			#figura geometrica che identifica il singolo gradino

			#supporto centrale
			support = PROD([QUOTE([sx/3]), 
							MKPOL([[[0,0],[sy,sz],[sy/2,sz],[0,sz/2]],[[1,2,3,4]],1])]) 
			support = STRUCT([T([1,3])([sx/2-sx/6,-sz/2]), support]) 
			
			stepTranslationList = [step]
			#per il primo supporto elemento taglio la parte che sporge su -z
			supportTranslationList = [DIFFERENCE([support,CUBOID([sx,sx,-sx])])]

			#tot traslazioni per ogni gradino da aggiungere per tutti gli elementi
			for i in range(nsteps-1): 
				translation = [T([2,3])([sy, sz])]
				stepTranslationList = stepTranslationList + translation + [step]
				supportTranslationList = supportTranslationList + translation + [support]
			
			
			return STRUCT([STRUCT(stepTranslationList),
						   COLOR(RED)(STRUCT(supportTranslationList))])

			#END AUX ------------------------------------------------------------------------------- 
		
		box = [dx,dy,dz] #coordinate box 
		
		sx = dx #lunghezza dei gradini

		#blondel
		a = (.63*dz)/(2*dz+dy)
		p = (.63*dy)/(2*dz+dy)
		nsteps = int(dz/a) #numero dei gradini
		sy = float(dy)/float(nsteps) 
		sz = float(dz)/float(nsteps) #altezza dei gradini
		
		stairs = suspended_straight_stair(sx,sy,sz,nsteps)

		return STRUCT([stairs])


	# #### Creazione del tetto tramite utilizzo del workshop_09
	# Utilizzo della funzione ausiliaria citata in precedenza:
	# * build_roof()

	def build_roof(perimeterPath):
		
		lines = []
		file = open(perimeterPath,'rt')
		try:
			reader = csv.reader(file)
			for row in reader:
				line = []
				for n in row:
					line.append(float(n))
				lines.append(line)
		finally:
			file.close()

		V = []
		F = [[1,2,3,4]]
		polyline = []

		for line in lines:
			V.append([line[0],line[1],0])
		   
		roof =  ggpl_create_roof(V,F,50,PI/4)
		x = 20/SIZE([1])(roof)[0]
		y = 16/SIZE([2])(roof)[0]
		z = 4/SIZE([3])(roof)[0]
		roof = S([1,2,3])([x,y,z])(roof)
		
		return roof



	#funzione del workshop_09 relativa alla creazione del tetto -------------------------------

	def ggpl_create_roof(V,F,z,rad):
		
		#AUX ------------------------------------------------------
		
		def create_segments_faces(V):

			lines = []
			for i in range(len(V)-1):
				lines.append([i+1,i+2])
			lines.append([len(V),1])
			return lines
		
		def line_from_two_points(A,B):
			x1,y1,z1 = A
			x2,y2,z2 = B

			a = y1 - y2
			b = x2 - x1
			c = x1*y2 - x2*y1

			return [a,b,-c]
		
		def line_line_intersection(r1, r2):
			D  = r1[0] * r2[1] - r1[1] * r2[0]
			Dx = r1[2] * r2[1] - r1[1] * r2[2]
			Dy = r1[0] * r2[2] - r1[2] * r2[0]

			if D!=0:
				x = Dx/D
				y = Dy/D
				return [x,y]
			else:
				return False
		
		def get_plane_pitch(A,B,z):
			x1,y1,z1 = A
			x2,y2,z2 = B

			angle = ATAN2([(y1-y2),(x2-x1)])

			A1 = [x1+COS(angle)*z,y1+SIN(angle)*z,z1]
			B2 = [x2+COS(angle)*z,y2+SIN(angle)*z,z2]

			planePitch = STRUCT([MKPOL([[A,B,A1,B2],[[1,2,3,4]],None])])
			return planePitch
		
		def get_sloping_pitch(A,B,z,rad):
			x1,y1,z1 = A
			x2,y2,z2 = B

			planePitch = get_plane_pitch(A,B,z) 
			angle = ATAN2([(x2-x1),(y1-y2)])
			#print angle*180/PI

			originPitch = T([1,2])([-A[0], -A[1]])(planePitch)
			originPitch = R([1,2])(angle)(originPitch)
			rotation = R([2,3])(rad)(originPitch)
			originPitch = R([1,2])(-angle)(rotation)

			slopingPitch = T([1,2])([A[0],A[1]])(originPitch)
			return slopingPitch
		
		def create_pitch(V, interPoints):
			VTemp = V + [V[0]] + interPoints + [interPoints[0]]
			pitches = []
			for i in range(len(V)):
				points = [VTemp[i],VTemp[i+1],VTemp[i+1+len(V)],VTemp[i+2+len(V)]]
				pitch = STRUCT([MKPOL([points,[[1,2,3,4]],None])])
				pitches.append(pitch)
			return TEXTURE(['./textures/roof_texture.jpg',True, False, 1, 1, PI/2., 5,5])(STRUCT(pitches))

		#END AUX---------------------------------------------------
		
		segments = create_segments_faces(V)
		pitches = []
		for i in segments:
			A = V[i[0]-1]
			B = V[i[1]-1]
			slopingPitch = get_sloping_pitch(A,B,z,rad)
			pitches.append(slopingPitch)

		lines = []
		for i in range(len(pitches)):
			#troviamo i punti di ogni falda: quelli con z != 0 
			#son quelli per cui vado a calcolare la retta per due punti
			pol1 = UKPOL(pitches[i])[0]
			points = []
			for j in range(len(pol1)):
				if (round(pol1[j][2],3) != 0.0) :
					h = pol1[j][2]
					points.append([round(k,3) for k in pol1[j]])
			lines.append(line_from_two_points(points[0],points[1]))

		interPoint = line_line_intersection(lines[len(lines)-1], lines[0]) + [h]
		interPoints = [[round(k,3) for k in interPoint]]
		for i in range(len(lines)-1):
			interPoint = line_line_intersection(lines[i], lines[i+1]) + [h]
			interPoints.append([round(k,3) for k in interPoint])

		platform = TEXTURE(['./textures/roof_texture.jpg',True, False, 1, 1, PI/2., 5,5])(STRUCT([MKPOL([interPoints,F,1])]))
	   
		#nel caso in cui non avessi a disposizione le faces del poligono:
		#
		#polyline = []
		#V2d = []
		#for point in V:
		#    V2d.append([point[0],point[1]])
		#platform = SOLIDIFY(STRUCT([POLYLINE(V2d)]))
		
		pitches = create_pitch(V,interPoints)

		return STRUCT([platform, pitches])
		
	###
	# ----------- FINE FUNZIONI AUSILIARIE --------------------------
	###
    
    #PIANO TERRA
	structureGround = ggpl_create_house(folderPath + "terra/")
	px,py,pz = get_positionXYZ(structureGround)
	#PRIMO PIANO
	structure1stFloor = ggpl_create_house(folderPath + "piano1/")
    #SCALE
	stair = build_stairs(folderPath + 'terra/muriEsterni.lines',folderPath + 'terra/scale.lines')
    #TETTO
	roof = build_roof(folderPath + 'terra/muriEsterni.lines')
	rx,ry,rz = get_positionXYZ(roof)

	return STRUCT([structureGround,stair,T(3)(4)(structure1stFloor),T([1,2,3])([px-rx,py-ry,8])(roof)])



#VIEW(ggpl_multistore_house("./casa/lines/"))






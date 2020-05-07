'''
Characteristics:
For a nodule > 3 mm, each reader is asked to subjectively assess the nodule's characteristics as described on LIDC CDE page http://cdebrowser.nci.nih.gov/CDEBrowser/ and as follows:
	
1. Subtlety
Radiologist assessment of nodule subtlety on 1-5 scale 
(1  extremely subtle
2 
3 
4   
5   obvious)

2. InternalStructure
Radiologist assessment of nodule internal structure 
(1  soft tissue, 
2 fluid,
3 fat, 
4 air)

3. Calcification
Radiologist assessment of internal calcification of nodule
(1    Popcorn       Popcorn Appearance
2   Laminated     Laminated Appearance
3   Solid     Solid Appearance
4   Non-Central   Non-Central Appearance
5   Central     Central Calcification
6   Absent)

4. Sphericity
Radiologist assessment of shape of nodule in terms of its roundness/sphericity with only 3 terms defined:
(1    Linear        Linear Appearance
2
3   Ovoid     Ovoid Appearance
4
5   Round         Round Appearance)      


5. Margin
Radiologist assessment of nodule margin on a 1-5 scale with only the extreme values explicitly defined:
(1    Poorly Defined    Poorly Defined
5   Sharp     Sharp Margin)

6. Lobulation
Radiologist assessment of nodule lobulation on a 1-5 scale with only the extreme values explicitly defined:
(1    No Lobulation       No Lobulation
5   Marked      Marked Lobulation)

7. Spiculation
Radiologist assessment of nodule spiculation on a 1-5 scale with only the extreme values explicitly defined:
(1    No Spiculation        No Spiculation
5   Marked      Marked Spiculation)

8. Texture
Radiologist assessment of nodule internal texture with only 3 terms defined:
(1    Non-Solid/Ground Glass Opacity
2
3   Part Solid/Mixed
4
5   Solid Texture)

9. Malignancy
Radiologist subjective assessment of likelihood of malignancy of this nodule (ASSUMING 60-year-old male smoker )
(1    Highly Unlikely for Cancer
2   Moderately Unlikely for Cancer
3   Indeterminate Likelihood
4   Moderately Suspicious for Cancer
5   Highly Suspicious for Cancer)
'''



def generate_explanation(cancerous,noncancerous,prediction_list):
	characteristics_desc = {
"subtlety":["is extremely subtle","","","","is obviously subtle"],
"internalStructure":["has soft tissue","has fluid tissue","has fatty tissue","has airy tissue"],
"calcification":["has popcorn appearance","has laminated appearance","has solid appearance","has non-central appearance","has central calcification","has no calcification"],
"sphericity":["has linear appearance","","has ovoid appearance","","has round appearance"],
"margin":["has poorly defined margin","","","","has a sharp margin"],
"lobulation":["has no lobulation","","","","has marked lobulation"],
"spiculation":["has no spiculation","","","","has marked spiculation"],
"texture":["has non-solid texture/ground glass opacity","","has part solid/mixed texture","","has solid texture"],
"malignancy":["highly unlikely for cancer","moderately unlikely for cancer","of indeterminate likelihood for cancer","moderately suspicious for cancer","highly suspicious for cancer"]
}

	characteristics_set = ["subtlety","internalStructure","calcification","sphericity","margin","lobulation","spiculation","texture","malignancy"]

	characteristics_eq = []
	for elem in prediction_list:
		words = elem[0].split(" ")
		if(len(words)==3):
			elem_characteristic = words[0]
			elem_value = int(float(words[2])) -1
			if(words[1] == "<=") : 
				while(characteristics_desc[elem_characteristic][elem_value]==""):
					elem_value = elem_value-1
				elem_descriptor = characteristics_desc[elem_characteristic][elem_value]
			elif(words[1] == ">") :
				while(characteristics_desc[elem_characteristic][elem_value]==""):
					elem_value = elem_value+1
				elem_descriptor = characteristics_desc[elem_characteristic][elem_value]

		elif(len(words)==5):
			elem_characteristic = words[2]
			elem_min_value = int(float(words[0])) -1 
			elem_max_value = int(float(words[4])) -1
			while(characteristics_desc[elem_characteristic][elem_min_value]=="" and elem_max_value>=elem_min_value):
				elem_min_value = elem_min_value+1
			elem_descriptor = characteristics_desc[elem_characteristic][elem_min_value]

		characteristics_eq.append((elem_characteristic,elem_descriptor,elem[1]))

	if(cancerous>0.8):
		malignancy_descriptor = characteristics_desc['malignancy'][4]
		explanation = "The nodule is " + malignancy_descriptor + " because it "
		cancerous_explanation = ""
		noncancerous_explanation = ""

		c=0
		
		for ch in characteristics_eq:
			if ch[2] > 0 and c<2:
				if c==0: cancerous_explanation = ch[1]
				elif c>0: cancerous_explanation = cancerous_explanation + " and " + ch[1]
				c=c+1

		explanation = explanation + cancerous_explanation + "."

	elif(0.6<cancerous<=0.8):
		malignancy_descriptor = characteristics_desc['malignancy'][3]
		explanation = "The nodule is " + malignancy_descriptor + " because it "
		cancerous_explanation = ""
		noncancerous_explanation = ""

		c=0
		nc=0
		for ch in characteristics_eq:
			if ch[2] > 0 and c<2:
				if c==0: cancerous_explanation = ch[1]
				elif c>0: cancerous_explanation = cancerous_explanation + " and " + ch[1]
				c=c+1

			elif ch[2] < 0 and nc<1:
				noncancerous_explanation = ch[1]
				nc = nc + 1

		explanation = explanation + cancerous_explanation + ". But, it is not " + characteristics_desc['malignancy'][4] + " because it "+ noncancerous_explanation + ", which classifies it for being non-cancerous."

	elif(0.4<cancerous<=0.6):
		malignancy_descriptor = characteristics_desc['malignancy'][2]
		explanation = "The nodule is " + malignancy_descriptor + " because it "
		cancerous_explanation = ""
		noncancerous_explanation = ""

		c=0
		nc=0
		for ch in characteristics_eq:
			if ch[2] > 0 and c<2:
				if c==0: cancerous_explanation = ch[1]
				elif c>0: cancerous_explanation = cancerous_explanation + " and " + ch[1]
				c=c+1

			elif ch[2] < 0 and nc<2:
				if nc==0: noncancerous_explanation = ch[1]
				elif nc>0: noncancerous_explanation = noncancerous_explanation + " and " + ch[1]
				nc=nc+1

		explanation = explanation + cancerous_explanation + ", which are factors that classifies it for being cancerous. But, it " + noncancerous_explanation + ", which classifies it for being non-cancerous."

	elif(0.2<cancerous<=0.4):
		malignancy_descriptor = characteristics_desc['malignancy'][1]
		explanation = "The nodule is " + malignancy_descriptor + " because it "
		cancerous_explanation = ""
		noncancerous_explanation = ""

		c=0
		nc=0
		for ch in characteristics_eq:
			if ch[2] > 0 and c<1:
				if c==0: cancerous_explanation = ch[1]
				c=c+1

			elif ch[2] < 0 and nc<2:
				if nc==0: noncancerous_explanation = ch[1]
				elif nc>0: noncancerous_explanation = noncancerous_explanation + " and " + ch[1]
				nc=nc+1

		explanation = explanation + noncancerous_explanation +  ". But, it is not " + characteristics_desc['malignancy'][0] +  " because it " +  cancerous_explanation + ", which classifies it for being cancerous."
	elif(0<=cancerous<=0.2):
		malignancy_descriptor = characteristics_desc['malignancy'][0]
		explanation = "The nodule is " + malignancy_descriptor + " because it "
		cancerous_explanation = ""
		noncancerous_explanation = ""

		nc=0
		for ch in characteristics_eq:
			if ch[2] < 0 and nc<2:
				if nc==0: noncancerous_explanation = ch[1]
				elif nc>0: noncancerous_explanation = noncancerous_explanation + " and " + ch[1]
				nc=nc+1
		explanation = explanation + noncancerous_explanation + "."
	return (explanation)

if __name__ == "__main__":
	cancerous = 1.00
	noncancerous = 0.00
	prediction_list = [('4.00 < texture <= 5.00', -0.18548802296929512),
	 ('margin <= 3.00', 0.09219321448974335),
	 ('4.00 < subtlety <= 5.00', 0.0786872595866838),
	 ('spiculation > 2.00', 0.0639965135917401),
	 ('sphericity <= 3.00', -0.02603242840626896),
	 ('1.00 < lobulation <= 2.00', 0.024947764992764243),
	 ('internalStructure <= 1.00', -0.0110531873465778),
	 ('calcification <= 6.00', 0.0)]

	print(generate_explanation(cancerous,noncancerous,prediction_list))


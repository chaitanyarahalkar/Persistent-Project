from django.shortcuts import render
from app.models import Nodule, Case
import base64
import urllib
import csv
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
# showid = 3 # from 0 to 4

# srslst = ['1.3.6.1.4.1.14519.5.2.1.6279.6001.208737629504245244513001631764',\
# 		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.108231420525711026834210228428',\
# 		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.161002239822118346732951898613',\
# 		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.162901839201654862079549658100',\
# 		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.179162671133894061547290922949']
# Create your views here.


def iou(box0, box1):

	r0 = box0[3] / 2
	s0 = box0[:3] - r0
	e0 = box0[:3] + r0
	r1 = box1[3] / 2
	s1 = box1[:3] - r1
	e1 = box1[:3] + r1

	overlap = []
	for i in range(len(s0)): 
		overlap.append(max(0, min(e0[i], e1[i]) - max(s0[i], s1[i])))

	intersection = overlap[0] * overlap[1] * overlap[2]
	union = box0[3] * box0[3] * box0[3] + box1[3] * box1[3] * box1[3] - intersection
	return intersection / union
	
def nms(output, nms_th):

	if len(output) == 0: return output
	output = output[np.argsort(-output[:, 0])]
	bboxes = [output[0]]

	for i in np.arange(1, len(output)):
		bbox = output[i]
		flag = 1
		for j in range(len(bboxes)):
			if iou(bbox[1:5], bboxes[j][1:5]) >= nms_th:
				flag = -1
				break
		if flag == 1: bboxes.append(bbox)
	bboxes = np.asarray(bboxes, np.float32)

	return bboxes


def index(request,id = 0):

	patient_case = Case.objects.get(case_id = 1)
	nodules = Nodule.objects.filter(case = patient_case)
	string = base64.b64encode(nodules[id].fig.read())
	img  = urllib.parse.quote(string)

	return render(request, 'app/index.html', {'nodules': nodules,'info': nodules[id], 'img':img})


def open(request):
	return render(request, 'app/open.html')


def add_case(request):
	if request.method == 'POST':

		patient_id = request.POST.get(id)
		case = Case(patient_id = patient_id)
		case.save()

		pbb = np.load('./detection/'+ patient_id +'_pbb.npy')
		lbb = np.load('./detection/'+ patient_id +'_lbb.npy')
		pbb = np.array(pbb[pbb[:,0] > -2])
		pbb = nms(pbb, 0.1)

		with open('annotations.csv', newline='') as csvfile:
			reader = csv.DictReader(csvfile)


		for idx in range(pbb.shape[0]):

			z, x, y = int(pbb[idx,1]), int(pbb[idx,2]), int(pbb[idx,3])
			nodule = Nodule()
			nodule.case = case
			nodule.x = x
			nodule.y = y
			nodule.z = z
			
			dat0 = np.array(ctdat[0, z, :, :])
			dat0[max(0,x-10):min(dat0.shape[0],x+10), max(0,y-10)] = 255
			dat0[max(0,x-10):min(dat0.shape[0],x+10), min(dat0.shape[1],y+10)] = 255
			dat0[max(0,x-10), max(0,y-10):min(dat0.shape[1],y+10)] = 255
			dat0[min(dat0.shape[0],x+10), max(0,y-10):min(dat0.shape[1],y+10)] = 255


			plt.figure(figsize=(30,30))
			path = f'Uploads/{case.id}-{idx}.png'

			plt.savefig(path)
			nodule.fig = path

			nodule.diameter = 
			nodule.probability = 
			nodule.slice_index = z
			nodule.score = 
			





# def annotate(request):
# 	ctdat = np.load('CT/'+srslst[showid]+'_clean.npy', allow_pickle=True)
# 	ctlab = np.load('CT/'+srslst[showid]+'_label.npy', allow_pickle=True)
# 	idx = 0
# 	images = list()
# 	no_nodules = len(ctlab.shape[0])
# 	for idx in range(ctlab.shape[0]):
# 		if abs(ctlab[idx,0])+abs(ctlab[idx,1])+ abs(ctlab[idx,2])+abs(ctlab[idx,3]) == 0:
# 			continue

# 		plt.figure(figsize=(30,30))
# 		z, x, y = int(ctlab[idx,0]), int(ctlab[idx,1]), int(ctlab[idx,2])
# 		dat0 = np.array(ctdat[0, z, :, :])
# 		dat0[max(0,x-10):min(dat0.shape[0],x+10), max(0,y-10)] = 255
# 		dat0[max(0,x-10):min(dat0.shape[0],x+10), min(dat0.shape[1],y+10)] = 255
# 		dat0[max(0,x-10), max(0,y-10):min(dat0.shape[1],y+10)] = 255
# 		dat0[min(dat0.shape[0],x+10), max(0,y-10):min(dat0.shape[1],y+10)] = 255

# 		buf = io.BytesIO()
# 		plt.imsave(buf, dat0, cmap='gray')

# 		buf.seek(0)
# 		string = base64.b64encode(buf.read())
# 		data = urllib.parse.quote(string)
# 		images.append(data)

# 	return render(request, 'app/annotate.html', {'images': images})
from django.shortcuts import render, redirect
from django.http import HttpResponse
from app.models import Nodule, Case
import base64
import urllib
import csv
import os
import numpy as np
from explanation import generate_explanation
import lime
import lime.lime_tabular
from sklearn.model_selection import train_test_split
import xgboost
import dill as pickle

# showid = 3 # from 0 to 4

available_cases = ['1.3.6.1.4.1.14519.5.2.1.6279.6001.208737629504245244513001631764',\
		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.108231420525711026834210228428',\
		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.161002239822118346732951898613',\
		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.162901839201654862079549658100',\
		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.179162671133894061547290922949']

	
feature_names = ['subtlety','internalStructure','calcification','sphericity','margin','lobulation','spiculation','texture']
target_names = ['Non-Cancerous','Cancerous']

gbtree = pickle.load(open("xgboost-trainer.bin", "rb"))
predict_fn = lambda x: gbtree.predict_proba(x).astype(float)
data =  np.loadtxt(fname = 'data-1.csv', delimiter = ',')
X = data[:,0:8]
Y = data[:,8]
train, test, labels_train, labels_test = train_test_split(X,Y,train_size=0.70,random_state=42)
explainer = lime.lime_tabular.LimeTabularExplainer(train, feature_names=feature_names, class_names=target_names, discretize_continuous=True)


# Create your views here.


def iou(box0, box1):
	r0 = box0[3] / 2
	s0 = box0[:3] - r0
	e0 = box0[:3] + r0
	r1 = box1[3] / 2
	s1 = box1[:3] - r1
	e1 = box1[:3] + r1
	overlap = []
	for i in range(len(s0)): overlap.append(max(0, min(e0[i], e1[i]) - max(s0[i], s1[i])))
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

def portal(request,case_id,id = 0):

	global img,explanation,cancerous
	patient_case = Case.objects.get(case_id = case_id)
	nodules = Nodule.objects.filter(case = patient_case)

	if request.method == 'GET':
		
		string = base64.b64encode(nodules[id].fig.read())
		img  = urllib.parse.quote(string)

		test = np.array([nodules[id].subtlety, nodules[id].internal_structure, nodules[id].calcification,nodules[id].sphericity,nodules[id].margin,nodules[id].lobulation,nodules[id].spiculation,nodules[id].texture])
		exp = explainer.explain_instance(test,predict_fn, num_features=10000)
		non_cancerous = exp.predict_proba[0]
		cancerous = 1 - non_cancerous 
		# exp.show_in_notebook(show_table=True, show_all=False)
		try:
			data = exp.as_list()
		except Exception as e:
			data = exp.as_list(label = 0)

		explanation = generate_explanation(cancerous, non_cancerous, data)

	elif request.method == 'POST':

		nodule = nodules[id]
		if request.POST.get('mc'):
			nodule.concerning = True

		if request.POST.get('ds'):
			nodule.concerning = False

		if request.POST.get('position'):
			nodule.position = request.POST.get('position')

		if request.POST.get('state'):
			nodule.state = request.POST.get('state')

		if request.POST.get('size'):
			nodule.size = request.POST.get('size')

		if request.POST.get('notes'):
			nodule.notes = request.POST.get('notes')

		nodule.save()


	return render(request, 'app/portal.html', {'nodules': enumerate(nodules),'info': nodules[id], 'img':img, 'case_id': case_id, 'explanation': explanation, 'probability': '{:.2f}'.format(cancerous) })


def open_case(request):

	registered_cases = Case.objects.all()
	
	return render(request, 'app/open.html', {'cases': available_cases, 'registered_cases': registered_cases})


def process(request):
	if request.method == 'POST':

		patient_id = request.POST.get("case")
		case_id = available_cases.index(patient_id)
		case,created = Case.objects.get_or_create(patient_id = patient_id, case_id = case_id)

		pbb = np.load('./detection/'+ patient_id +'_pbb.npy',allow_pickle = True)
		lbb = np.load('./detection/'+ patient_id +'_lbb.npy',allow_pickle = True)
		count = np.load('./CT/'+ patient_id +'_label.npy',allow_pickle = True).shape[0]


		pbb = np.array(pbb[pbb[:,0] > -2])
		pbb = nms(pbb, 0.1)	

		lines = list()

		cf = open('data.csv')
		reader = csv.DictReader(cf)
		for line in reader:
			if line['SeriesUid'] == patient_id:
				lines.append(line)

		cf.close()

		for idx,line in enumerate(lines):

			dia = line['Diameter_mm']
			sub = line['Subtlety']
			ins = line['InternalStructure']
			cal = line['Calcification']
			sph = line['Sphericity']
			mar = line['Margin']
			lob = line['Lobulation']
			spi = line['Spiculation']
			tex = line['Texture']
			mal = line['Malignancy']
			can = line['Cancerous']

			if int(can) >= 3:
				con = True
			else:
				con = False

			z, x, y = int(pbb[idx,1]), int(pbb[idx,2]), int(pbb[idx,3])
			path = f'Uploads/{case_id}/{case_id}-{idx}.png'
			nodule, created = Nodule.objects.get_or_create(subtlety = sub, internal_structure = ins, calcification = cal, sphericity = sph, margin = mar, lobulation = lob, spiculation = spi, texture = tex, concerning = con, x = x, y = y, z = z, case = case, fig = path, slice_index = z, score = mal, diameter = dia, probability = 0)
				
		return redirect(f'/portal/{case_id}/0/')

	return HttpResponse('Get not allowed!')

			
# <<<<<<< Updated upstream
# # def submit(request):
# # 	if request.method == 'POST':
# # 		id = request.POST.get('id')
		
# # 		nodule = Nodule.objects.get(id = id)
# # 		ll = request.POST.get('leftlung')
# # 		rl = request.POST.get('rightlung')
		
# =======
# >>>>>>> Stashed changes





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
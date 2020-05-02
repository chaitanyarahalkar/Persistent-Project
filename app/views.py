from django.shortcuts import render

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import base64
import urllib
import io 
showid = 3 # from 0 to 4

srslst = ['1.3.6.1.4.1.14519.5.2.1.6279.6001.208737629504245244513001631764',\
		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.108231420525711026834210228428',\
		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.161002239822118346732951898613',\
		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.162901839201654862079549658100',\
		  '1.3.6.1.4.1.14519.5.2.1.6279.6001.179162671133894061547290922949']
# Create your views here.


def index(request):
	return render(request, 'app/index.html')


def open(request):
	return render(request, 'app/open.html')


def annotate(request):
	ctdat = np.load('CT/'+srslst[showid]+'_clean.npy', allow_pickle=True)
	ctlab = np.load('CT/'+srslst[showid]+'_label.npy', allow_pickle=True)
	idx = 0
	images = list()
	no_nodules = len(ctlab.shape[0])
	for idx in range(ctlab.shape[0]):
		if abs(ctlab[idx,0])+abs(ctlab[idx,1])+ abs(ctlab[idx,2])+abs(ctlab[idx,3]) == 0:
			continue

		plt.figure(figsize=(30,30))
		z, x, y = int(ctlab[idx,0]), int(ctlab[idx,1]), int(ctlab[idx,2])
		dat0 = np.array(ctdat[0, z, :, :])
		dat0[max(0,x-10):min(dat0.shape[0],x+10), max(0,y-10)] = 255
		dat0[max(0,x-10):min(dat0.shape[0],x+10), min(dat0.shape[1],y+10)] = 255
		dat0[max(0,x-10), max(0,y-10):min(dat0.shape[1],y+10)] = 255
		dat0[min(dat0.shape[0],x+10), max(0,y-10):min(dat0.shape[1],y+10)] = 255

		buf = io.BytesIO()
		plt.imsave(buf, dat0, cmap='gray')

		buf.seek(0)
		string = base64.b64encode(buf.read())
		data = urllib.parse.quote(string)
		images.append(data)

	return render(request, 'app/annotate.html', {'images': images})
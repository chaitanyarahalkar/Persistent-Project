import sys
import pylidc as pl



pid = 'LIDC-IDRI-0220'
scan = pl.query(pl.Scan).filter(pl.Scan.patient_id == pid).first()
nods = scan.cluster_annotations()
nod = nods[int(sys.argv[1])][0]
nod.visualize_in_scan()

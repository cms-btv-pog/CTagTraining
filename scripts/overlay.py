from rootpy.io import root_open
import rootpy.plotting as plt
from argparse import ArgumentParser
from pdb import set_trace

graph_path = "ROC_C_light_Inclusive"
file_names = [
   ('AllHistograms_RFC_sklearn.root', 'SKLearn training Seth'),
   ('plots/HopeSethEquivalent/AllHistograms.root', 'SKLearn training Mauro'),
]
output = 'overlay.png'

canvas = plt.Canvas()
canvas.SetLogy();
canvas.SetGridx();
canvas.SetGridy();

legend = plt.Legend(len(file_names))

tfiles = []
graphs = []
idx = 0
for name, legname in file_names:
   tfile = root_open(name)
   tfiles.append(
      tfile
      )
   graph = tfile.Get(graph_path)
   graph.linecolor = idx+2
   graph.linewidth = 2
   graph.title = legname
   graph.markerstyle = 0
   graph.legendstyle = 'l'
   legend.AddEntry(graph);
   graphs.append(
      graph
      )
   idx += 1


diag_x = [
   0.001,0.005,
   0.01, 0.015, 0.02, 0.04, 0.05, 0.07, 0.09,
   0.1, 0.15,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1];
diag = plt.Graph(len(diag_x))
diag.linecolor = 13
diag.linestyle = 2
#set_trace()
for i, x in enumerate(diag_x):
   diag.SetPoint(i, x, x)

graphs.append(diag)

graphs[0].Draw()
for i in graphs[1:]:
   i.Draw('same')

legend.Draw()
canvas.Update()

canvas.SaveAs(output)

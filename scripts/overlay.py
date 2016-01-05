from rootpy.io import root_open
import rootpy.plotting as plt
from argparse import ArgumentParser
from pdb import set_trace

graph_path = "ROC_C_light_Inclusive"
file_names = [
##  ('SethTrainings/AllHistograms_TMVA.root', 'TMVA'),
##  ('plots/Categories/ROCs.root', 'SKL categories, 1% 200 trees'),
##  ('plots/CategoriesEquivalent/AllHistograms.root', 'SKLearn 1% 2000 trees'),
##  ('plots/CTagEquivalent/AllHistograms.root', 'SKL RFC'),
##  ('plots/GBC10PcBetter/AllHistograms.root', 'SKL GBC'),
  ('CvsL_GBC_17Dec/ROCs/7aa4de24d8_ROCs.root', 'SKL GBC Optimized (500 Trees)'),
  ('CvsL_GBC_17Dec/ROCs/8640356720_ROCs.root', 'SKL GBC Optimized (1000 Trees)'),
  ('CvsL_GBC_17Dec/ROCs/32c9c99660_ROCs.root', 'SKL GBC Optimized (2000 Trees)'),
  ('CvsL_GBC_17Dec/ROCs/edce325587_ROCs.root', 'SKL GBC Optimized (3000 Trees)'),
##  ('plots/GBC_Optimized_Categories/ROCs.root', 'SKL GBC OPT, Categories'),
##  ('plots/CTagEquivalent/AllHistograms.root', 'SKLearn Mauro, new w, 10% 2000 trees'),
]
output = 'pngs/optimization_ntrees_roc.png'

canvas = plt.Canvas()
canvas.SetLogy();
canvas.SetGridx();
canvas.SetGridy();

max_txt_len = max(len(i) for _, i in file_names)
legend = plt.Legend(
   len(file_names), 
   leftmargin=0.23+(30-max_txt_len)*0.016,
   rightmargin=0.01, 
   topmargin=0.6-0.05*(len(file_names)-3), 
   entrysep=0, 
   margin=0.1+0.006*(30-max_txt_len)
)

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

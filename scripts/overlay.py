'''
simple overlay script for ROCs, should add var parsing. inputfiles and attached legend entry are defined in the file_names variable
'''
from rootpy.io import root_open
import rootpy.plotting as plt
from argparse import ArgumentParser
from pdb import set_trace
import prettyjson
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptTitle(0)

parser = ArgumentParser()
parser.add_argument('input', nargs='*', help='input json config')
args = parser.parse_args()

graph_path = "ROC_C_light_Inclusive"
file_names = [
#
# CvsL
#
   ('CvsL_76_17Jan/ROCs/5565121efc_ROCs.root', '7.6 Optimization'),
   ('test/ROCs.root', 'separate testing'),
#
# CvsB
#
# ('CvsB_76_18Jan/ROCs/82d2a6148a_ROCs.root', '7.5 Optimization'),
# ('CvsB_76_18Jan/ROCs/ff481cb37f_ROCs.root', '7.6 Optimization'),
]
output = 'test/test.png'

if args.input:
   jconf = prettyjson.loads(open(args.input[-1]).read())
   file_names = [tuple(i) for i in jconf['file_names']]
   output = jconf['output']
   graph_path = jconf['graph_path']

#dump configuration in json for bookkeeping
jconf = {
   'file_names' : file_names,
   'output' : output,
   'graph_path' : graph_path,
}

jout = output.split('.')[0]
with open('%s.json' % jout, 'w') as out:
   out.write(prettyjson.dumps(jconf))

canvas = plt.Canvas(800, 800)
canvas.SetLogy();
canvas.SetGridx();
canvas.SetGridy();

max_txt_len = max(len(i) for _, i in file_names)
legend = plt.Legend(
   len(file_names), 
   leftmargin=0.18+(30-max_txt_len)*0.016,
   rightmargin=0.005, 
   topmargin=0.60-0.057*(len(file_names)-3), 
   entrysep=0, 
   margin=0.1+0.006*(30-max_txt_len)
)
legend.SetTextSize(
   legend.GetTextSize()*0.8
)
legend.SetFillColor(0)
legend.SetFillStyle(1001)

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
   graph.yaxis.SetTitleOffset(
      graph.yaxis.GetTitleOffset()*1.4
      )
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

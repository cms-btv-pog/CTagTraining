from BasePlotter import BasePlotter
from rootpy.io import root_open
import rootpy.plotting.views as views
from ROOT import TProfile
import binning
from pdb import set_trace
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('in',  help='input root file')
parser.add_argument('out', help='output dir')
args = parser.parse_args()
      
tfile = root_open(args.in)
plotter = BasePlotter(
   args.out,
   defaults={'save':{'pdf' : False}},
   )
b_plots = views.StyleView(
   views.TitleView(views.SubdirectoryView(tfile, 'B'), 'B'),
   linewidth=2,
   linecolor='#2aa198',
   legendstyle='l',
   drawstyle='hist'
   )

c_plots = views.StyleView(
   views.TitleView(views.SubdirectoryView(tfile, 'C'), 'C'),
   linewidth=2,
   linecolor='#0055ff',
   legendstyle='l',
   drawstyle='hist',
   )

l_plots = views.StyleView(
   views.TitleView(views.SubdirectoryView(tfile, 'DUSG'), 'DUSG'),
   linewidth=2,
   linecolor='#ab5555',
   legendstyle='l',
   drawstyle='hist',
   )

to_plot = [
   ('ring_sum_5', 'tracker energy deposit ring [0,5]', True, 'SE'),
   ('ring_sum_4', 'tracker energy deposit ring [0,4]', True, 'SE'),
   ('ring_sum_6', 'tracker energy deposit ring [0,6]', True, 'SE'),
   ('ring_sum_1', 'tracker energy deposit ring [0,1]', True, 'SE'),
   ('ring_sum_3', 'tracker energy deposit ring [0,3]', True, 'SE'),
   ('ring_sum_2', 'tracker energy deposit ring [0,2]', True, 'SE'),
   ('ring7', 'tracker energy deposit ring 7', True, 'SW'), 
   ('ring6', 'tracker energy deposit ring 6', True, 'SW'), 
   ('ring5', 'tracker energy deposit ring 5', True, 'SW'), 
   ('ring4', 'tracker energy deposit ring 4', True, 'SW'), 
   ('ring3', 'tracker energy deposit ring 3', True, 'SW'), 
   ('ring2', 'tracker energy deposit ring 2', True, 'SW'), 
   ('ring1', 'tracker energy deposit ring 1', True, 'SW'), 
   ('ring0', 'tracker energy deposit ring 0', True, 'SW'), 
   ('ptD', 'p_{TD}', False, 'NW'), 
   ('ring_profile', 'Mean energy deposit in ring number', False, 'NE'),
   ]

vtx_plots = [
   ('svmass', 'SV Mass', False, 'NE'),
   ('svmass_corrected', 'Corrected SV Mass', False, 'NE')
]

sl_plots = [
   ('ratiolpt', 'p_{T}(SL)/p_{T}(jet)', False, 'NE')
]

def norm(histo):
   if not isinstance(histo, TProfile):
      if histo.Integral():
         histo.Scale(1./histo.Integral())
   return histo      

def draw(paths, title, logy, name):
   b_histo = norm(sum(b_plots.Get(i) for i in paths))
   l_histo = norm(sum(l_plots.Get(i) for i in paths))
   c_histo = norm(sum(c_plots.Get(i) for i in paths))
   plotter.overlay([c_histo, l_histo, b_histo], logy=logy, xtitle=title)
   plotter.add_legend([c_histo, l_histo, b_histo], leftside=False)
   plotter.add_watermark('CMS Simulation')
   plotter.save(name)
   
#paths = ['CombinedSV%s%s/ratiolpt' % (i, j) for i in binning.sv_categories for j in binning.lep_categories if 'NoSoftLepton' not in j]
#draw(paths, 'p_{T}(SL)/p_{T}(jet)', False, 'ratiolpt_nofilter')

for category in binning.sv_categories:
   plotter.set_subdir(category)
   plotted = to_plot[:]
   if 'RecoVertex' in category:
      plotted.extend(vtx_plots)
   for plot, title, logy, _ in plotted:
      draw(
         ['CombinedSV%s%s/%s' % (category, i, plot) for i in binning.lep_categories], 
         title, logy, plot
         )

for category in binning.sv_categories:
   plotted = to_plot[:]
   if 'RecoVertex' in category:
      plotted.extend(vtx_plots)
   for lepcat in binning.lep_categories:
      plotter.set_subdir('%s%s' % (category, lepcat))
      plotted = to_plot[:]
      if 'NoSoftLepton' not in lepcat:
         plotted.extend(sl_plots)
      for plot, title, logy, _ in plotted:
         draw(
            ['CombinedSV%s%s/%s' % (category, lepcat, plot) for i in binning.lep_categories], 
            title, logy, plot
            )

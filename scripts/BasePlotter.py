'''
Base plotter class, copied with reduced functionalitied from my analysis framework https://gitlab.cern.ch/mverzett/URAnalysis
Special thanks to Mario Galanti, who had most of these functions in C++
'''

import fnmatch
import re
import os
import rootpy.plotting.views as views
import rootpy.plotting as plotting
import rootpy.io as io
import prettyjson
import sys
from math import sqrt
from rootpy.plotting.hist import HistStack, Hist
from pdb import set_trace
import logging
import ROOT
import uuid
from itertools import izip_longest 

ROOT.gROOT.SetBatch(True)

def quad(*xs):
   '''Function to sum in quadrature'''
   return math.sqrt(sum(x*x for x in xs))

def get_best_style(sample, styles):
    best_pattern = ''
    for pattern, style_dict in styles.iteritems():
        log.debug("Checking pattern: %s against %s", pattern, sample)
        if fnmatch.fnmatch(sample, pattern):
            log.debug("-> it matches!")
            if len(pattern) > len(best_pattern):
                best_pattern = pattern
                log.info("Found new best style for %s: %s",
                         sample, pattern)
    if best_pattern:
        return styles[best_pattern]
    else:
        return None


_original_draw = plotting.Legend.Draw
# Make legends not have crappy border
def _monkey_patch_legend_draw(self, *args, **kwargs):
  ''' Make a plotting.legend look nice '''
  #self.SetBorderSize(0)
  _original_draw(self, *args, **kwargs)
plotting.Legend.Draw = _monkey_patch_legend_draw

class LegendDefinition(object):
  def __init__(self, title='', position='', entries=[], labels=[]):
    self.title_ = title
    self.position_ = position.lower()
    self.entries_ = entries
    self.labels_ = labels
    self.nentries_ = sum(
      len(i.hists) if isinstance(i, plotting.HistStack) else 1 
      for i in entries
      )
  
  @property
  def entries(self):
    return self.entries_
  
  @entries.setter
  def entries(self, entries):
    self.entries_ = entries
    self.nentries_ = sum(
      len(i.hists) if isinstance(i, plotting.HistStack) else 1 
      for i in entries
      )
    
  @property
  def title(self):
    return self.title_
  @title.setter
  def title(self, title):
    self.title_=title

  @property
  def labels(self):
    return self.labels_
  @labels.setter
  def labels(self, labels):
    self.labels_=labels

  @property
  def position(self):
    return self.position_
  @position.setter
  def position(self, position):
    self.position_=position.lower()

  @staticmethod
  def ndc_coordinates(position, nchars, nlines):
    pad = ROOT.gPad
    padLeftMargin = pad.GetLeftMargin()
    padRightMargin = pad.GetRightMargin()
    padTopMargin = pad.GetTopMargin()
    padBottomMargin = pad.GetBottomMargin()
    plotWidth = 1. - (padLeftMargin + padRightMargin)
    plotHeight = 1. - (padTopMargin + padBottomMargin)

    txt_width = nchars*0.023 #no reason for this factor other than "it works" 
    entry_height = 0.040
    txt_height = nlines*entry_height 

    if 'e' in position: 
      right = 0.98*plotWidth + padLeftMargin
      left  = right - txt_width
    elif 'w' in position:
      left  = 0.02*plotWidth + padLeftMargin
      right = left+txt_width
    else:
      left  = padLeftMargin + 0.5*plotWidth - 0.5*txt_width
      right = left+txt_width

    if 'n' in position:
      top = 0.98*plotHeight + padBottomMargin
      bottom = max(top-txt_height, 0)
    elif 's' in position:
      bottom = 0.02*plotHeight + padBottomMargin
      top = min(bottom+txt_height, 1)
    else:
      #FIXME todo
      bottom = padBottomMargin + plotHeight*0.5 - 0.5*txt_height
      top    = bottom + txt_height

    #print (position, nchars, nlines), (left, bottom, right, top)
    return left, bottom, right, top

  def make_legend(self):
    # Create the legend Set the legend position according to LegendDefinition::position variable
    maxTextSize = 0
    if len(self.title) > maxTextSize:
      maxTextSize = min(
        len(self.title),
        40
        )

    if not self.labels_ or any(i is None for i in self.labels_):
      for entry in self.entries:
        if isinstance(entry, plotting.HistStack):
          for sub in entry:
            maxTextSize = max(
              len(sub.title),
              maxTextSize
              )
        else:
          maxTextSize = max(
            len(entry.title),
            maxTextSize
            )
    else:
      maxTextSize = max(maxTextSize, max(len(i) for i in self.labels_))
      
    if len(self.title) > 0:
      self.nentries_ += 1
    
    legend = plotting.Legend(
      self.nentries_, entrysep=0., margin=0.35, textfont=42, entryheight=0.04, textsize=0.035,
      )
    legend.position = LegendDefinition.ndc_coordinates(self.position, maxTextSize, self.nentries_)
    if self.title:
      legend.SetHeader(self.title)

    if not self.labels_ or any(i is None for i in self.labels_):
      self.labels_ = [None for _ in self.entries]
    for entry, label in zip(self.entries, self.labels_):
      if label is None:
        legend.AddEntry(entry)
      else:
        legend.AddEntry(entry, label)

    # Set generic options
    legend.UseCurrentStyle()
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.SetFillStyle(0)
            
    return legend

    

class BasePlotter(object):
  def __init__(self, outputdir='./', defaults={}, styles={}):
    ''' Initialize the BasePlotter 

    outputdir is where histograms will be saved.
    
    defaults provides basic configuration of the plotter. Most of the options 
    can be anyway overridden by the specific command in case one exception
    to the general rule is needed. Available defaults:
      - clone : (bool, default True) chooses the clone policy. If true histograms
    will be cloned before being styled and drawn
      - show_title : (bool, default False) shows the histogram title in the canvas
      - name_canvas: (bool, default False) name the canvas after the histogram.name it is drawn inside
      - save: (dict, default {'png' : True, 'pdf' : True, 'dotc' : False, 
          'dotroot' : False, 'json' : False} set the formats to which save the canvas

    styles provides the plotter a look-up table of styles to be applied to the histograms in
    the form key : style. Key is a POSIX regular expression that is matched to the 
    histogram title.
    '''
    self.outputdir = outputdir
    self.base_out_dir = outputdir
    self.canvas = plotting.Canvas(800, 800, name='adsf', title='asdf')
    self.set_canvas_style(self.canvas)
    self.canvas.cd()
    self.pad    = plotting.Pad( 0., 0., 1., 1.) #ful-size pad 
    self.pad.Draw()
    self.set_canvas_style(self.pad)
    self.pad.cd()
    self.lower_pad = None
    self.keep = []
    self.defaults = defaults
    self.styles = styles
    self.label_factor = None
    BasePlotter.set_canvas_style(self.canvas)
    self.set_style()

  def set_subdir(self, folder=''):
    '''Sets the output to be written 
    in a particular subdir'''
    self.outputdir = '/'.join([self.base_out_dir, folder])
    if not os.path.isdir(self.outputdir):
      os.makedirs(self.outputdir)

  def set_style(self):
    # For the canvas:
    ROOT.gStyle.SetCanvasBorderMode(0)
    ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
    ROOT.gStyle.SetCanvasDefH(600) # Height of canvas
    ROOT.gStyle.SetCanvasDefW(600) # Width of canvas
    ROOT.gStyle.SetCanvasDefX(0) # Position on screen
    ROOT.gStyle.SetCanvasDefY(0)
    
    # For the Pad:
    ROOT.gStyle.SetPadBorderMode(0)
    ROOT.gStyle.SetPadColor(ROOT.kWhite)
    ROOT.gStyle.SetPadGridX(False)
    ROOT.gStyle.SetPadGridY(False)
    ROOT.gStyle.SetGridColor(0)
    ROOT.gStyle.SetGridStyle(3)
    ROOT.gStyle.SetGridWidth(1)
    
    # For the frame:
    ROOT.gStyle.SetFrameBorderMode(0)
    ROOT.gStyle.SetFrameBorderSize(1)
    ROOT.gStyle.SetFrameFillColor(0)
    ROOT.gStyle.SetFrameFillStyle(0)
    ROOT.gStyle.SetFrameLineColor(1)
    ROOT.gStyle.SetFrameLineStyle(1)
    ROOT.gStyle.SetFrameLineWidth(1)
    
    # For the histo:
    ROOT.gStyle.SetHistLineColor(1)
    ROOT.gStyle.SetHistLineStyle(0)
    ROOT.gStyle.SetHistLineWidth(1)    
    ROOT.gStyle.SetEndErrorSize(2)
    #ROOT.gStyle.SetErrorX(0.) 
    #removed since it messes up with E2 draw options (to draw stack unc)
    ROOT.gStyle.SetMarkerStyle(20)
    
    # For the fit/function:
    ROOT.gStyle.SetOptFit(1)
    ROOT.gStyle.SetFitFormat("5.4g")
    ROOT.gStyle.SetFuncColor(2)
    ROOT.gStyle.SetFuncStyle(1)
    ROOT.gStyle.SetFuncWidth(1)
    
    # For the date:
    ROOT.gStyle.SetOptDate(0);
    
    # For the statistics box:
    ROOT.gStyle.SetOptFile(0)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetStatColor(ROOT.kWhite)
    ROOT.gStyle.SetStatFont(42)
    ROOT.gStyle.SetStatFontSize(0.027)
    ROOT.gStyle.SetStatTextColor(1)
    ROOT.gStyle.SetStatFormat("6.4g")
    ROOT.gStyle.SetStatBorderSize(1)
    ROOT.gStyle.SetStatH(0.1)
    ROOT.gStyle.SetStatW(0.15)
    ROOT.gStyle.SetStatX(0.93)
    ROOT.gStyle.SetStatY(0.86)
    
    # Margins:
    ROOT.gStyle.SetPadTopMargin(0.1)
    ROOT.gStyle.SetPadBottomMargin(0.14)
    ROOT.gStyle.SetPadLeftMargin(0.18)
    ROOT.gStyle.SetPadRightMargin(0.035)
    
    # For the Global title:
    opt = int(self.defaults['show_title']) if 'show_title' in self.defaults else 0
    ROOT.gStyle.SetOptTitle(opt)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleColor(1)
    ROOT.gStyle.SetTitleTextColor(1)
    ROOT.gStyle.SetTitleFillColor(0)
    ROOT.gStyle.SetTitleFontSize(0.04)
    ROOT.gStyle.SetTitleX(0.55) # Set the position of the title box
    ROOT.gStyle.SetTitleY(0.95) # Set the position of the title box
    ROOT.gStyle.SetTitleAlign(22)
    ROOT.gStyle.SetTitleBorderSize(0)
    
    # For the axis titles:
    ROOT.gStyle.SetTitleColor(1, "XYZ")
    ROOT.gStyle.SetTitleFont(42, "XYZ")
    ROOT.gStyle.SetTitleSize(0.05, "XYZ")
    ROOT.gStyle.SetTitleXOffset(1.1)
    ROOT.gStyle.SetTitleYOffset(1.5)
    
    # For the axis labels:
    ROOT.gStyle.SetLabelColor(1, "XYZ")
    ROOT.gStyle.SetLabelFont(42, "XYZ")
    ROOT.gStyle.SetLabelOffset(0.007, "XYZ")
    ROOT.gStyle.SetLabelSize(0.04, "XYZ")
    
    # For the axis:
    ROOT.gStyle.SetAxisColor(1, "XYZ")
    ROOT.gStyle.SetStripDecimals(True)
    ROOT.gStyle.SetTickLength(0.03, "XYZ")
    ROOT.gStyle.SetNdivisions(505, "X")
    ROOT.gStyle.SetNdivisions(510, "YZ")
    ROOT.gStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
    ROOT.gStyle.SetPadTickY(1)
    
    # Default to no-log plots:
    ROOT.gStyle.SetOptLogx(0)
    ROOT.gStyle.SetOptLogy(0)
    ROOT.gStyle.SetOptLogz(0)
    
    # Postscript options:
    ROOT.gStyle.SetPaperSize(20.,20.)
    
    ROOT.gStyle.SetPalette(1)
    
    ROOT.gStyle.cd()
       
     
  @staticmethod
  def divide(passed, total, graph, method="bayes"):
    xTitle = graph.GetXaxis().GetTitle()
    yTitle = graph.GetYaxis().GetTitle()
    if method == "bayes":
      graph.BayesDivide(passed,total)
    elif method == "clopperpeason":
      graph.Divide(passed, total,"cp")
    graph.GetXaxis().SetTitle(xTitle)
    graph.GetYaxis().SetTitle(yTitle)
          
  @staticmethod
  def set_canvas_style(c, logscalex=False, logscaley=False, logscalez=False):
    c.UseCurrentStyle()
    if logscalex == True:
      c.SetLogx(1)
    else:
      c.SetLogx(0)
    if logscaley == True:
      c.SetLogy(1)
    else:
      c.SetLogy(0)
    if logscalez == True:
      c.SetLogz(1)
    else:
      c.SetLogz(0)
          
  @staticmethod
  def set_profile_style(p):
    p.UseCurrentStyle()
    p.SetMarkerStyle(3)
      
  @staticmethod
  def set_histo_style(histo, **kwargs):
    if not plotting.hist._Hist in type(histo).__bases__: #work around isinstance issue
      return
    if 'linewidth' not in kwargs:
      kwargs['linewidth'] = 2
    if 'name' in kwargs:
      kwargs['title'] = kwargs['name']
      del kwargs['name']
    histo.UseCurrentStyle()
    for key, val in kwargs.iteritems():
      if key == 'xtitle':
        histo.xaxis.title = val
      elif key =='ytitle':
        histo.yaxis.title = val
      else:        
        setattr(histo, key, val)
    histo.SetTitleFont(ROOT.gStyle.GetTitleFont())
    histo.SetTitleSize(ROOT.gStyle.GetTitleFontSize(), "")
    histo.SetStats(False)

  def style_histo(self, histo, **kwargs):
    '''non static histo styling, uses default styles, 
    can be overridden by keyword args'''
    style = histo.decorators
    if self.styles:
      bstyle = get_best_style(histo.title, self.styles)
      if bstyle:
        style.update(bstyle)
    style.update(kwargs)
    BasePlotter.set_histo_style(histo, **style)
    if self.label_factor is not None:
      label_size = ROOT.gStyle.GetTitleSize()*self.label_factor
      if isinstance(histo, plotting.HistStack):
        for i in histo.hists:
          i.SetLabelSize(label_size, "XYZ")
          i.SetTitleSize(label_size, "XYZ")
          i.yaxis.SetTitleOffset(i.yaxis.GetTitleOffset()/self.label_factor)
      else:
        histo.SetLabelSize(label_size, "XYZ")
        histo.SetTitleSize(label_size, "XYZ")
        histo.yaxis.SetTitleOffset(histo.yaxis.GetTitleOffset()/self.label_factor)
      
  @staticmethod
  def set_stack_histo_style(histo, color):
    BasePlotter.set_histo_style(
      histo, 
      fillcolor=color,
      linecolor=1,
      linewidth=1
      )
  
  @staticmethod
  def set_graph_style(graph, markerstyle, linecolor):
    graph.UseCurrentStyle()
    if markerstyle != 0:
      graph.SetMarkerStyle(markerstyle)
    graph.SetMarkerColor(linecolor)
    graph.SetLineColor(linecolor)
  
  @staticmethod
  def _kwargs_to_styles_(kwargs, nhists):
    '''translates keyword arguments dict containing multiple styles
    into a list of styles. kwargs with list values are unpacked,
    kwargs with single value are used throughout'''
    styles = [{} for _ in range(nhists)]
    for key, value in kwargs.iteritems():
      if isinstance(value, list):
        for style, item in zip(styles, value):
          style[key] = item
      else:
        for style in styles:
          style[key] = value
    return styles
  
  def create_stack(self, *histos, **styles_kwargs):
    '''makes a HistStack out of provided histograms,
    styles them according to provided styles and default
    ones'''
    sort  = True
    histos = list(histos)
    if 'sort' in styles_kwargs:
      sort = styles_kwargs['sort']  
      del styles_kwargs['sort']
    if sort:
      histos.sort(key=lambda x: x.Integral())
    stack = plotting.HistStack()
    styles = BasePlotter._kwargs_to_styles_(
      styles_kwargs, 
      len(histos)
      )
    for histo, style in izip_longest(histos, styles):
      style = style if style else {}
      self.style_histo(histo, **style)
      stack.Add(histo)
    return stack
      
  @staticmethod
  def _get_y_range_(*histos):
    def __get_min__(obj):
      if isinstance(obj, plotting.HistStack):
        return sum(obj.hists).min() 
      elif isinstance(obj, ROOT.TGraph):
        return obj.GetYmin()
      else:
        return obj.min()
    def __get_max__(obj):
      if isinstance(obj, plotting.HistStack):
        return sum(obj.hists).max() 
      elif isinstance(obj, ROOT.TGraph):
        return obj.GetYmax()
      else:
        return obj.max()

    ymin = min(
      __get_min__(i)
      for i in histos
      )
    ymax = max(
      __get_max__(i)
      for i in histos
      )
            
    if ymin >= 0:
      ymin = 0 + (ymax-ymin)/100000000
      ymax = ymax + (ymax-ymin)*0.2
    elif ymin < 0 and ymax > 0:
      ymin = ymin - (ymax-ymax)*0.2
      ymax = ymax + (ymax-ymin)*0.2
    else:
      ymin = ymin - (ymax-ymin)*0.2
      ymax = 0 - (ymax-ymin)/100000000
    return ymin, ymax
  
  def _get_defaulted_par_(self, key, kwargs, default):
    ret = default
    if key in kwargs:
      do_clone = kwargs[key]
      del kwargs[key]
    elif key in self.defaults:
      ret = self.defaults[key]
    return ret, kwargs

  def plot(self, hh, legend_def=None, logx=False, logy=False, 
    logz=False, xtitle='', ytitle='', writeTo='', **kwargs):
    '''plots a single histogram. rootpy styling can be passed as 
    keyword args as the cloning policy (wether or not to clone the 
    histo before styling it) with key "clone" (defaulted True) and assigning the 
    canvas name by the key name_canvas (dedfaulted False)'''
    do_clone, style = self._get_defaulted_par_('clone', kwargs, True)    
    name_canvas, style = self._get_defaulted_par_('name_canvas', style, False)    

    BasePlotter.set_canvas_style(self.canvas, logx, logy, logz)
    if name_canvas:
      self.canvas.name = 'c'+hh.name

    histo = hh.Clone() if do_clone else hh
    self.pad.cd()
    self.style_histo(histo, **style)
    y_range = BasePlotter._get_y_range_(histo)
    if isinstance(histo, plotting.HistStack):
      histo.SetMinimum(y_range[0])
      histo.SetMaximum(y_range[1])
    else:
      histo.yaxis.range_user = y_range
    histo.Draw()
    #after drawing because of stacks -.-'
    if xtitle:
      histo.xaxis.title = xtitle
    if ytitle:
      histo.yaxis.title = ytitle    
    histo.Draw()
    self.keep.append(histo)
    if legend_def is not None:
      legend_def.entries = [histo]
      legend = legend_def.make_legend()
      legend.Draw()
      self.keep.append(legend)

    if writeTo:
      self.save(writeTo)
    return histo
  
  def overlay(
    self, hhs, legend_def=None, logx=False, logy=False, 
    logz=False, writeTo='', y_range=None, xtitle='', ytitle='', 
    yaxis_divisions=None, **kwargs):
    '''Overlays multiple histograms. rootpy styling can be passed as 
    keyword args as the cloning policy (wether or not to clone the 
    histo before styling it) with key "clone". The styling passed as list are 
    applied one per histogram, styles with single value are used for every 
    histogram'''
    do_clone, styles_kw = self._get_defaulted_par_('clone', kwargs, True)
    histos = [i.Clone() if do_clone else i for i in hhs] #clone to avoid messing up

    ROOT.gPad.SetLogx(logx)
    ROOT.gPad.SetLogy(logy)
    ROOT.gPad.SetLogz(logz)

    styles = BasePlotter._kwargs_to_styles_(styles_kw, len(histos))
    first = True
    for histo, style in zip(histos, styles):
      self.style_histo(histo, **style)
      if yaxis_divisions is not None:
        histo.yaxis.SetNdivisions(yaxis_divisions)
      histo.Draw('' if first else 'same')
      #after drawing because of stacks -.-'
      histo.xaxis.title = xtitle if xtitle else histo.xaxis.title
      histo.yaxis.title = ytitle if ytitle else histo.yaxis.title
      ROOT.gPad.Modified()
      if first:
        y_range = BasePlotter._get_y_range_(*histos) if y_range is None else y_range 
        if isinstance(histo, plotting.HistStack):
          histo.SetMinimum(y_range[0])
          histo.SetMaximum(y_range[1])
        else:
          histo.yaxis.range_user = y_range
      first = False
      self.keep.append(histo)

    if legend_def is not None:
      legend_def.entries = histos
      legend = legend_def.make_legend()
      legend.Draw()
      self.keep.append(legend)

    if writeTo:
      self.save(writeTo)
    return None
    
  def compare(self, ref, targets, method, xtitle='', ytitle='', **styles_kw):
    for target in targets:
      target.title = ''
      target.SetStats(False)
      #set comparison values depending on method
      for rbin, tbin in zip(ref, target):
        if method == 'pull':
          error = quad(rbin.error, tbin.error)
          tbin.value = (tbin.value-rbin.value)/error if error else 9999
          tbin.error = 0.01
        elif method == 'ratio':
          if rbin.value and tbin.value:
            result = tbin.value/rbin.value
            error  = quad((tbin.error/tbin.value), (rbin.error/rbin.value))
            tbin.value = result
            tbin.error = error
          else:
            tbin.value = 9999
            tbin.error = 1
        elif method == 'diff':
          if rbin.value:
            val = (tbin.value-rbin.value)/rbin.value
            if (tbin.value-rbin.value) != 0:
              err = sqrt(((rbin.error**2+tbin.error**2)/(rbin.value-rbin.value))**2+(rbin.error/rbin.value)**2)*val
            else:
              err = 9999
            tbin.value = val
            tbin.err = err
          else:
            tbin.value = 9999
            tbin.err = 1
      
      #set comparison labels
      ylabels = {
        'pull' : 'Pull',
        'ratio': 'Ratio',
        'diff' : 'Difference'
        }
      yranges = {
        'pull' : (-2.999,2.999),
        'ratio': (0.,1.999),
        'diff' : (-0.499,0.499)
        }
      styles_kw['drawstyle'] = 'e x0'
      self.overlay(
        targets, y_range=yranges[method], xtitle=xtitle, 
        yaxis_divisions=4, ytitle=ylabels[method], **styles_kw)

  def dual_pad_format(self):
    if self.lower_pad is None:
      self.canvas.cd()
      self.canvas.SetCanvasSize( self.canvas.GetWw(), int(self.canvas.GetWh()*1.3) )
      self.set_canvas_style(self.canvas)
      self.pad.SetPad(0, 0.33, 1., 1.)
      self.set_canvas_style(self.pad)
      self.pad.SetBottomMargin(0.001)
      self.pad.Draw()
      self.canvas.cd()
      #create lower pad
      self.lower_pad = plotting.Pad(0, 0., 1., 0.33)
      self.set_canvas_style(self.lower_pad)
      self.lower_pad.Draw()
      self.lower_pad.cd()
      self.pad.cd()
      self.lower_pad.SetTopMargin(0.005)
      self.lower_pad.SetGridy(True)
      self.lower_pad.SetBottomMargin(self.lower_pad.GetBottomMargin()*3)
    
    labelSizeFactor1 = (self.pad.GetHNDC()+self.lower_pad.GetHNDC()) / self.pad.GetHNDC()
    labelSizeFactor2 = (self.pad.GetHNDC()+self.lower_pad.GetHNDC()) / self.lower_pad.GetHNDC()
    mm = min(labelSizeFactor1, labelSizeFactor2)
    return labelSizeFactor1/mm, labelSizeFactor2/mm
  
  def overlay_and_compare(self, histos, reference, method='pull', 
    legend_def=None, logx=False, logy=False, xtitle='', ytitle='',
    logz=False, writeTo='', **styles_kw):
    labelSizeFactor1, labelSizeFactor2 = self.dual_pad_format()
    self.pad.cd()
    self.label_factor = labelSizeFactor1

    self.overlay(
      histos+[reference],
      legend_def=legend_def,
      logx=False, logy=False, 
      logz=False, ytitle=ytitle,
      **styles_kw
      )

    self.lower_pad.cd()
    self.label_factor = labelSizeFactor2
    to_compare = [
      sum(i.hists) if isinstance(i, plotting.HistStack) else i.Clone()
      for i in histos
      ]
    self.compare(
      reference.Clone(), to_compare, method, xtitle=xtitle, 
      ytitle=ytitle, **styles_kw)

    if writeTo:
      self.save(writeTo)

  def add_watermark(self, text):
      ''' Add a watermark'''
      self.pad.cd()
      latex = ROOT.TLatex()
      latex.SetNDC();
      latex.SetTextSize(0.04);
      latex.SetTextAlign(31);
      latex.SetTextAlign(11);
      self.keep.append(latex.DrawLatex(0.18,0.96, text));
                      
  def add_legend(self, samples, leftside=True, entries=None):
      ''' Build a legend using samples.

      If entries is None it will be taken from len(samples)

      '''
      nentries = entries if entries is not None else len(samples)
      legend = None
      if leftside:
          legend = plotting.Legend(nentries, leftmargin=0.03, topmargin=0.05, rightmargin=0.65)
      else:
          legend = plotting.Legend(nentries, rightmargin=0.07, topmargin=0.05, leftmargin=0.45)
      for sample in samples:
          if isinstance(sample, plotting.HistStack):
              for s in sample:
                  if getattr(sample, 'inlegend', True):
                      label = s.GetTitle()
                      style = s.legendstyle
                      legend.AddEntry(s, style, label) 
          else:
              legend.AddEntry(sample)
      legend.SetEntrySeparation(0.0)
      legend.SetMargin(0.35)
      legend.Draw()
      self.keep.append(legend)
      return legend

  def make_text_box(self, text, position='NE'):
      '''Adds a text box in the main pad'''
      #FIXME make width smart depending on the text width
      max_line_len = max(len(i) for i in text.split('\n'))
      nlines = len(text.split('\n'))
      p = LegendDefinition.ndc_coordinates(position.lower(), max_line_len, nlines) \
         if isinstance(position, str) \
         else position
      
      stat_box = ROOT.TPaveText(p[0], p[1], p[2], p[3], 'NDC')
      for line in text.split('\n'):
          stat_box.AddText(line)
      
      #Set some graphics options not to suck
      stat_box.UseCurrentStyle()
      stat_box.SetTextAlign(32)
      stat_box.SetFillColor(0)
      stat_box.SetBorderSize(0)
      stat_box.SetMargin(0.)
      stat_box.SetTextSize(0.037)        
      return stat_box

  def reset(self):
      '''hard graphic reset'''
      del self.canvas
      del self.pad
      del self.lower_pad
      self.keep = []
      self.canvas = plotting.Canvas(800, 800, name='adsf', title='asdf')
      BasePlotter.set_canvas_style(self.canvas)
      self.canvas.cd()
      self.pad    = plotting.Pad(0., 0., 1., 1.) #ful-size pad
      self.pad.Draw()
      BasePlotter.set_canvas_style(self.pad)
      self.pad.cd()
      self.lower_pad = None
      self.label_factor = None

  def save(self, filename=None, verbose=False, **inkwargs):
      ''' Save the current canvas contents to [filename] '''
      kwargs = {
          'png' : True, 'pdf' : True, 'dotc' : False, 
          'dotroot' : False, 'json' : False
          }
      kwargs.update(
          self.defaults['save'] if 'save' in self.defaults else {}
          )
      kwargs.update(
          inkwargs
          )
      #
      if filename is None:
        filename = self.canvas.name
      
      #self.pad.Draw()
      self.canvas.Update()
      if not os.path.exists(self.outputdir):
          os.makedirs(self.outputdir)
      if verbose:
          print 'saving '+os.path.join(self.outputdir, filename) + '.png'
      if kwargs['png']: self.canvas.SaveAs(os.path.join(self.outputdir, filename) + '.png')
      if kwargs['pdf']: self.canvas.SaveAs(os.path.join(self.outputdir, filename) + '.pdf')
      if kwargs['dotc']:
          self.canvas.SaveAs(os.path.join(self.outputdir, filename) + '.C')
      if kwargs['json']:
          jdict = {}
          for obj in self.keep:
              if isinstance(obj, ROOT.TH1):
                  jdict[obj.GetTitle()] = [obj.GetBinContent(1), obj.GetBinError(1)] 
              if isinstance(obj, ROOT.THStack):
                  jdict['hist_stack'] = {}
                  for i in obj.GetHists():
                      jdict['hist_stack'][i.GetTitle()] = [i.GetBinContent(1), i.GetBinError(1)]
          with open(os.path.join(self.outputdir, filename) + '.json', 'w') as jout:
              jout.write(prettyjson.dumps(jdict))
      if kwargs['dotroot']:
          logging.error(
              'This functionality still has to be implemented '
              'properly, due to the awsome ROOT "features"')
          rfile = os.path.join(self.outputdir, filename) + '.root'
          with io.root_open(rfile, 'recreate') as tfile:
              self.canvas.Write()
              for obj in self.keep:
                  if isinstance(obj, plotting.HistStack):
                      for hist in obj.hists:
                          hist.Write()
                  obj.Write()

      self.reset()
  
if __name__ == '__main__':
  #from rootpy.io import root_open
  p = BasePlotter()
  myfile = ROOT.TFile.Open('plots/2015May05/ttxsec_standard/ptthad/ptthad.root', 'READ')
  outfile = ROOT.TFile.Open('test_baseplotter.root','RECREATE')
  outfile.cd()
  for directory in (i.ReadObj() for i in myfile.GetListOfKeys() if i.GetName().startswith('Bin')):
    dirname=directory.GetName()
    print dirname
    tt_wrong = directory.Get("tt_wrong")
    print 'I am here 0.1'
    tt_right = directory.Get("tt_right")
    print 'I am here 0.2'
    single_top = directory.Get("single_top")
    print 'I am here 0.3'
    only_thad_right = directory.Get("only_thad_right")
    print 'I am here 0.4'
    vjets = directory.Get("vjets")
    print 'I am here 0.5'
    data_obs = directory.Get("data_obs")
    print 'I am here 0.6'
    
    data_obs.GetXaxis().SetTitle("Mass discriminant")
    data_obs.GetYaxis().SetTitle("Events")
    
    print 'I am here 1'
    leg = LegendDefinition()
    leg.title = dirname
    leg.position = 'ne'
    leg.labels = ['Data', 'V+jets', 'Single top', 'Only t_{had} right', 'Wrong t#bar{t}', 'Right t#bar{t}']
    
    print 'I am here 2'
    
    linestyles = [1,1,1,1,1,1,1,1,1]
    markerstyles = [20,21,22,23,20,21,22,23,20,21]
    colors = [1,2,3,4,5,0,6,7,8,9]
    histos = [data_obs, vjets, single_top, only_thad_right, tt_wrong, tt_right]
    print 'I am here 3'
    p.create_and_write_canvas_with_comparison('test_stack_pull_'+dirname, linestyles, markerstyles, colors, leg, False, False, histos, write=True, comparison='pull', stack=True)
    print 'I am here 4'
    p.create_and_write_canvas_with_comparison('test_stack_ratio_'+dirname, linestyles, markerstyles, colors, leg, False, False, histos, write=True, comparison='ratio', stack=True)
    print 'I am here 5'
    p.create_and_write_canvas_with_comparison('test_stack_diff_'+dirname, linestyles, markerstyles, colors, leg, False, False, histos, write=True, comparison='diff', stack=True)
    print 'I am here 6'
    linestyles = [0,0,0,0,0,0,0,0,0,0]
    colors = [1,2,3,4,5,6,7,8,9,10]
    histos = [data_obs, tt_right, tt_wrong, only_thad_right, single_top, vjets]
    leg.labels = ['Data', 'Right t#bar{t}', 'Wrong t#bar{t}', 'Only t_{had} right', 'Single top', 'V+jets']
    p.create_and_write_canvas_with_comparison('test_pull_'+dirname, linestyles, markerstyles, colors, leg, False, False, histos, write=True, comparison='pull', stack=False)
    print 'I am here 7'
    p.create_and_write_canvas_with_comparison('test_ratio_'+dirname, linestyles, markerstyles, colors, leg, False, False, histos, write=True, comparison='ratio', stack=False)
    print 'I am here 8'
    p.create_and_write_canvas_with_comparison('test_diff_'+dirname, linestyles, markerstyles, colors, leg, False, False, histos, write=True, comparison='diff', stack=False)
    
    print 'I am here 9'
    p.create_and_write_canvas_single('test_single_'+dirname, 0, 20, 2, False, False, tt_right, write=True)
    print 'I am here 10'
    p.create_and_write_canvas_many('test_many_'+dirname, linestyles, markerstyles, colors, leg, False, False, histos, write=True)
    
    
    
    #for histo in histos:
        #del histo
    #del canvas
    print 'I am here 11'
    
  outfile.Close()
  myfile.Close()
    
    

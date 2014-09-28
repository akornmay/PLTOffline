#!/usr/bin/env python

"""
Helper functions for TimingAlignment.py
"""

###############################
# Imports
###############################

import os
import sys
import array
import math

import ROOT


###############################
# Init ROOT
###############################

ROOT.gStyle.SetPadLeftMargin(0.15)
ROOT.gStyle.SetPadRightMargin(0.14)
ROOT.gStyle.SetPadBottomMargin(0.12)
ROOT.gStyle.SetPadTopMargin(0.05)
ROOT.gROOT.ForceStyle()

c = ROOT.TCanvas("","",800,800)


###############################
# print_usage
###############################

def print_usage():
    print "Usage: python {0} run action".format(sys.argv[0])
    print "run: run number (int)"
    print "action: 0=analyze    1=run on small sample     2=find alignment"
    print "Example: python 70 0"
# End of print_usage


###############################
# coordinate_to_box
###############################

def coordinate_to_box(x, y, min_x, max_x, min_y, max_y, n):
    """ Map x/y coordiantes into a n-times-n array of boxes.
    Return [x_box, y_box]
    Where x_box/y_box are the boxes-id to which the position is mapped.
    The x_xbox/y_box range goes from 0 to n-1. 
    Return the number -1 instead of a list if one of the positions is outside the target range
    """
    
    # Make sure the input position is valid
    if ( (x < min_x) or
         (x > max_x) or
         (y < min_y) or
         (y > max_y)):
        return -1

    # What is the range that should go into one box
    unit_length_x = 1.0 * (max_x - min_x) / n
    unit_length_y = 1.0 * (max_y - min_y) / n
    

    # Convert 
    # For example 1 .. 4 into 4 boxes:
    # 0.0 .. 0.99999 into box 0
    # 1.0 .. 1.99999 into box 1
    # 2.0 .. 2.99999 into box 3
    # 3.0 .. 3.99999 into box 4
    x_box = int(math.floor((x-min_x)/unit_length_x))
    y_box = int(math.floor((y-min_y)/unit_length_y))

    return [x_box, y_box]
# end of coordinate_to_box    


###############################
# pixel_to_pad_time
###############################

def pixel_to_pad_time(pixel_now, pixel_0, pad_now, pad_0, offset, slope):
    
    # How many ticks have passed since first pixel time-stamp
    delta_pixel = pixel_now - pixel_0

    # Convert ticks to seconds (1 tick ~ 25 ns)            
    delta_second = delta_pixel * 25e-9 + offset

    # Add time difference (in seconds) to initial pad time
    return pad_0 + delta_second + slope * (pad_now - pad_0)

# End of pixel-to-pad time conversion


###############################
# Class: Diamond
###############################

class Diamond:
    """ Storage class for diamond position related variables
    
    Current memeber variables:
    name
    x_pos_min
    x_pos_max
    y_pos_min
    y_pos_max
    """

    diamonds = {}

    def __init__(self,
                 name,
                 x_pos_min,
                 x_pos_max,
                 y_pos_min,
                 y_pos_max):
        self.name = name
        self.x_pos_min = x_pos_min
        self.x_pos_max = x_pos_max
        self.y_pos_min = y_pos_min
        self.y_pos_max = y_pos_max
        
        Diamond.diamonds[name] = self

    # End __init__
    
# End of class Diamond


###############################
# Class: RunTiming
###############################

class RunTiming:
    """ Storage class for timing alignment information between pad and pixel data.
    
    Current memeber variables:
    run number
    offset (in seconds)
    slope (in seconds/second)
    align_pixel (which pixel event to use for aligning clocks)    
    align_pad (which pad event to use for aligning clocks)    
    diamond_name (which diamond pad was used. This is mainly used for position information at the moment)
    bias_voltage
    number of channels
    """
    
    runs = {}

    def __init__(self,
                 run, 
                 offset = 0.,
                 slope  = 1.9e-6,
                 align_pixel = 0,
                 align_pad = 0,
                 diamond_name = "dummy",
                 bias_voltage = 0,
                 n_channels = 3,
             ):
        self.run = run
        self.offset = offset
        self.slope = slope
        self.align_pixel = align_pixel
        self.align_pad = align_pad
        self.diamond_name = diamond_name
        self.bias_voltage = bias_voltage
        self.n_channels = n_channels

        RunTiming.runs[run] = self

    # End __init__
    
    def print_info(self):
        print 'RunTiming({0}, {1}, {2}, {3}, {4}, "{5}", {6}, {7}),'.format(self.run,
                                                                            self.offset, 
                                                                            self.slope, 
                                                                            self.align_pixel,
                                                                            self.align_pad,
                                                                            self.diamond_name,
                                                                            self.bias_voltage,
                                                                            self.n_channels)

    # End of print_info

    
# End of class RunTiming

#  
#  ###############################
#  # Try to find two good events for aligning times
#  ###############################
#  
#  def find_alignment(run):
#  
#      di_runs[run] = RunTiming()
#  
#      # We are going to select the alignment event with the lowest residual RMS
#      # Make a list of triples: [pixel_event, pad_event, residual RMS]
#      index_pixel = 0
#      index_pad = 1
#      index_rms = 2
#      li_residuals_rms = []
#      
#      # Loop over potential pad events for aligning:
#      for i_align_pad in xrange(max_align_pad):
#  
#          tree_pad.GetEntry(i_align_pad)
#          initial_t_pad = getattr(tree_pad, br_t_pad)
#  
#          # Loop over potential pixel events for aligning:
#          for i_align_pixel in xrange(max_align_pixel):
#  
#              tree_pixel.GetEntry(i_align_pixel)
#  
#              initial_t_pixel = getattr(tree_pixel, br_t_pixel)
#  
#              h = ROOT.TH1F("", "", 100, -0.005, 0.005)
#  
#              i_pixel = 0
#  
#              for i_pad in xrange(0, 1000):
#  
#                  tree_pad.GetEntry(i_pad)
#                  time_pad = getattr(tree_pad, br_t_pad)
#  
#                  delta_ts = []
#  
#                  for i_pixel_test in range(i_pixel+1-10, i_pixel+1+10):        
#  
#                      if i_pixel_test < 0:
#                          continue
#  
#                      tree_pixel.GetEntry(i_pixel_test)        
#                      time_pixel = getattr(tree_pixel, br_t_pixel)
#  
#                      delta_ts.append( [i_pixel_test, pixel_to_pad_time(time_pixel, 
#                                                                        initial_t_pixel, 
#                                                                        time_pad, 
#                                                                        initial_t_pad) - time_pad])
#  
#                  best_match = sorted(delta_ts, key = lambda x:abs(x[1]))[0]
#                  h.Fill(best_match[1])
#  
#                  # Set the starting-value for the next iteration 
#                  # Our basis assumption is no-missing event
#                  i_pixel = best_match[0] + 1
#                  # End of loop over pad events
#  
#              h.Draw()
#              c.Print("run_{0}/ipad_{1}_ipixel_{2}.pdf".format(run, i_align_pad, i_align_pixel))
#  
#              print "Pad Event {0} / Pixel Event {1}: Mean: {2:2.6f} RMS:{3:2.6f}".format(i_align_pad, 
#                                                                                          i_align_pixel, 
#                                                                                          h.GetMean(), 
#                                                                                          h.GetRMS())
#              
#              # Make sure we have enough events actually in the histogram
#              if h.Integral() > 900:
#                  li_residuals_rms.append( [i_align_pixel, i_align_pad, h.GetRMS()] )
#                              
#          # End of loop over pixel alignment events
#      # End of loop over pad alignment events
#  
#      best_i_align_pixel = sorted(li_residuals_rms, key = lambda x: abs(x[index_rms]))[0][index_pixel]
#      best_i_align_pad = sorted(li_residuals_rms, key = lambda x: abs(x[index_rms]))[0][index_pad]
#      
#      print "Best pad / pixel event for alignment: ", best_i_align_pad, best_i_align_pixel
#  
#      di_runs[run].align_pixel = best_i_align_pixel
#      di_runs[run].align_pad = best_i_align_pad
#      di_runs[run].print_info()
#  
#  if action == 2:
#      find_alignment(run)
#      sys.exit()
#  
#  ###############################
#  # Look at time drift
#  ###############################
#  
#  if action == 1:
#      print "Doing Initial run - restricting events"
#      max_events = min(25000, tree_pad.GetEntries()-1)
#  
#      # Update final-times for test analysis
#      tree_pad.GetEntry(max_events)
#      tree_pixel.GetEntry(max_events)        
#      final_t_pad = getattr(tree_pad, br_t_pad)
#      final_t_pixel = getattr(tree_pixel, br_t_pixel)
#  
#  else:
#      max_events = tree_pad.GetEntries()-1
#  
#  
#  # Book histograms
#  h2 = ROOT.TH2D("", "", 2000, 0, final_t_pad-initial_t_pad, 300, -0.01, 0.01)
#  h = ROOT.TH1D("","",500, -0.007, 0.007)
#  h_delta_n = ROOT.TH1D("", "", 21, -10, 10)
#  h_calib_events = ROOT.TH2D("", "", 16, -0.5, 15.5, 2, -0.5, 1.5)
#  
#  h_tracks = ROOT.TH2D("","", 100, -1, 1, 100, -1, 1)
#  h_integral = ROOT.TH3D("","", 100, -1, 1, 100, -1, 1, 200, -1000, 1000)
#  
#  h_tracks_zoom = ROOT.TH2D("","", 
#                            50, # bins in x 
#                            Diamond.diamonds[di_runs[run].diamond_name].x_pos_min,
#                            Diamond.diamonds[di_runs[run].diamond_name].x_pos_max,
#                            50, # bins in y
#                            Diamond.diamonds[di_runs[run].diamond_name].y_pos_min,
#                            Diamond.diamonds[di_runs[run].diamond_name].y_pos_max)
#  
#  h_integral_zoom = ROOT.TH3D("","", 
#                              50, # bins in x 
#                              Diamond.diamonds[di_runs[run].diamond_name].x_pos_min,
#                              Diamond.diamonds[di_runs[run].diamond_name].x_pos_max,
#                              50, # bins in y
#                              Diamond.diamonds[di_runs[run].diamond_name].y_pos_min,
#                              Diamond.diamonds[di_runs[run].diamond_name].y_pos_max,
#                              200, -1000, 1000)
#  
#  # Also create a matrix of histograms for the PH as a function of the
#  # location
#  n_boxes = 5 # How many boxes per side. Will use the boundaries of the
#              # diamond and the coordinate_to_box function
#  integral_box_matrix = []
#  for x_pos in range(n_boxes):
#      tmp_li = []
#      for y_pos in range(n_boxes):
#          if di_runs[run].bias_voltage > 0:
#              tmp_li.append(ROOT.TH1D("", "", 200, -500, 200))
#          else:
#              tmp_li.append(ROOT.TH1D("", "", 200, -200, 500))
#      # End of x-loop
#      integral_box_matrix.append(tmp_li)
#  # End of y-loop        
#  
#          
#  tree_pad.GetEntry(di_runs[run].align_pad)
#  tree_pixel.GetEntry(di_runs[run].align_pixel)
#  
#  initial_t_pad = getattr(tree_pad, br_t_pad)
#  initial_t_pixel = getattr(tree_pixel, br_t_pixel)
#  
#  i_pixel = 0
#  
#  for i_pad in xrange(max_events):
#  
#      if i_pad % 1000 == 0:
#          print "{0} / {1}".format(i_pad, max_events)
#  
#      tree_pad.GetEntry(i_pad)
#      time_pad = getattr(tree_pad, br_t_pad)
#  
#      delta_ts = []
#      for i_pixel_test in range(i_pixel-6, i_pixel+6):        
#  
#          if i_pixel_test < 0:
#              continue
#  
#          tree_pixel.GetEntry(i_pixel_test)        
#          time_pixel = getattr(tree_pixel, br_t_pixel)
#  
#          delta_ts.append( [i_pixel_test, pixel_to_pad_time(time_pixel, 
#                                                            initial_t_pixel, 
#                                                            time_pad, 
#                                                            initial_t_pad) - time_pad])
#  
#  
#      best_match =  sorted(delta_ts, key = lambda x:abs(x[1]))[0]
#  
#      i_pixel = best_match[0] 
#      tree_pixel.GetEntry(i_pixel)        
#  
#      h_delta_n.Fill(best_match[0]-i_pixel+1)
#      h.Fill(best_match[1])
#      h2.Fill(time_pad-initial_t_pad, best_match[1])
#  
#      # Check if we are happy with the timing
#      # (residual below 1 ms)
#      if abs(best_match[1]) < 0.001:        
#          hit_plane_bits = getattr(tree_pixel, br_hit_plane_bits_pixel)
#          calib_flag = getattr(tree_pad, br_calib_flag_pad)
#          h_calib_events.Fill(hit_plane_bits, calib_flag)
#  
#          out_branches["n_pad"][0] = getattr(tree_pad, br_n_pad)
#          out_branches["accepted"][0] = 1
#          out_branches["track_x"][0] = getattr(tree_pixel, br_track_x)
#          out_branches["track_y"][0] = getattr(tree_pixel, br_track_y)
#          out_branches["integral50"][0] = getattr(tree_pad, br_integral50)
#  
#          tree_out.Fill()            
#          
#          h_tracks.Fill(getattr(tree_pixel, br_track_x),
#                        getattr(tree_pixel, br_track_y))
#  
#          h_tracks_zoom.Fill(getattr(tree_pixel, br_track_x),
#                             getattr(tree_pixel, br_track_y))
#          
#          h_integral.Fill(getattr(tree_pixel, br_track_x),
#                          getattr(tree_pixel, br_track_y),
#                          getattr(tree_pad, br_integral50))
#  
#          h_integral_zoom.Fill(getattr(tree_pixel, br_track_x),
#                               getattr(tree_pixel, br_track_y),
#                               getattr(tree_pad, br_integral50))
#  
#          ret = coordinate_to_box(getattr(tree_pixel, br_track_x), 
#                                             getattr(tree_pixel, br_track_y),
#                                             Diamond.diamonds[di_runs[run].diamond_name].x_pos_min,
#                                             Diamond.diamonds[di_runs[run].diamond_name].x_pos_max,
#                                             Diamond.diamonds[di_runs[run].diamond_name].y_pos_min,
#                                             Diamond.diamonds[di_runs[run].diamond_name].y_pos_max, n_boxes)
#          if ret != -1:
#              x_box = ret[0]
#              y_box = ret[1]
#              integral_box_matrix[x_box][y_box].Fill( getattr(tree_pad, br_integral50))
#          
#  
#      # done filling tree and calibration histogram
#  
#  # End of loop over pad events
#  
#  
#  
#  h.GetXaxis().SetTitle("t_{pixel} - t_{pad} [s]")
#  h.GetYaxis().SetTitle("Events")
#  h.Draw()
#  c.Print("run_{0}/residual{1}.pdf".format(run, test_string))
#  
#  print h2,c
#  fun = ROOT.TF1("fun", "[0]+[1]*x")
#  h2.Fit(fun,"","")
#  h2.GetYaxis().SetTitleOffset(1.9)
#  h2.GetXaxis().SetTitle("t_{pad} [s]")
#  h2.GetYaxis().SetTitle("t_{pixel} - t_{pad} [s]")
#  h2.Draw()
#  c.Print("run_{0}/time{1}.pdf".format(run, test_string))
#  
#  di_runs[run].offset -= fun.GetParameter(0)
#  di_runs[run].slope  -= fun.GetParameter(1)    
#  
#  
#  c.SetLogy(1)
#  h_delta_n.Draw()
#  c.Print("run_{0}/delta_n{1}.pdf".format(run, test_string))
#  c.SetLogy(0)
#  
#  
#  ROOT.gStyle.SetOptStat(0)
#  c.SetLogz(1)
#  h_calib_events.GetXaxis().SetTitle("Pixel Plane Hit Bit")
#  h_calib_events.GetYaxis().SetTitle("Pad Calibration Flag")
#  h_calib_events.GetYaxis().SetTitleOffset(1.5)
#  h_calib_events.Draw("COLZTEXT")
#  c.Print("run_{0}/calib_events{1}.pdf".format(run, test_string))
#  
#  ROOT.gStyle.SetOptStat(0)
#  c.SetLogz(1)
#  h_tracks.GetXaxis().SetTitle("Pad position x [cm]")
#  h_tracks.GetYaxis().SetTitle("Pad position y [cm]")
#  h_tracks.GetYaxis().SetTitleOffset(1.5)
#  h_tracks.Draw("COLZ")
#  c.Print("run_{0}/tracks{1}.pdf".format(run, test_string))
#  
#  ROOT.gStyle.SetOptStat(0)
#  c.SetLogz(1)
#  h_tracks_zoom.GetXaxis().SetTitle("Pad position x [cm]")
#  h_tracks_zoom.GetYaxis().SetTitle("Pad position y [cm]")
#  h_tracks_zoom.GetYaxis().SetTitleOffset(1.5)
#  h_tracks_zoom.Draw("COLZ")
#  c.Print("run_{0}/tracks_zoom{1}.pdf".format(run, test_string))
#  
#  
#  ROOT.gStyle.SetOptStat(0)
#  c.SetLogz(0)
#  proj = h_integral.Project3DProfile("yx")
#  proj.SetTitle("")
#  proj.GetXaxis().SetTitle("Pad Position x [cm]")
#  proj.GetYaxis().SetTitle("Pad Position y [cm]")
#  proj.GetXaxis().SetTitleOffset(1.2)
#  proj.GetYaxis().SetTitleOffset(1.5)
#  
#  proj.Draw("COLZ")
#  c.Print("run_{0}/integral{1}_fullrange.pdf".format(run, test_string))
#  
#  
#  ROOT.gStyle.SetOptStat(0)
#  c.SetLogz(0)
#  proj_zoom = h_integral_zoom.Project3DProfile("yx")
#  proj_zoom.SetTitle("")
#  proj_zoom.GetXaxis().SetTitle("Pad Position x [cm]")
#  proj_zoom.GetYaxis().SetTitle("Pad Position y [cm]")
#  proj_zoom.GetXaxis().SetTitleOffset(1.2)
#  proj_zoom.GetYaxis().SetTitleOffset(1.5)
#  
#  proj_zoom.Draw("COLZ")
#  c.Print("run_{0}/integral{1}_zoom_fullrange.pdf".format(run, test_string))
#  
#  
#  if di_runs[run].bias_voltage > 0:
#      proj.SetMinimum(-550)
#      proj.SetMaximum(50)
#  
#      proj_zoom.SetMinimum(-550)
#      proj_zoom.SetMaximum(50)
#  else:
#      proj.SetMinimum(-50)
#      proj.SetMaximum(500)
#  
#      proj_zoom.SetMinimum(-50)
#      proj_zoom.SetMaximum(500)
#  
#  proj.Draw("COLZ")
#  c.Print("run_{0}/integral{1}.pdf".format(run, test_string))
#  
#  proj_zoom.Draw("COLZ")
#  c.Print("run_{0}/integral_zoom{1}.pdf".format(run, test_string))
#  
#  
#  
#  
#  
#  for x_pos in range(n_boxes):
#      for y_pos in range(n_boxes):
#          
#          fun = ROOT.TF1("", "gaus")
#          integral_box_matrix[x_pos][y_pos].Fit(fun)
#          print "XXX X: {0} Y: {1} Mean: {2:2.2f} RMS {3:2.2f}".format(x_pos, 
#                                                                       y_pos, 
#                                                                       fun.GetParameter(1), 
#                                                                       fun.GetParameter(2))
#          integral_box_matrix[x_pos][y_pos].Draw()
#          c.Print("run_{0}/1d_integral_x_{1}_y_{2}{3}.pdf".format(run, x_pos, y_pos, test_string))
#          c.Print("run_{0}/1d_integral_x_{1}_y_{2}{3}.png".format(run, x_pos, y_pos, test_string))
#  
#  
#  f_out.Write()
#  
#  di_runs[run].print_info()

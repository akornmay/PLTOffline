#!/usr/bin/env python

"""
Study timing between pixel and pad detectors.
"""

###############################
# Imports
###############################

import os
import sys
import array

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
# Helper: print_usage
###############################

def print_usage():
    print "Usage: python {0} run action".format(sys.argv[0])
    print "run: run number (int)"
    print "action: 0=analyze    1=run on small sample     2=find alignment"
    print "Example: python 70 0"
# End of print_usage


###############################
# Get configuration
###############################

max_align_pad = 40
max_align_pixel = 40

if not len(sys.argv) == 3:
    print_usage()
    sys.exit()

try:
    run = int(sys.argv[1])
    action = int(sys.argv[2])
except:
    print_usage()
    sys.exit()

print "Going to process run {0} with action = {1}".format(run, action)

campgain = "bt2014_09"

###############################
# Class: RunTiming
###############################

class RunTiming:
    """ Storage class for timing alignment information between pad and pixel data.
    
    Current memeber variables:
    offset (in seconds)
    slope (in seconds/second)
    align_pixel (which pixel event to use for aligning clocks)    
    align_pad (which pad event to use for aligning clocks)    
    """

    def __init__(self,
                 offset = 0.,
                 slope  = 1.9e-6,
                 align_pixel = 0,
                 align_pad = 0):
        self.offset = offset
        self.slope = slope
        self.align_pixel = align_pixel
        self.align_pad = align_pad
    # End __init__
    
    def print_info(self):
        print "RunTiming({0}, {1}, {2}, {3})".format(self.offset, 
                                                     self.slope, 
                                                     self.align_pixel,
                                                     self.align_pad)

# Enf of class RunTiming


###############################
# Put additional run timings here
###############################

di_runs = {
    6   : RunTiming( 0.0003045,  2.155918e-06, 0),
    12  : RunTiming(-0.00030472, 1.955999e-06, 0),
    38  : RunTiming( 0.00052454, 1.9e-06,      4),
    63  : RunTiming(-0.00030911, 1.837389e-06, 0),
    65  : RunTiming( 0.00034346, 1.864050e-06, 0),
    68  : RunTiming(-0.00085284, 2.026819e-06, 6),
    70  : RunTiming(-0.00028498, 1.910828e-06, 6),
    109 :RunTiming(0.000323963498273, 1.81841520034e-06, 15, 1),
    131 : RunTiming(-0.000191132147971, 1.93697727798e-06, 13, 2),
    134: RunTiming(-3.1728796239e-05, 1.64755689822e-06, 14, 0),
    354: RunTiming(0, 1.66190809094e-06, 7, 0),
    355: RunTiming(-0.000314315985828, 1.66190809094e-06, 2, 1),
    360: RunTiming(-0.000185791051023, 1.59938328397e-06, 5, 1),
    565: RunTiming(0.000473639852545, 1.87068995292e-06, 13, 1)

    

}


###############################
# Prepare Input
###############################

# Input branch-names:
# Event Numbers
br_n_pad = "n"
br_n_pixel = "ievent"

# Time
br_t_pad = "time_stamp" # [Unix Time]
br_t_pixel = "time"     # clock-ticks (25 ns spacing)

# Pixel only:
# - Hit plane bits 
br_hit_plane_bits_pixel = "hit_plane_bits"
# -Tracks
br_track_x = "track_x"
br_track_y = "track_y"

# Pad only:
# - Calibration flag
br_calib_flag_pad = "calibflag"
# - Integral50
br_integral50 = "Integral50"


###############################
# Prepare Output
###############################

if action == 0:
    test_string = ""
elif action == 1:
    test_string = "_short"
elif action == 2:
    test_string = "_align"
else:
    print "Invalid action: ", action
    print "Exiting"
    sys.exit()

try:
    os.mkdir("run_{0}".format(run))
except:
    pass

# Output ROOT File
filename_out = "run_{0}/track_info{1}.root".format(run, test_string)
f_out = ROOT.TFile(filename_out, "recreate")

# Output Tree
tree_out = ROOT.TTree("track_info", "track_info")

# Output branches
out_branches = {}

# Event Number (from pad)
out_branches["n_pad"] = array.array( 'i', [ 0 ] ) 
tree_out.Branch( 'n_pad', out_branches["n_pad"], 'n_pad/I' )

# Did we accept this event in the pixel+timing analysis
# Possible reasons for rejection:
#   - could not find event in the pixel stream
#   - event found in the pixel stream but time difference too large
#   - event matched but no track from pixels
out_branches["accepted"] = array.array( 'i', [ 0 ] )
tree_out.Branch( 'accepted', out_branches["accepted"], 'accepted/I' )

# Track interesect with pad
out_branches["track_x"] = array.array( 'f', [ 0. ] ) 
out_branches["track_y"] = array.array( 'f', [ 0. ] )
tree_out.Branch( 'track_x', out_branches["track_x"], 'track_x/F' )
tree_out.Branch( 'track_y', out_branches["track_y"], 'track_y/F' )

# Pad integral
out_branches["integral50"] = array.array( 'f', [ 0. ] ) 
tree_out.Branch( 'integral50', out_branches["integral50"], 'integral50/F' )


###############################
# Helper Function
# pixel_to_pad_time
###############################

def pixel_to_pad_time( pixel_now, pixel_0, pad_now, pad_0):
    
    # How many ticks have passed since first pixel time-stamp
    delta_pixel = pixel_now - pixel_0

    # Convert ticks to seconds (1 tick ~ 25 ns)            
    delta_second = delta_pixel * 25e-9 + di_runs[run].offset

    # Add time difference (in seconds) to initial pad time
    return pad_0 + delta_second +  di_runs[run].slope * (pad_now - pad_0)

# End of pixel-to-pad time conversion


###############################
# Get Trees
###############################

basedir_pad = "../../padreadout-devel/data/output/"
basedir_pixel = "../plots/"

if run < 10:
    format_pad = "{0}run_2014_09r00000{1}.root"
    format_pixel = "{0}00000{1}/histos.root"
elif run < 100:
    format_pad = "{0}run_2014_09r0000{1}.root"
    format_pixel = "{0}0000{1}/histos.root"
else:
    format_pad = "{0}run_2014_09r000{1}.root"
    format_pixel = "{0}000{1}/histos.root"

filename_pad = format_pad.format(basedir_pad, run)
filename_pixel = format_pixel.format(basedir_pixel, run)

f_pad = ROOT.TFile.Open(filename_pad)
f_pixel = ROOT.TFile.Open(filename_pixel)

print f_pad

tree_pad = f_pad.Get("rec")
tree_pixel = f_pixel.Get("time_tree")

print "Read:"
print "PAD Tree: ", tree_pad.GetEntries(), "entries"
print "Pixel Tree: ", tree_pixel.GetEntries(), "entries"


###############################
# Gather Information on Run
###############################

# Get the intial numbers for pad and pixel
tree_pad.GetEntry(0)
tree_pixel.GetEntry(0)

# Start with nominal (0/0) event align
# Try to find better pair of events below
initial_n_pad = getattr(tree_pad, br_n_pad)
initial_n_pixel = getattr(tree_pixel, br_n_pixel)

initial_t_pad = getattr(tree_pad, br_t_pad)
initial_t_pixel = getattr(tree_pixel, br_t_pixel)

print "Pad: Initial n = {0}, Initial t = {1}".format(initial_n_pad, initial_t_pad)
print "Pixel: Initial n = {0}, Initial t = {1}".format(initial_n_pixel, initial_t_pixel)

# Get the final numbers for pad and pixel
tree_pad.GetEntry(tree_pad.GetEntries()-1)
tree_pixel.GetEntry(tree_pixel.GetEntries()-1)

final_n_pad = getattr(tree_pad, br_n_pad)
final_n_pixel = getattr(tree_pixel, br_n_pixel)

final_t_pad = getattr(tree_pad, br_t_pad)
final_t_pixel = getattr(tree_pixel, br_t_pixel)

print "Pad: Final n = {0}, Final t = {1}".format(final_n_pad, final_t_pad)
print "Pixel: Final n = {0}, Final t = {1}".format(final_n_pixel, final_t_pixel)

print "Duration: {0} seconds".format(final_t_pad - initial_t_pad)


###############################
# Try to find two good events for aligning times
###############################

if action == 2:

    di_runs[run] = RunTiming()

    # We are going to select the alignment event with the lowest residual RMS
    # Make a list of triples: [pixel_event, pad_event, residual RMS]
    index_pixel = 0
    index_pad = 1
    index_rms = 2
    li_residuals_rms = []
    
    # Loop over potential pad events for aligning:
    for i_align_pad in xrange(max_align_pad):

        tree_pad.GetEntry(i_align_pad)
        initial_t_pad = getattr(tree_pad, br_t_pad)

        # Loop over potential pixel events for aligning:
        for i_align_pixel in xrange(max_align_pixel):

            tree_pixel.GetEntry(i_align_pixel)

            initial_t_pixel = getattr(tree_pixel, br_t_pixel)

            h = ROOT.TH1F("", "", 100, -0.005, 0.005)

            i_pixel = 0

            for i_pad in xrange(0, 1000):

                tree_pad.GetEntry(i_pad)
                time_pad = getattr(tree_pad, br_t_pad)

                delta_ts = []

                for i_pixel_test in range(i_pixel+1-10, i_pixel+1+10):        

                    if i_pixel_test < 0:
                        continue

                    tree_pixel.GetEntry(i_pixel_test)        
                    time_pixel = getattr(tree_pixel, br_t_pixel)

                    delta_ts.append( [i_pixel_test, pixel_to_pad_time(time_pixel, 
                                                                      initial_t_pixel, 
                                                                      time_pad, 
                                                                      initial_t_pad) - time_pad])

                best_match = sorted(delta_ts, key = lambda x:abs(x[1]))[0]
                h.Fill(best_match[1])

                # Set the starting-value for the next iteration 
                # Our basis assumption is no-missing event
                i_pixel = best_match[0] + 1
                # End of loop over pad events

            h.Draw()
            c.Print("run_{0}/ipad_{1}_ipixel_{2}.pdf".format(run, i_align_pad, i_align_pixel))

            print "Pad Event {0} / Pixel Event {1}: Mean: {2:2.6f} RMS:{3:2.6f}".format(i_align_pad, 
                                                                                        i_align_pixel, 
                                                                                        h.GetMean(), 
                                                                                        h.GetRMS())
            
            # Make sure we have enough events actually in the histogram
            if h.Integral() > 900:
                li_residuals_rms.append( [i_align_pixel, i_align_pad, h.GetRMS()] )

        # End of loop over pixel alignment events
    # End of loop over pad alignment events

    best_i_align_pixel = sorted(li_residuals_rms, key = lambda x: abs(x[index_rms]))[0][index_pixel]
    best_i_align_pad = sorted(li_residuals_rms, key = lambda x: abs(x[index_rms]))[0][index_pad]
    
    print "Best pad / pixel event for alignment: ", best_i_align_pad, best_i_align_pixel

    di_runs[run].align_pixel = best_i_align_pixel
    di_runs[run].align_pad = best_i_align_pad
    di_runs[run].print_info()

    sys.exit()

###############################
# Look at time drift
###############################

if action == 1:
    print "Doing Initial run - restricting events"
    max_events = min(25000, tree_pad.GetEntries()-1)

    # Update final-times for test analysis
    tree_pad.GetEntry(max_events)
    tree_pixel.GetEntry(max_events)        
    final_t_pad = getattr(tree_pad, br_t_pad)
    final_t_pixel = getattr(tree_pixel, br_t_pixel)

else:
    max_events = tree_pad.GetEntries()-1



h2 = ROOT.TH2D("", "", 2000, 0, final_t_pad-initial_t_pad, 300, -0.01, 0.01)
h = ROOT.TH1D("","",500, -0.007, 0.007)
h_delta_n = ROOT.TH1D("", "", 21, -10, 10)
h_calib_events = ROOT.TH2D("", "", 16, -0.5, 15.5, 2, -0.5, 1.5)
h_integral = ROOT.TH3D("","", 100, -0.4, 0.4, 100, -0.4, 0.4, 200, -1000, 1000)
h_tracks = ROOT.TH2D("","", 100, -0.4, 0.4, 100, -0.4, 0.4)

tree_pad.GetEntry(di_runs[run].align_pad)
tree_pixel.GetEntry(di_runs[run].align_pixel)

initial_t_pad = getattr(tree_pad, br_t_pad)
initial_t_pixel = getattr(tree_pixel, br_t_pixel)

i_pixel = 0

for i_pad in xrange(max_events):

    if i_pad % 1000 == 0:
        print "{0} / {1}".format(i_pad, max_events)

    tree_pad.GetEntry(i_pad)
    time_pad = getattr(tree_pad, br_t_pad)

    delta_ts = []
    for i_pixel_test in range(i_pixel-6, i_pixel+6):        

        if i_pixel_test < 0:
            continue

        tree_pixel.GetEntry(i_pixel_test)        
        time_pixel = getattr(tree_pixel, br_t_pixel)

        delta_ts.append( [i_pixel_test, pixel_to_pad_time(time_pixel, 
                                                          initial_t_pixel, 
                                                          time_pad, 
                                                          initial_t_pad) - time_pad])


    best_match =  sorted(delta_ts, key = lambda x:abs(x[1]))[0]

    i_pixel = best_match[0] 
    tree_pixel.GetEntry(i_pixel)        

    h_delta_n.Fill(best_match[0]-i_pixel+1)
    h.Fill(best_match[1])
    h2.Fill(time_pad-initial_t_pad, best_match[1])

    # Check if we are happy with the timing
    # (residual below 1 ms)
    if abs(best_match[1]) < 0.001:        
        hit_plane_bits = getattr(tree_pixel, br_hit_plane_bits_pixel)
        calib_flag = getattr(tree_pad, br_calib_flag_pad)
        h_calib_events.Fill(hit_plane_bits, calib_flag)

        out_branches["n_pad"][0] = getattr(tree_pad, br_n_pad)
        out_branches["accepted"][0] = 1
        out_branches["track_x"][0] = getattr(tree_pixel, br_track_x)
        out_branches["track_y"][0] = getattr(tree_pixel, br_track_y)
        out_branches["integral50"][0] = getattr(tree_pad, br_integral50)

        tree_out.Fill()            
        
        h_tracks.Fill(getattr(tree_pixel, br_track_x),
                      getattr(tree_pixel, br_track_y))
        
        h_integral.Fill(getattr(tree_pixel, br_track_x),
                        getattr(tree_pixel, br_track_y),
                        getattr(tree_pad, br_integral50))

    # done filling tree and calibration histogram

# End of loop over pad events



h.GetXaxis().SetTitle("t_{pixel} - t_{pad} [s]")
h.GetYaxis().SetTitle("Events")
h.Draw()
c.Print("run_{0}/residual{1}.pdf".format(run, test_string))

print h2,c
fun = ROOT.TF1("fun", "[0]+[1]*x")
h2.Fit(fun,"","")
h2.GetYaxis().SetTitleOffset(1.9)
h2.GetXaxis().SetTitle("t_{pad} [s]")
h2.GetYaxis().SetTitle("t_{pixel} - t_{pad} [s]")
h2.Draw()
c.Print("run_{0}/time{1}.pdf".format(run, test_string))

c.SetLogy(1)
h_delta_n.Draw()
c.Print("run_{0}/delta_n{1}.pdf".format(run, test_string))
c.SetLogy(0)


ROOT.gStyle.SetOptStat(0)
c.SetLogz(1)
h_calib_events.GetXaxis().SetTitle("Pixel Plane Hit Bit")
h_calib_events.GetYaxis().SetTitle("Pad Calibration Flag")
h_calib_events.GetYaxis().SetTitleOffset(1.5)
h_calib_events.Draw("COLZTEXT")
c.Print("run_{0}/calib_events{1}.pdf".format(run, test_string))

ROOT.gStyle.SetOptStat(0)
c.SetLogz(1)
h_tracks.GetXaxis().SetTitle("Pad position x [cm]")
h_tracks.GetYaxis().SetTitle("Pad position y [cm]")
h_tracks.GetYaxis().SetTitleOffset(1.5)
h_tracks.Draw("COLZ")
c.Print("run_{0}/tracks{1}.pdf".format(run, test_string))


ROOT.gStyle.SetOptStat(0)
c.SetLogz(0)
proj = h_integral.Project3DProfile("yx")
proj.SetTitle("")
proj.GetXaxis().SetTitle("Pad Position x [cm]")
proj.GetYaxis().SetTitle("Pad Position y [cm]")
proj.GetXaxis().SetTitleOffset(1.2)
proj.GetYaxis().SetTitleOffset(1.5)

proj.Draw("COLZ")
c.Print("run_{0}/integral{1}_fullrange.pdf".format(run, test_string))


proj.SetMinimum(100)
proj.SetMaximum(300)
proj.Draw("COLZ")
c.Print("run_{0}/integral{1}.pdf".format(run, test_string))


f_out.Write()

di_runs[run].offset -= fun.GetParameter(0)
di_runs[run].slope  -= fun.GetParameter(1)    
di_runs[run].print_info()

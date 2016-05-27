#ifndef GUARD_PLTTracking_h
#define GUARD_PLTTracking_h

#include <vector>
#include <iostream>
#include <set>
#include <math.h>


#include "PLTTelescope.h"
#include "PLTAlignment.h"
#include "PLTU.h"
#include "PLTMask.h"


class PLTTracking
{
  public:
    enum TrackingAlgorithm {
      kTrackingAlgorithm_NoTracking = 0,
      kTrackingAlgorithm_01to2_All,
      kTrackingAlgorithm_01to2_AllCombs,
      kTrackingAlgorithm_2PlaneTracks_All
    };

    PLTTracking ();
    PLTTracking (PLTAlignment*, TrackingAlgorithm const);
    ~PLTTracking ();

    void SetTrackingAlignment (PLTAlignment*);
    void SetTrackingAlgorithm (TrackingAlgorithm const);
    int  GetTrackingAlgorithm ();
    static bool CompareTrackD2 (PLTTrack*, PLTTrack*);


    void RunTracking (PLTTelescope&);

    void TrackFinder_01to2_All (PLTTelescope&);
    void SortOutTracksNoOverlapBestD2(std::vector<PLTTrack*>&);


  private:
    PLTAlignment* fAlignment;
    TrackingAlgorithm fTrackingAlgorithm;
    // Added Mask
    PLTMask* fMask;

    static bool const DEBUG = false;
};



#endif


#!/bin/bash

#expects BAND in $1
#should be run from the root data folder 
#(containing $BAND subfolder)
process_band() {
	local BAND=$1
	cd $BAND
	mkdir -p projected
	mImgtbl raw rimages.tbl
	mProjExec -p raw rimages.tbl ../pleiades.hdr projected stats.tbl
	mImgtbl projected pimages.tbl
	mAdd -p projected pimages.tbl ../pleiades.hdr $BAND.fits
	cd ..
}

#updating $PATH to contain Montage binaries
export PATH=$PATH:`readlink -f ../bin`

for BAND in DSS2B DSS2R DSS2IR
do 
	echo "Processing $BAND"
	process_band $BAND
done

echo "Bands processed. Starting image generation"
mJPEG -blue DSS2B/DSS2B.fits -1s 99.999% gaussian-log \
		-green DSS2R/DSS2R.fits -1s 99.999% gaussian-log \
		-red DSS2IR/DSS2IR.fits -1s 99.999% gaussian-log \
		-out DSS2_BRIR_sync.jpg


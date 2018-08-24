#!/usr/bin/perl

#usage: ./modify_pathline.pl 


$inFile = "test_1.mppth";
$outFile = "test.pathline_out";

open(OUT,">$outFile") || die "cannot open $outFile\n";
open(IN,"<$inFile") || die "cannot open $inFile\n";

$header1 = <IN>;
$header2 = <IN>;
$header3 = <IN>;

print OUT "@ [ MODPATH 6.0 (TREF=   0.000000E+00 ) ] \n";

while (<IN>) {


$ParticleID	= substr($_,0,10);	#1
$ParticleGroup	= substr($_,10,6);	#2
$TimePointIndex	= substr($_,16,6);	#3
$CumTimeStep	= substr($_,22,6);	#4
$TrackingTime	= substr($_,28,24);	#5
$GlobalX	= substr($_,52,24);	#6
$GlobalY	= substr($_,76,24);	#7
$GlobalZ	= substr($_,100,24);	#8
$Layer		= substr($_,124,5);	#9
$Row		= substr($_,129,5);	#10
$Column		= substr($_,134,5);	#11
$Grid		= substr($_,139,3);	#12
$LocalX		= substr($_,142,15);	#13
$LocalY		= substr($_,157,16);	#14
$LocalZ		= substr($_,173,16);	#15
$LineSegIndex	= substr($_,189,6);	#16


print OUT "         $ParticleID";
print OUT "    $GlobalX";
print OUT "    $GlobalY";
print OUT "    $LocalZ";
print OUT "    $GlobalZ";
print OUT "    $TrackingTime";
print OUT "    $Row";
print OUT "    $Column";
print OUT "    $Layer";
print OUT "    $CumTimeStep\n";
	
}


close IN;
close OUT;


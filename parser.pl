#!/usr/bin/perl

use strict;

sub parse_score
{
	$_ = unshift @_;
	my $score = {	data	=>	$_};

	if (/^\s*(\d+)(=?)\s+(\D*)\s+(-?\d+)(\s+\d+x)?((\s+(Bronze|Silver|Gold))?)\s*$/) {

		$score->{type}	= "standard";
		$score->{position} = $1;
		$score->{joint}	= $2 eq "=";
		$score->{name}	= $3;
		$score->{score}	= $4;
		$score->{nox}	= $5;
		$score->{medal}	= $6;

	}
	else {
		$score->{type} = "unknown";
	};
	
	return $score;
}

print "<html><head><link rel='stylesheet' type='text/css' href='scorestyle.css' /></head><body><table>";

my $i=0;
my $lastline;
my $competitions = [];
my $state = "between competitions";

my $competition = {
	scores => []
};


foreach (<STDIN>) {
	$i++;
	my $line = $_;
	my $oldstate = $state;
		
	if ($state eq "reading scores") {
		if (/^\s+$/) {
			push @$competitions, $competition;
			$state = "between competitions";
			$competition = {scores => []};
		}
		else {
			push @{$competition->{scores}}, parse_score($_);
		}
	}
	elsif($state eq "between competitions") {
		if (/^\s*(\d+) Entries\s*$/) {
			$competition->{entries} = $1;
			$state = "awaiting header";
		}
		elsif (/^\s*No Entries\s*$/) {
			$competition->{entries} = 0;
			push @$competitions, $competition;
			$competition = {scores => []};
		}
		else {
			$competition->{name} = $_;
		}
	}
	elsif($state eq "awaiting header") {
		if (/\t/) {
			$state = "reading scores"
		}
		else {
			print STDERR "line ", $i, ": Expected table header.  Got '", $_, "' instead!\n";
			$state = "between competitions";
		}
	}
	else {
		print STDERR "line ", $i, ": unexpected state '", $state, "'\n"
	}
	
	$lastline = $_;
	
	print "<tr class='$oldstate'><td>$i</td><td>$oldstate</td><td>", $line, "</td></tr>\n";
};

print "</table></body></html>";

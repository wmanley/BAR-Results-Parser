#!/usr/bin/perl

use strict;
use Data::Dumper;

sub trim($)
{
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
}

sub parse_score
{
	$_ = @_[0];
	my $score = {	data	=>	$_};

	if (/^\s*(\d+)(=?)\s+(\D*)\s+(-?\d+)(\s+\d+x)?((\s+(Bronze|Silver|Gold))?)\s*$/) {

		$score->{type}	= "standard";
		$score->{position} = trim($1);
		$score->{joint}	= $2 eq "=";
		$score->{name}	= trim($3);
		$score->{score}	= trim($4);
		$score->{nox}	= trim($5);
		$score->{medal}	= trim($6);

		$score->{nox} =~ s/x//;
	}
	else {
		$score->{type} = "unknown";
	};
	
	return $score;
}

sub print_scores
{
	my $competitions = @_[0];
	
	my $comp;
	foreach $comp (@$competitions) {
		print "<h2>", $comp->{name}, "</h2>";
		if ($comp->{entries} == 0) {
			print "<p class='entries'>No Entries</p>";
			next;
		}
		
		print "<p class='entries'>", $comp->{entries}, " Entries</p>";
		
		print "<table>";
		print "<tr><td>Position</td><td>Name</td><td colspan='2'>Score</td><td>Prize</td></tr>";
		
		my $score;
		foreach $score (@{$comp->{scores}}) {
			if ($score->{type} eq "unknown") {
				print "<tr class='unknown'><td colspan='5'>UNKNOWN: ", $score->{data}, "</td></tr>";
				next;
				
			}
			print "<tr class='", $score->{medal}, "'>";
			print "<td>", $score->{position}, $score->{joint} ? "=" : "", "</td>";			
			print "<td>", $score->{name}, "</td>";
			print "<td>", $score->{score}, "</td>";
			print "<td>", defined($score->{nox}) ? $score->{nox}."x" : "", "</td>";
			print "<td>", $score->{medal}, "</td>";
			print "</tr>";
		}
	}
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
			push @{$competition->{scores}}, parse_score($line);
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

print "</table>";
print_scores($competitions);
print "</body></html>";

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
	my $score = {	data	=>	trim($_)};

	if (/^\s*(\d+)(=?)\s+(\D*)\s+(-?\d+\.?\d*|No score)(\s+\d+x)?((\s+(Bronze|Silver|Gold))?)\s*$/) {

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

sub print_bar_graph
{
	my ($score, $minscore, $maxscore) = @_;
	my $barwidth = 300;
	
	if ($minscore > $maxscore) {
		my $a = $maxscore;
		$maxscore = $minscore;
		$minscore = $a;
	}
	
	if ($minscore > 0) {
		$minscore = 0;
	}
	
	if ($maxscore < 0) {
		$maxscore = 0;
	}
	
	my $m = $barwidth / ($maxscore - $minscore);
	my $c = $m * -$minscore;
	
	if ($score > 0) {
		print "<td class='neg'></td><td class='pos'><div style='width:", $m*$score, "px'> </div></td>";
	}
	else {
		print "<td class='neg'><div style='width:", -$m*$score, "px'> </div></td><td class='pos'></td>";
	}
}

sub print_competition
{
	my $comp = @_[0];
	
	print "<h2>", $comp->{name}, "</h2>";
	my @s = @{$comp->{scores}};
	if ($comp->{entries} == 0) {
		print "<p class='entries'>No Entries</p>";
		return;
	}
	
	print "<p class='entries'>", $comp->{entries}, " Entries</p>";
	
	print "<table>";
	print "<tr><td>Position</td><td>Name</td><td colspan='2'>Score</td><td>Prize</td></tr>";
	foreach my $score (@s) {
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
		print_bar_graph($score->{score}, $comp->{minscore}, $comp->{maxscore});
		print "</tr>\n";
	}
	print "</table>";
}

sub print_scores
{
	my $competitions = @_[0];
	
	my $comp;
	foreach $comp (@$competitions) {
		print_competition($comp);
	}
}

# Extracts information about competitions by looking at the results
sub prepare_competitions
{
	my $competitions = @_[0];
	my $comp;
	foreach $comp (@$competitions) {
		if (scalar @{$comp->{scores}} == 0) {
			next;
		}

		$comp->{type} = $comp->{scores}->[0]->{type};		
		$comp->{maxscore} = $comp->{scores}->[0]->{score};
		$comp->{minscore} = $comp->{scores}->[(scalar @{$comp->{scores}}) - 1]->{score};		

		# This is required if the last score is "No Score"
		foreach (@{$comp->{scores}}) {
			if ($_->{score} > $comp->{maxscore}) {
				$comp->{maxscore} = $_->{score};
			}
		}
	}
}

sub parse
{
	my $input = shift;
	my $i=0;
	my $lastline;
	my $competitions = [];
	my $state = "between competitions";

	my $competition = {
		scores => []
	};


	foreach (<$input>) {
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
				$competition->{name} = trim($_);
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
	};
	return $competitions;
}

sub main
{
	print "<html><head><link rel='stylesheet' type='text/css' href='scorestyle.css' /></head><body>";
	my $competitions = parse(\*STDIN);
	prepare_competitions($competitions);
	print_scores($competitions);
	print "</body></html>";
};

main();

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
		$score->{name}	= [trim($3)];
		$score->{score}	= trim($4);
		$score->{nox}	= trim($5);
		$score->{medal}	= trim($6);

		$score->{nox} =~ s/x//;
	}
	elsif (/^(\d+)(=?)\s+(\D*)\s+((\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-)\s*\/\s*(\d+|-))\s*\/\s*(\d+)((\s+(Bronze|Silver|Gold))?)$/) {
		$score->{type}	= "aggregate";
		$score->{position} = trim($1);
		$score->{joint}	= $2 eq "=";
		$score->{name}	= [trim($3)];
		$score->{components}	= trim($4);
		$score->{score}	= trim($5);
		$score->{medal}	= trim($6);

		$score->{components} =~ s/\//\+/g;
	}
	elsif (/^(\d+)(=?)\s+(\D+)\s*\((-?\d+)\)\s+\&\s+(\D+)\s+\((-?\d+)\)\s*(-?\d+)((\s+(Bronze|Silver|Gold))?)$/) {
		$score->{type}	= "doubles";
		$score->{position} = trim($1);
		$score->{joint}	= $2 eq "=";
		$score->{name}	= [trim($3), trim($5)];
		$score->{scores}	= [trim($4), trim($6)];
		$score->{score}	= trim($7);
		$score->{medal}	= trim($8);

		$score->{components} =~ s/\//\+/g;
	}
	elsif (/^(\d+)(=?)\s+(\D*)$/) {
		$score->{type}	= "manvman";
		$score->{position} = trim($1);
		$score->{joint}	= $2 eq "=";
		my $name = trim($3);
		if ($name =~ /(Bronze|Silver|Gold)$/) {
			$score->{medal} = $1;
			$name =~ s/\s+(Bronze|Silver|Gold)$//;
		}
		$score->{name}	= [$name];
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
		
		print "<tr onClick='javascript:ClickedThis(this)' class='", $score->{medal}, "'>";
		print "<td>", $score->{position}, $score->{joint} ? "=" : "", "</td>";			
		
		if ($score->{type} eq "doubles") {
			print "<td>", $score->{name}->[0], " </td>";
			print "<td> ", $score->{scores}->[0], " + ";
			print $score->{scores}->[1], " </td>";
			print "<td> ", $score->{name}->[1], "</td>";
		}
		else {
			print "<td>", $score->{name}->[0], "</td>";
		}
		if ($score->{type} eq "aggregate") {
			print "<td>", $score->{components}, " = </td>";
		}
		print "<td>", $score->{score}, "</td>";
		print "<td>", defined($score->{nox}) ? $score->{nox}."x" : "", "</td>";
		print "<td>", $score->{medal}, "</td>";
		if ($score->{type} ne "manvman") {
			print_bar_graph($score->{score}, $comp->{minscore}, $comp->{maxscore});
		}
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

sub print_file
{
	my $filename = shift;
	open FILE, $filename or die $!;
	
	foreach (<FILE>) {
		print;
	}
}

sub analyse_people
{
	my $competitions = shift;
	my $people = {};
	
	foreach my $comp (@$competitions) {
		foreach my $score (@{$comp->{scores}}) {
			if ($score->{type} eq "unknown") {
				next;
			}
			foreach my $name (@{$score->{name}}) {
				$people->{$name}->{entries}++;
				if ($score->{medal} eq "Gold") {
		 			$people->{$name}->{golds}++;
				}
				if ($score->{medal} eq "Silver") {
		 			$people->{$name}->{silvers}++;
				}
				if ($score->{medal} eq "Bronze") {
		 			$people->{$name}->{bronzes}++;
				}
			}
		}
	}
	return $people;
}

sub print_people
{
	my $people = shift;
	print "<table class='sortable'><tr><th>Name</th><th>Entries</th><th>Golds</th><th>Silvers</th><th>Bronzes</th><th>Biggest Rival</th></tr>";
	while (my ($name, $value) = each(%$people)) {
		print "<tr><td>", $name, "</td><td>", $value->{entries}, 
			"</td><td>", $value->{golds}, 
			"</td><td>", $value->{silvers}, 
			"</td><td>", $value->{bronzes}, 
			"</td><td>", $value->{rival}, " (", $value->{rival_diff}, "/", $value->{rival_matches}, ")</td></tr>\n";
	}
	print "</table>";
}

sub analyse_enemies
{
	my $competitions = shift;
	my %people;
	
	# We do this so $people{will}->{steve} will equal the number of times
	# will has beaten steve
	foreach my $comp (@$competitions) {
		my @winners;
		foreach my $score (@{$comp->{scores}}) {
			if ($score->{type} eq "unknown") {
				next;
			}
			foreach (@winners) {
				foreach my $name ( @{$score->{name}} ) {
					$people{$_}->{$name}++;
				}
			}
			push @winners, @{$score->{name}};
		}
	}
	return \%people;
}

sub print_big_enemies_table
{
	my $enemies = shift;
	my $people = shift;
	my @winners = sort { $people->{$b}->{entries} <=> $people->{$a}->{entries} } keys %$people; 
	
	print "<table><tr><td></td>";
	foreach my $winner (@winners) {
		print "<th>$winner</th>";
	}
	print "</tr>";
	foreach my $winner (@winners) {
		print "<tr>";
		print "<th>$winner</th>";
		foreach my $loser (@winners) {
			my $won = $enemies->{$winner}->{$loser};
			my $lost = $enemies->{$loser}->{$winner};
			if (($won + $lost) == 0) {
				print "<td></td>";
				next;
			}
			if ($won > $lost) {
				print "<td class='pos'>+";
			}
			elsif ($lost > $won) {
				print "<td class='neg'>";
			}
			else {
				print "<td>";
			}
			print $won-$lost, "/", $won+$lost, "</td>";
		};
		print "</tr>";
	}
	print "</table>";
}

sub analyse_rivalries
{
	my $enemies = shift;
	my $people = shift;
	
	my @peoples_names = keys %$people;
	
	my %rivalries;
	
	foreach my $winner (@peoples_names) {
		foreach my $loser (@peoples_names) {
			my $won = $enemies->{$winner}->{$loser};
			my $lost = $enemies->{$loser}->{$winner};
			
			if (($won + $lost) > 0) {
				$rivalries{$winner}->{$loser} = abs(($won-$lost)/($won+$lost)) - log($won+$lost)/5;
			};
		};
		my @rivals = sort { $rivalries{$winner}->{$a} <=> $rivalries{$winner}->{$b} } keys %{$rivalries{$winner}};
		$people->{$winner}->{rival} = $rivals[0];
		$people->{$winner}->{rival_matches} = $enemies->{$rivals[0]}->{$winner} + $enemies->{$winner}->{$rivals[0]};
		$people->{$winner}->{rival_diff} = $enemies->{$rivals[0]}->{$winner} - $enemies->{$winner}->{$rivals[0]};
	}
}

sub get_full_name
{
	my $people = shift;
	my $initial = shift;
	my $surname = shift;
	
	my @poss;
	foreach (keys %$people) {
		if (/^($initial)\S+\s+($surname)$/) {
			push @poss, $_;
		}
	}
	if ((scalar @poss) > 1) {
		print STDERR "Warning: More than one match for abbreviation '$initial $surname'\n";
		return $initial . " " . $surname;
	}
	elsif ((scalar @poss) < 1) {
		print STDERR "Warning: No match for abbreviation '$initial $surname'\n";
		return $initial . " " . $surname;
	}
	else {
		return @poss[0];
	}
}

sub get_abbreviation_map
{
	my $people = shift;
	my %abbrmap;
	
	foreach (keys %$people) {
		if (/^(\S)\s+(.*)$/) {
			$abbrmap{$_} = get_full_name($people, $1, $2);
		}
	}
	return \%abbrmap;
}

sub fix_abbreviations_in_entries
{
	my $competitions = shift;
	my $abbrmap = shift;
	
	foreach my $comp (@$competitions) {
		foreach my $score (@{$comp->{scores}}) {
			if ($score->{type} eq "unknown") {
				next;
			}
			my $i=0;
			foreach my $name (@{$score->{name}}) {
				if (defined $abbrmap->{$name}) {
					$score->{name}->[$i] = $abbrmap->{$name};
				}
				$i++;
			}
		}
	}
}

sub main
{
	print_file("header.html");
	
	my $competitions = parse(\*STDIN);
	prepare_competitions($competitions);
	
	my $people = analyse_people($competitions);
	
	my $abbrmap = get_abbreviation_map($people);
	fix_abbreviations_in_entries($competitions, $abbrmap);
	
	$people = analyse_people($competitions);
	
	my $enemies = analyse_enemies($competitions);
	analyse_rivalries($enemies, $people);

	print_scores($competitions);
	print_people($people);
	print_big_enemies_table($enemies, $people);
		
	print "</body></html>";
};

main();

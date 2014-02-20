#! /usr/bin/perl -w

use strict;
use CGI;

print "Content-Type: text/html\n\n";

my %leagueTable;

my %players;

my $query = CGI::new();

my $player1 = $query->param('redplayer');
my $player2 = $query->param('blueplayer');
my $player1score = $query->param('redscore');
my $player2score = $query->param('bluescore');

if($player1 !~ /^\D+$/) {
    print "<html><head><title>Table Football League</title></head>";
    print "<body><h1>Incorrect submission</h1>";
    print "<p>Incorrect name for red player.</p></body>";
    print "</html>\n";
}
elsif($player2 !~ /^\D+$/) {
    print "<html><head><title>Table Football League</title></head>";
    print "<body><h1>Incorrect submission</h1>";
    print "<p>Incorrect name for blue player.</p></body>";
    print "</html>\n";
}
elsif($player1score !~ /^\d+$/) {
    print "<html><head><title>Table Football League</title></head>";
    print "<body><h1>Incorrect submission</h1>";
    print "<p>Incorrect score for red player.</p></body>";
    print "</html>\n";
}
elsif($player2score !~ /^\d+$/) {
    print "<html><head><title>Table Football League</title></head>";
    print "<body><h1>Incorrect submission</h1>";
    print "<p>Incorrect score for blue player.</p></body>";
    print "</html>\n";
}
else {

    my %exclude;
    my $rewrite = 0;
    open(FILE, "ladderExclude");
    while(<FILE>) {
        chomp;
        if(/^(\D+)$/) {
            if($1 eq $player1 or $1 eq $player2) {
                $rewrite = 1;
            }
            else {
                $exclude{$1} = 1;
            }
        }
    }
    close(FILE);
    
    if($rewrite) {
        open(FILE, ">ladderExclude");
        foreach(sort keys %exclude) {
            print FILE "$_\n";
        }
        close(FILE);
    }

    open(FILE, ">>ladder.txt");
    print FILE "\n$player1 $player1score $player2 $player2score " . time();
    close(FILE);
    
    print "<html><head><meta http-equiv=\"refresh\" content=\"0;URL=football.cgi?justPlayed=$player1&amp;justPlayed=$player2\"/></head></html>\n";
}



#!/usr/bin/perl -w
# Filename : password_checker.pl

use strict;
use Socket;

# Write a Perl function that takes in a password and checks whether it's valid.  The password should follow the following rule:
# Passwords must be at least 8 characters long.
# Between 8-11: requires mixed case letters, numbers and symbols
# Between 12-15: requires mixed case letters and numbers
# Between 16-19: requires mixed case letters
# 20+: any characters desired

sub pwdChk {
    my ($pwd) = @_;
    my $len = length($pwd);
    if ( $len < 8 ) {
        return 0;
    }
    elsif ( $len < 20 ) {
        unless ( $pwd =~ /(?=.*[a-z])(?=.*[A-Z])/ ) {

            # requires mixed case letters
            return 0;
        }

        if ( $len < 16 ) {
            unless ( $pwd =~ /(?=.*\d)/ ) {

                # and requires numbers
                return 0;
            }

            if ( $len < 12 ) {
                unless ( $pwd =~ /(?=.*[^a-zA-Z0-9])/ ) {

                    # and requires symbols
                    return 0;
                }
            }
        }
    }
    return 1;
}



# below is just for test
$pwd = "jd#Kd&1";
print "Input: $pwd\n";
print "output: ", pwdChk($pwd), " (length = ", length($pwd), ")\n";

$pwd = "jdfKd&1a";
print "Input: $pwd\n";
print "output: ", pwdChk($pwd), " (length = ", length($pwd), ")\n";

$pwd = "jdfKd&ca";
print "Input: $pwd\n";
print "output: ", pwdChk($pwd), " (length = ", length($pwd), ")\n";

$pwd = "jdfKd81a";
print "Input: $pwd\n";
print "output: ", pwdChk($pwd), " (length = ", length($pwd), ")\n";

$pwd = "jdfkd&1a";
print "Input: $pwd\n";
print "output: ", pwdChk($pwd), " (length = ", length($pwd), ")\n";

$pwd = "jdfKd31abcde";
print "Input: $pwd\n";
print "output: ", pwdChk($pwd), " (length = ", length($pwd), ")\n";

$pwd = "jdfKdabcdebcdefgh";
print "Input: $pwd\n";
print "output: ", pwdChk($pwd), " (length = ", length($pwd), ")\n";

$pwd = "aaaaaaasdfdsfsdfsdfsdafsdafsdfsdafsaffdsfdsfdsfsad";
print "Input: $pwd\n";
print "output: ", pwdChk($pwd), " (length = ", length($pwd), ")\n";
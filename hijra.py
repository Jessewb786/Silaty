#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hijri Islamic Calendar converting functions,
Copyright (c) 2006-2008 Muayyad Saleh Alsadi<alsadi@gmail.com>
Based on an enhanced algorithm designed by me
the algorithm is discussed in a book titled "حتى لا ندخل جحور الضباب"
(not yet published)

This file can be used to implement apps, gdesklets or karamba ..etc

This algorithm is based on integer operations
which that there is no round errors (given accurate coefficients)
the accuracy of this algorithm is based on 3 constants (p,q and a)
where p/q is the full months percentage [ gcd(p,q) must be 1 ]
currently it's set to 191/360 which mean that there is 191 months
having 30 days in a span of 360 years, other months are 29 days.
and a is just a shift.


    Released under terms on Waqf Public License.
    This program is free software; you can redistribute it and/or modify
    it under the terms of the latest version Waqf Public License as
    published by Ojuba.org.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    The Latest version of the license can be found on
    "http://www.ojuba.org/wiki/doku.php/waqf/license"


Portions of this algorithm is based on that found on GNU EMACS
the difference is that this algorithm does not set
all months to a fixed number of days (in the original algorithm
first month always have 30 days)


The original GNU Emacs LISP algorithm
Copyright (C) 1995, 1997, 2001 Free Software Foundation, Inc.
    Edward M. Reingold <reingold@cs.uiuc.edu>
  Technical details of all the calendrical calculations can be found in
  ``Calendrical Calculations'' by Nachum Dershowitz and Edward M. Reingold,
  Cambridge University Press (1997).
  Comments, corrections, and improvements should be sent to
   Edward M. Reingold               Department of Computer Science
   (217) 333-6733                   University of Illinois at Urbana-Champaign
   reingold@cs.uiuc.edu             1304 West Springfield Avenue
"""
__p_const=191
__q_const=360
__a_const=48
__hijri_epoch=227015 # = Julian 0622-7-16 = gregorian 0759-6-11 (I think it should be 622, 7, 19)
# TODO: Why does the the hijri_epoch 227015 does not give the expected value when converted to gregorian

def get_consts():
   """Return a tuple of the 3 constants (p,q,a) used by this algothim, for debuging"""
   return (__p_const, __q_const, __a_const)

def get_epoch():
   """Return Hijri epoch, number of days since gregorian epoch, (should be Julian 0622-7-16 (ie. 227015 days)"""
   return __hijri_epoch

def hijri_month_days(Y,M):
   """Return the number of days in a given hijri month M in a given Y"""
   Mc = ( Y -1) *12 + M
   if (((Mc+ __a_const) * __p_const) % __q_const)  < __p_const : return 30
   else: return 29

# NOTE: trivial implementation
#def hijri_days_before_month_(Y,M): # simple mothod, optimization is possible by reusing Mc ..etc.
#   """Return the number of days before a given moth M in a given year Y"""
#   sum=0
#   for i in range(1,M): sum+=hijri_month_days(Y,i);
#   return sum

def hijri_days_before_month(Y,M):
   """Return the number of days before a given moth M in a given year Y (0 for M=1)"""
   Mc = (Y -1) *12 + 1 + __a_const
   McM=Mc * __p_const
   sum=0
   for i in range(1,M):
      if (McM % __q_const)  < __p_const : sum+=30
      else: sum+=29
      McM+=__p_const
   return sum

#TEST: PASSED
# test that the faster hijri_days_before_month is ok
#def test_hijri_days_before_month():
#  l=[(y,m) for y in range(1400,1499) for m in range(1,13)]
#  for y,m in l:
#    d1=hijri_days_before_month(y,m)
#    d2=hijri_days_before_month_(y,m)
#    if d1!=d2: print y,m,d1,d2


def hijri_year_days(Y):
   """Return the number of days in a given year Y"""
   return hijri_days_before_month(Y,13)

def hijri_day_number (Y, M, D):
   """Return the day number within the year of the Islamic date (Y, M, D), 1 for 1/1 in any year"""
   return hijri_days_before_month(Y,M)+D


# BAD fast implementation
#def hijri_to_absolute_ (Y, M, D):
#   """Return absolute date of Hijri (Y,M,D), eg. ramadan (9),1,1427 -> 732578 """
#   Mc=(Y-1)*12
#   # days before Hijra +  days in the years before + days from the begining of that year
#   return __hijri_epoch + \
#      Mc*29 + Mc*__p_const/__q_const + \ # this line should involve __a_const
#      hijri_day_number (Y, M, D) - 1

# correct implementation # TODO: optimize it more and test that after optimization
def hijri_to_absolute (Y, M, D):
   """Return absolute date of Hijri (Y,M,D), eg. ramadan (9),1,1427 -> 732578 """
   Mc=(Y-1)*12
   # day count=days before Hijra plus (...)
   dc=__hijri_epoch
   # plus days in the years before till first multiples of q plus (...)
   Mc-=Mc % __q_const
   y=Y-Mc//12
   dc+=Mc*29 + Mc*__p_const//__q_const
   # plus those after the multiples plus (...)
   for i in range(1,y): dc += hijri_year_days(i)
   # plus days from the begining of that year
   dc+=hijri_day_number (Y, M, D) - 1
   return dc

def hijri_month_days_(y,m):
   """Return the number of days in a given hijri month M in a given Y"""
   return hijri_to_absolute(y+m//12,m%12+1,1)-hijri_to_absolute(y,m,1)

# TEST: PASSED
#def test_hijri_to_absolute_v_month_days():
#  #l=[(y,m) for y in range(1,31) for m in range(1,13)]
#  l=[(y,m) for y in range(1400,1499) for m in range(1,13)]
#  for y,m in l:
#    d1=hijri_month_days(y,m)
#    d2=hijri_to_absolute(y+m/12,m%12+1,1)-hijri_to_absolute(y,m,1)
#    if d1!=d2: print y,m,y+m/12,m%12+1,'d1=',d1,", d2=",d2

# round then move to exact, very slow perfect implementation
#def absolute_to_hijri_ (date): # TODO: check if it's always compatible with absolute_from_hijri
#   """Return Hijri date (Y,M,D) corresponding to the given absolute number of days."""
#   if date < __hijri_epoch: return None; # pre-Islamic date
#   dd=date-__hijri_epoch
#   Mc=dd/(29*(__q_const-__p_const)+ 30*__p_const)*__q_const # mounth count till multibles of q
#   Y=y=Mc/12+1; M=m=(Mc%12)+1
#   while(date > hijri_to_absolute(Y,M,1)):
#     y,m=Y,M
#     M+=1
#     if M>12: M=1; Y+=1
#   Y=y; M=m
#   D=1 + date - hijri_to_absolute(Y,M,1)
#   if D>hijri_month_days(Y,M):
#     M+=1
#     if M>12: M=1; Y+=1
#   D=1 + date - hijri_to_absolute(Y,M,1)
#   return (Y,M,D)


# direct way, test PASSED
def absolute_to_hijri (date):
   """Return Hijri date (Y,M,D) corresponding to the given absolute number of days."""
   if date < __hijri_epoch: return None; # pre-Islamic date
   Mc=(date-__hijri_epoch+1)*__q_const//(29*__q_const+__p_const)
   Y=Mc//12+1; M=(Mc%12)+1
   # consistency check
   d=hijri_to_absolute(Y,M,1) # TODO: this is an expensive call
   if (date < d): # go one month back if needed
     M-=1
     if M==0: Y-=1; M=12
     d-=hijri_month_days(Y,M) # this call is fast
   #
   D=1 + date - d
   return (Y,M,D)

# TEST: PASSED
#def test_c():
#  l=[(y,m) for y in range(1400,1499) for m in range(1,13)]
#  for y,m in l:
#    d=hijri_month_days(y,m)
#    if absolute_to_hijri(hijri_to_absolute(y,m,1))!=(y,m,1): print y,m,1, absolute_to_hijri(hijri_to_absolute(y,m,1))
#    if absolute_to_hijri(hijri_to_absolute(y,m,d))!=(y,m,d): print y,m,d, absolute_to_hijri(hijri_to_absolute(y,m,d))

def hijri_day_of_week (Y, M, D):
   """Return the day-of-the-week index of hijri (Y,M,D) Date, 0 for Sunday, 1 for Monday, etc."""
   return hijri_to_absolute (Y,M, D) % 7
# ///////////////////////////////
# high level converting functions

def hijri_to_gregorian (year, month, day):
   """Return gregorian (year, month, day) converted from Islamic Hijri calender"""
   return absolute_to_gregorian( hijri_to_absolute (year, month, day))

def gregorian_to_hijri (year, month, day):
   """Return Hijri  (year, month, day) converted from gregorian calender"""
   return absolute_to_hijri( gregorian_to_absolute (year, month, day))

#///////////////////////////////////
# Gregorian functions
#///////////////////////////////////
# This Portions of is based on that found on GNU EMACS

#The original GNU Emacs LISP algorithm
#Copyright (C) 1995, 1997, 2001 Free Software Foundation, Inc.
# Edward M. Reingold <reingold@cs.uiuc.edu>
#  Technical details of all the calendrical calculations can be found in
#  ``Calendrical Calculations'' by Nachum Dershowitz and Edward M. Reingold,
#  Cambridge University Press (1997).
#  Comments, corrections, and improvements should be sent to
#  Edward M. Reingold               Department of Computer Science
#  (217) 333-6733                   University of Illinois at Urbana-Champaign
#  reingold@cs.uiuc.edu             1304 West Springfield Avenue

days_in_month=( 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
def gregorian_leap_year_p (year):
   """Return 1 (True) if YEAR is a Gregorian leap year."""
   if ((year % 4) == 0 and ((year % 100) or (year % 400) == 0)): return 1;
   return 0;

def gregorian_month_days (year, month):
   """The last day in MONTH during YEAR."""
   if (month == 2 and gregorian_leap_year_p (year)): return 29;
   return days_in_month[month-1];

def gregorian_day_number (year, month, day):
   """Return the day number within the year of the date (year,month, day)"""
   if month<3: return day + (31 * (month - 1))
   return day + (31 * (month - 1)) - \
   ((month << 2) + 23) // 10 + (gregorian_leap_year_p (year) & 1);

def gregorian_to_absolute (year, month, day):
   prior_years = year - 1
   return gregorian_day_number (year, month, day) + \
   (365 * prior_years + (prior_years >> 2)) - \
   (prior_years // 100) + (prior_years // 400)

def absolute_to_gregorian(date):
   """return (year month day) corresponding to the absolute DATE.
The absolute date is the number of days elapsed since the (imaginary)
Gregorian date Sunday, December 31, 1 BC."""

# See the footnote on page 384 of ``Calendrical Calculations, Part II:
# Three Historical Calendars'' by E. M. Reingold,  N. Dershowitz, and S. M.
# Clamen, Software--Practice and Experience, Volume 23, Number 4
# (April, 1993), pages 383-404 for an explanation.
   d0 = date - 1;
   n400 = d0 // 146097;
   d1 = d0 % 146097;
   n100 = d1 // 36524;
   d2 = d1 % 36524;
   n4 = d2 // 1461;
   d3 = d2 % 1461;
   n1 = d3 // 365;
   dd = (d3 % 365) + 1;
   yy = ((400 * n400) + (100 * n100) + (n4 * 4) + n1);
   if (n100 == 4) or (n1 == 4): return (yy, 12, 31);
   yy=yy+1;
   mm = 1;
   while(date >= gregorian_to_absolute (yy,mm, 1)): mm+=1;
   d=gregorian_to_absolute (yy, mm-1, 1);
   return (yy, mm-1,date-d+1);
#   d = calendar_absolute_from_gregorian (1, 1, yy);
#   mm=1;
#   while(mm <= 12):
#     dd = date - d + 1;
#     dm = calendar_last_day_of_month (mm, yy);
#     if dd <= dm: return (mm,dd+1,yy);
#     d += dm;
#     mm=mm+1;
# return 0; # should not happened
def gregorian_day_of_week (yy, mm, dd):
   """Return the day-of-the-week index of gregorian (yy, mm, dd) DATE, 0 for Sunday, 1 for Monday, etc."""
   return gregorian_to_absolute (yy,mm, dd) % 7;
# ///////////////////////////////
# some tests for debuging to be removed

def test1():
  global __a_const;
  __a_const=48
  for __a_const in range(0,100): unmatched=0; from_y=1; to_y=4001
  for y in range(from_y,to_y):
    if hijri_days(y)!=emacs_hijri_days(y): unmatched+=1
  print ("%d years (%g %%) unmatched when a=%d", (unmatched, float(float(unmatched)/(to_y-from_y)), __a_const))
  __a_const=48
  sum=0.0
  for y in range(1,4001): sum+=hijri_days(y)
  print ("year len=%f ", float(float(sum)/4000.0*100.0))
  __a_const=47
  sum=0.0
  for y in range(1,4001): sum+=hijri_days(y)
  print ("year len=%f ", float(float(sum)/4000.0*100.0))
##########################
if __name__ == "__main__":
   # conclusion
   # 0% for a=16 48 65
   # 7% for a=1 31 33 50 80 82 97 99
   # 13% for a=14 18 46 63 67 95
   # 20% for a=12 29 3 35 52 78 84
   # ...
   # 73% for a=45 47 49 ..etc.
   ##########################
   __a_const=16
   print ("for a=%d", __a_const)
   sum=0.0
   for y in range(1,4001): sum+= float(hijri_month_days(y,12)==30)
   print ("perfect thu-hijja months is %f %% ", float(float(sum)/4000.0*100.0))
   sum=0.0
   for y in range(1,4001): sum+= float(hijri_month_days(y,9)==30)
   print ("perfect Ramadan months is %f %% ", float(float(sum)/4000.0*100.0))

   __a_const=48
   print ("for a=%d", __a_const)
   sum=0.0
   for y in range(1,4001): sum+= float(hijri_month_days(y,12)==30)
   print ("perfect thu-hijja months is %f %% ", float(float(sum)/4000.0*100.0))
   sum=0.0
   for y in range(1,4001): sum+= float(hijri_month_days(y,9)==30)
   print ("perfect Ramadan months is %f %% ", float(float(sum)/4000.0*100.0))

   __a_const=65
   print ("for a=%d", __a_const)
   sum=0.0
   for y in range(1,4001): sum+= float(hijri_month_days(y,12)==30)
   print ("perfect thu-hijja months is %f %% ", float(float(sum)/4000.0*100.0))
   sum=0.0
   for y in range(1,4001): sum+= float(hijri_month_days(y,9)==30)
   print ("perfect Ramadan months is %f %% ", float(float(sum)/4000.0*100.0))

   __a_const=48
   print ("for a=%d", __a_const)
   for m in range(1,13):
      sum=0.0
      for y in range(1,4001): sum+= float(hijri_month_days(y,m)==30)
      print ("perfect %d months is %f %% ", (m,float(float(sum)/4000.0*100.0)))

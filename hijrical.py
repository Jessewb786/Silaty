#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hijri Islamic High level Calendar API,
Copyright (c) 2006-2008 Muayyad Saleh Alsadi<alsadi@gmail.com>
Based on an enhanced algorithm designed by me
the algorithm is discussed in a book titled "حتى لا ندخل جحور الضباب"
(not yet published)

This file can be used to implement apps, gdesklets or karamba ..etc

The algorith itself is not here, it's in another file called hijra.py

    Released under terms on Waqf Public License.
    This program is free software; you can redistribute it and/or modify
    it under the terms of the latest version Waqf Public License as
    published by Ojuba.org.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    The Latest version of the license can be found on
    "http://www.ojuba.org/wiki/doku.php/waqf/license"

"""
from time import localtime
from hijra import *

class HijriCal:
    """a Class that provide a high level Islamic Hijri calendar API"""
    def __init__(self):
        """Create HijriCal Object"""
        self.__md = [[""]*7,[""]*7,[""]*7,[""]*7,[""]*7,[""]*7] # 7 days on at most 6 weeks
        self.__g_md = [[""]*7,[""]*7,[""]*7,[""]*7,[""]*7,[""]*7] # 7 days on at most 6 weeks
        self.__direct =- 1
        self.__ws = 6 # make Sat is first day of week, and fill rows directly
        self.goto_today()

    def goto_today(self):
        """Jump to today"""
        yy, mm, dd = localtime()[:3]
        self.g_today = (yy, mm, dd)
        Y, M, D = self.goto_gregorian_day(yy, mm, dd)
        wd = hijri_day_of_week (Y, M, D)
        self.today = (Y, M, D, wd)

    def refresh_today(self):
        """check is today is uptodate, update them if not and return True"""
        if self.g_today==localtime()[:3]:
            return False
        else:
            yy, mm, dd = localtime()[:3]
            self.g_today= (yy, mm, dd)
            Y, M, D = gregorian_to_hijri(yy, mm, dd)
            wd = hijri_day_of_week (Y, M, D)
            self.today= (Y, M, D, wd)
            return True

    def goto_gregorian_day(self,yy, mm, dd):
        """Jump to some Hijri day"""
        try:
            Y, M, D = gregorian_to_hijri(yy, mm, dd)
            self.goto_hijri_day(Y, M, D)
        except:
            self.validate()

        return (self.Y,self.M,self.D)

    def goto_hijri_day(self,Y,M,D):
        """Jump to some Hijri day"""
        self.Y, self.M, self.D = Y, M, D
        self.gy,self.gm,self.gd = hijri_to_gregorian(Y, M, D)
        self.validate()

        self.mn=hijri_month_days(self.Y, self.M)
        self.ms=(7 - self.__ws + hijri_day_of_week(self.Y, self.M, 1))% 7
        self.fill_month_days()
        return (Y,M,D)

    def fill_month_days(self):
        """for internal usage"""
        Y, M, D = self.Y,self.M, 1
        gy,gm,gd=hijri_to_gregorian(Y,M,D)
        gn=gregorian_month_days(gy,gm)
        for i in range(6):
            for j in range(7):
                self.__md[i][j]=""
                self.__g_md[i][j]=""
        row=0
        if self.__direct>0:
            col=self.ms
            endcol=7
            icol=0
        else:
            col=6-self.ms
            endcol=-1
            icol=6
        for i in range(self.mn):
            self.__md[row][col]=i+1
        self.__g_md[row][col]=(gd,gm,gy)
        gd+=1
        if (gd>gn):
            gd=1
            gm+=1

        if gm>12:
            gm=1
            gy+=1

        col+=self.__direct
        if (col==endcol):
            row+=1
            col=icol

    def validate(self):
        """Make sure the the current Y,M,D is a a valid date, return 0 if it's already valid"""
        f=0
        if self.M<1:
            self.M=12
            self.Y-=1
            f=1
        if self.M>12:
            self.M=1
            self.Y+=1
            f=1
        if self.Y<1:
            self.Y=1
            f=1
        if self.D<1:
            self.D=1
            f=1

        d=hijri_month_days(self.Y, self.M)
        if self.D>d :
            self.D=d
            f=1
        return f

    def get_array(self): return tuple(self.__md)
    def get_g_array(self): return tuple(self.__g_md)

    def get_week_start(self): return self.__ws
    def set_week_start(self,ws):
        """Set the first day of the week, 0:Sun, 1:Mon, ..., 6:Sat."""
        self.__ws=ws
        self.goto_hijri_day(self.Y, self.M, self.D)

    def get_direction(self): return self.__direct
    def set_direction(self, direct):
        """Set the BiDi RTL direction, 1 direct, -1 reversed"""
        self.__direct=direct
        self.goto_hijri_day(self.Y, self.M, self.D)

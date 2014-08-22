#!/usr/bin/python2
# -*- coding: utf-8 -*-
from math import sqrt, floor, ceil
import os
import subprocess

import yaml
import Tkconstants as TkC
from Tkinter import Tk, Frame, Button, Label, PhotoImage
from PIL import Image
import sys


class FlatButton(Button):
    def __init__(self, master=None, cnf={}, **kw):
        Button.__init__(self, master, cnf, **kw)
        # self.pack()
        self.config(
            compound=TkC.TOP,
            relief=TkC.FLAT,
            bd=0,
            bg="#b91d47",  # dark-red
            fg="white",
            activebackground="#b91d47",  # dark-red
            activeforeground="white",
            # height=118,
            #width=104,
            highlightthickness=0
        )

    def set_color(self, color):
        self.configure(
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white"
        )


class PiMenu(Frame):
    doc = None
    framestack = []
    icons = {}

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.pack(fill=TkC.BOTH, expand=1)

        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + '/pimenu.yaml', 'r') as f:
            self.doc = yaml.load(f)
        self.init()

    def init(self):
        self.show_items(self.doc)

    def show_items(self, items, upper=[]):
        num = 0

        # create a new frame
        wrap = Frame(self, bg="#e3a21a")
        # when there were previous frames, hide the top one and add a back button for the new one
        if len(self.framestack):
            self.hide_top()
            back = FlatButton(
                wrap,
                text='back...',
                image=self.get_icon("up_circular"),
                command=self.go_back,
            )
            back.set_color("#00a300")  # green
            back.grid(row=0, column=0, padx=1, pady=1, sticky=TkC.W + TkC.E + TkC.N + TkC.S)
            num += 1
        # add the new frame to the stack and display it
        self.framestack.append(wrap)
        self.show_top()

        # calculate tile distribution
        all = len(items) + num
        rows = floor(sqrt(all))
        cols = ceil(all / rows)

        # make cells autoscale
        for x in range(int(cols)):
            wrap.columnconfigure(x, weight=1)
        for y in range(int(rows)):
            wrap.rowconfigure(y, weight=1)

        # display all given buttons
        for item in items:
            act = upper + [item['name']]

            if 'icon' in item:
                image = self.get_icon(item['icon'])
            else:
                image = self.get_icon(item['label'][0:1].upper())

            btn = FlatButton(
                wrap,
                text=item['label'],
                image=image
            )

            if 'items' in item:
                # this is a deeper level
                btn.configure(command=lambda act=act, item=item: self.show_items(item['items'], act), )
                btn.set_color("#2b5797")  # dark-blue
            else:
                # this is an action
                btn.configure(command=lambda act=act: self.go_action(act), )

            # add buton to the grid
            btn.grid(
                row=int(floor(num / cols)),
                column=int(num % cols),
                padx=1,
                pady=1,
                sticky=TkC.W + TkC.E + TkC.N + TkC.S
            )
            num += 1

    def get_icon(self, name):
        # fixme check for existance
        if name in self.icons:
            return self.icons[name]
        self.icons[name] = PhotoImage(file='ico/' + name + '.gif')
        return self.icons[name]

    def hide_top(self):
        self.framestack[len(self.framestack) - 1].pack_forget()

    def show_top(self):
        self.framestack[len(self.framestack) - 1].pack(fill=TkC.BOTH, expand=1)

    def destroy_top(self):
        self.framestack[len(self.framestack) - 1].destroy()
        self.framestack.pop()

    def go_action(self, actions):
        # hide the menu and show a delay screen
        self.hide_top()
        delay = Frame(self, bg="#2d89ef")
        delay.pack(fill=TkC.BOTH, expand=1)
        label = Label(delay, text="Executing...", fg="white", bg="#2d89ef", font="Sans 30")
        label.pack(fill=TkC.BOTH, expand=1)
        self.parent.update()

        # excute shell script
        subprocess.call([os.path.dirname(os.path.realpath(sys.argv[0])) + '/pimenu.sh'] + actions,
                        shell=True)

        # remove delay screen and show menu again
        delay.destroy()
        self.show_top()

    def go_back(self):
        """
        destroy the current frame and reshow the one below
        :return:
        """
        self.destroy_top()
        self.show_top()


def main():
    root = Tk()
    root.geometry("320x240")
    app = PiMenu(root)
    root.mainloop()


if __name__ == '__main__':
    main()







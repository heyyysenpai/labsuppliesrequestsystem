from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter
import random
import pymysql
import csv
from datetime import datetime
import numpy as np

window=tkinter.Tk()
window.title("Lab Supplies Request System")
window.geometry("720x640")
my_tree=ttk.Treeview(window,show='headings',height=20)
style=ttk.Style()


placeholderArray=['']*11

for i in range(0,10):
    placeholderArray[i]=tkinter.StringVar()

dummydata=[
    ['asdf','asdf','asdf','asdf','asdf','asdf','asdf','asdf','asdf','asdf']
]

def refreshTable():
    for data in my_tree.get_children():
        my_tree.delete(data)
    for array in dummydata:
        my_tree.insert(parent='',index='end',iid=array,text="",values=(array),tag="orow")
    my_tree.tag_configure('orow',background="#EEEEEE")
    my_tree.pack()

frame=tkinter.Frame(window,bg="#4169e1")
frame.pack()

btnColor="#36454F"

manageFrame=tkinter.LabelFrame(frame,text="Manage",borderwidth=5)
manageFrame.grid(row=0,column=0,sticky="w",padx=[10,200],pady=20,ipadx=[6])

saveBtn=Button(manageFrame,text="SAVE",width=10,borderwidth=3,bg=btnColor,fg='white')
updateBtn=Button(manageFrame,text="UPDATE",width=10,borderwidth=3,bg=btnColor,fg='white')
deleteBtn=Button(manageFrame,text="DELETE",width=10,borderwidth=3,bg=btnColor,fg='white')
selectBtn=Button(manageFrame,text="SELECT",width=10,borderwidth=3,bg=btnColor,fg='white')
findBtn=Button(manageFrame,text="FIND",width=10,borderwidth=3,bg=btnColor,fg='white')
clearBtn=Button(manageFrame,text="CLEAR",width=10,borderwidth=3,bg=btnColor,fg='white')
exportBtn=Button(manageFrame,text="EXPORT",width=10,borderwidth=3,bg=btnColor,fg='white')

saveBtn.grid(row=0,column=0,padx=5,pady=5)
updateBtn.grid(row=0,column=1,padx=5,pady=5)
deleteBtn.grid(row=0,column=2,padx=5,pady=5)
selectBtn.grid(row=0,column=3,padx=5,pady=5)
findBtn.grid(row=0,column=4,padx=5,pady=5)
clearBtn.grid(row=0,column=5,padx=5,pady=5)
exportBtn.grid(row=0,column=6,padx=5,pady=5)

entriesFrame=tkinter.LabelFrame(frame,text="Form",borderwidth=5)
entriesFrame.grid(row=1,column=0,sticky="w",padx=[10,200],pady=[0,20],ipadx=[6])

requestnumberLabel=Label(entriesFrame,text="REQUEST NO.",anchor="e",width=15)
statusLabel=Label(entriesFrame,text="STATUS",anchor="e",width=15)
requestdateLabel=Label(entriesFrame,text="REQUEST DATE",anchor="e",width=15)
itemLabel=Label(entriesFrame,text="ITEM",anchor="e",width=15)
quantityLabel=Label(entriesFrame,text="QUANTITY",anchor="e",width=15)
unitLabel=Label(entriesFrame,text="UNIT",anchor="e",width=15)
catalognumberLabel=Label(entriesFrame,text="CATALOG NO.",anchor="e",width=15)
brandLabel=Label(entriesFrame,text="BRAND",anchor="e",width=15)
productlinkLabel=Label(entriesFrame,text="PRODUCT LINK",anchor="e",width=15)
iobLabel=Label(entriesFrame,text="IOB ALLOCATION",anchor="e",width=15)
ppmpLabel=Label(entriesFrame,text="PPMP ALLOCATION",anchor="e",width=15)

requestnumberLabel.grid(row=0,column=0,padx=10)
statusLabel.grid(row=1,column=0,padx=10)
requestdateLabel.grid(row=2,column=0,padx=10)
itemLabel.grid(row=3,column=0,padx=10)
quantityLabel.grid(row=4,column=0,padx=10)
unitLabel.grid(row=5,column=0,padx=10)
catalognumberLabel.grid(row=6,column=0,padx=10)
brandLabel.grid(row=7,column=0,padx=10)
productlinkLabel.grid(row=8,column=0,padx=10)
iobLabel.grid(row=9,column=0,padx=10)
ppmpLabel.grid(row=10,column=0,padx=10)

statusArray=['Pending','Done']

requestnumberEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[0])
statusCombo=ttk.Combobox(entriesFrame,width=50,textvariable=placeholderArray[1],values=statusArray)
requestdateEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[2])
itemEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[3])
quantityEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[4])
unitEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[5])
catalognumberEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[6])
brandEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[7])
productlinkEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[8])
iobEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[9])
ppmpEntry=Entry(entriesFrame,width=50,textvariable=placeholderArray[10])

requestnumberEntry.grid(row=0,column=2,padx=5,pady=5)
statusCombo.grid(row=1,column=2,padx=5,pady=5)
requestdateEntry.grid(row=2,column=2,padx=5,pady=5)
itemEntry.grid(row=3,column=2,padx=5,pady=5)
quantityEntry.grid(row=4,column=2,padx=5,pady=5)
unitEntry.grid(row=5,column=2,padx=5,pady=5)
catalognumberEntry.grid(row=6,column=2,padx=5,pady=5)
brandEntry.grid(row=7,column=2,padx=5,pady=5)
productlinkEntry.grid(row=8,column=2,padx=5,pady=5)
iobEntry.grid(row=9,column=2,padx=5,pady=5)
ppmpEntry.grid(row=10,column=2,padx=5,pady=5)

generateCodeBtn=Button(entriesFrame,text="GENERATE CODE",borderwidth=3,bg=btnColor,fg='white')
generateCodeBtn.grid(row=0,column=3,padx=5,pady=5)

style.configure(window)

my_tree['columns']=("Request No.","Status","Request Date","Item","Quantity","Unit","Catalog No.",
                    "Brand","Product Link","IOB Allocation","PPMP Allocation")
my_tree.column("#0",width=0,stretch=NO)
my_tree.column("Request No.",anchor=W,width=70)
my_tree.column("Status",anchor=W,width=70)
my_tree.column("Request Date",anchor=W,width=100)
my_tree.column("Item",anchor=W,width=70)
my_tree.column("Quantity",anchor=W,width=70)
my_tree.column("Unit",anchor=W,width=70)
my_tree.column("Catalog No.",anchor=W,width=70)
my_tree.column("Brand",anchor=W,width=70)
my_tree.column("Product Link",anchor=W,width=80)
my_tree.column("IOB Allocation",anchor=W,width=70)
my_tree.column("PPMP Allocation",anchor=W,width=70)
my_tree.heading("Request No.",text="Request No.",anchor=W)
my_tree.heading("Status",text="Status",anchor=W)
my_tree.heading("Request Date",text="Request Date",anchor=W)
my_tree.heading("Item",text="Item",anchor=W)
my_tree.heading("Quantity",text="Quantity",anchor=W)
my_tree.heading("Unit",text="Unit",anchor=W)
my_tree.heading("Catalog No.",text="Catalog No.",anchor=W)
my_tree.heading("Brand",text="Brand",anchor=W)
my_tree.heading("Product Link",text="Product Link",anchor=W)
my_tree.heading("IOB Allocation",text="IOB Allocation",anchor=W)
my_tree.heading("PPMP Allocation",text="PPMP Allocation",anchor=W)
my_tree.tag_configure('orow',background="#EEEEEE")
my_tree.pack()

refreshTable()

window.resizable(True,True)
window.mainloop()
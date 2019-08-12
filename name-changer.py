import os, sys
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

#####################################################
#                       CLASSES                     #
#####################################################

class Window:
    def __init__(self, run_script):
        self.geo = "320x280"
        self.title = "Name Changer"
        self.path = ''
        self.old = ''
        self.new = ''
        self.history = [[]] #--each array within history will contain results from each scan: From and To fullpaths

    def create(self):
        window = tk.Tk()
        window.geometry(self.geo)
        window.title(self.title)
        tk.Label(window, text='').pack()
        browse = tk.StringVar()
        browse.set('Select Parent Folder')
        browseLabel = tk.Label(window, textvariable=browse)
        browseLabel.pack()
        browseBtnLabel='...'
        pathButton = tk.Button(window, text='...', width=3, command=lambda : self.get_path(browse))
        pathButton.pack()
        tk.Label(window, text='').pack()
        fromLabel = tk.Label(window, text='From:')
        fromLabel.pack()
        titleFrom = tk.Entry(window)
        titleFrom.pack()
        toLabel = tk.Label(window, text='To:')
        toLabel.pack()
        titleTo = tk.Entry(window)
        titleTo.pack()
        tk.Label(window, text='').pack()
        runButton = tk.Button(window, text='Run Script', width=15, command=lambda : run_script(titleFrom, titleTo, self.path, self.history))
        runButton.pack()
        undoButton = tk.Button(window, text='Undo', width=5, command=self.undo)
        undoButton.pack()
        window.mainloop()

    def get_path(self, browse):
        tempPath = filedialog.askdirectory()
        if tempPath == '':
            return
        self.path = tempPath
        browse.set(self.path)

    def undo(self):
        def sortPaths(paths):                           #  For sorting paths so that deepest paths are reverted
            for pos in range(len(paths)-1, 0, -1):      #  first. This avoids reverting a parent dir that 
                for index in range(pos):                #  may contain a child that needs reverted as well.
                    if len(paths[index]['New'].split('/')) < len(paths[index+1]['New'].split('/')):
                        shorterPath = paths[index]
                        paths[index] = paths[index+1]
                        paths[index+1] = shorterPath

        if len(self.history) == 1:    #  Return if there is no history yet.
            if len(self.history[0]) == 0:
                return

        sortPaths(self.history[-1])
        problemPaths = []
        successPaths = []
        for path in self.history[-1]:
            oldPath = path['Old']
            newPath = path['New']
            result = rename(newPath, oldPath) #  Reversing the parameters since we are undoing.
            if not result:
                problemPaths.append(path)
            else:
                successPaths.append(path)

        if len(problemPaths) > 0:
            errorMessage = ''
            for path in problemPaths:
                oldPath = path['Old']
                newPath = path['New']
                errorMessage += f'FROM {newPath} TO {oldPath}\n\n'
            messagebox.showerror('Error!', f'The following files or folders could not be restored:\n\n{errorMessage}')

        if len(successPaths) > 0:
            successMessage = ''
            for path in successPaths:
                oldPath = path['Old']
                successMessage += f'{oldPath}\n'
            messagebox.showinfo('Success!', f'The following files or folders have been restored:\n\n{successMessage}')

        if len(self.history) == 1:
            self.history = [[]]
        else:
            del self.history[-1]


class NameChanger:
    def __init__(self, old, new, history):
        self.folderTally = 0
        self.fileTally = 0
        self.old = old
        self.new = new

    def worker(self, path, history, rename):
        if self.error_check(path) == 'error':
            return 'error'

        folders = []
        for f in os.listdir(path):
            fullPath = path + '/' + f
            if os.path.isdir(fullPath):
                if self.old in f:
                    fullPath = self.handle_rename(f, path, fullPath, history, rename)
                    if not fullPath:
                        return
                folders.append(fullPath)
            else:
                if self.old in f:
                    self.handle_rename(f, path, fullPath, history, rename)

        if len(folders) > 0:
            for f in folders:
                self.worker(f, history, rename)


    def handle_rename(self, name, path, fullPath, history, rename):
        newName = name.replace(self.old, self.new)
        oldPath = fullPath
        newPath = path + '/' + newName
        rename(oldPath, newPath)
        if os.path.isdir(newPath):
            self.folderTally += 1
        else:
            self.fileTally += 1
        history[-1].append({'Old': oldPath, 'New': newPath})
        return newPath

    def error_check(self, path):
        if not os.path.isdir(path):
            messagebox.showerror('Error!', 'Please select a valid path.')
            return 'error'
        if self.old == self.new:
            messagebox.showerror('Error!', '"From" and "To" can not match.')
            return 'error'
        if self.old == '':
            messagebox.showerror('Error!', '"From" can not be an empty string.')
            return 'error'

    def result(self):
        def qtyStr(fType):
            qty = self.folderTally if fType == 'folder' else self.fileTally
            ifPlural = 's' if qty != 1 else ''
            fType += ifPlural
            return f'{qty} {fType}'
        folderQtyStr = qtyStr('folder')
        filQtyStr = qtyStr('file')
        messagebox.showinfo("Done", f'{folderQtyStr} and {filQtyStr} have been renamed!')


#########################################################
#                       FUNCTIONS                       #
#########################################################


def rename(oldPath, newPath):
    try:
        os.rename(oldPath, newPath)
        return True
    except:
        messagebox.showerror('Error!', f'{oldPath} could not be renamed!\n\n{sys.exc_info()[1]}')
        return

def run_script(old, new, path, history):
    if len(history[-1]) > 0: #----------history is for keeping track of results of each scan
        history.append([])   #----------if nothing was changed, no need to append another empty array
    scan = NameChanger(old.get(), new.get(), history) #--just use the already existing empty array
    result = scan.worker(path, history, rename)
    if result == 'error':
        return
    scan.result()

def main():
    app = Window(run_script)
    app.create()


###################################################
#                       BODY                      #
###################################################

    
if __name__ == "__main__":
    main()


####################################################
#                       To-Do                      #
####################################################


#change path to Entry and put browse button next to it

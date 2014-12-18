__author__ = 'wack'


import wx
import wx.aui
import wx.lib.agw.customtreectrl as ctc
import wx.py.crust
import wx.grid
import matplotlib as mpl
import numpy as np
from wx.py.shell import Shell

import RockPy
import RockPy.file_operations as rfo


# uncomment the following to use wx rather than wxagg
#matplotlib.use('WX')
#from matplotlib.backends.backend_wx import FigureCanvasWx as FigureCanvas

# comment out the following to use wx rather than wxagg
#mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from wx import xrc

class MainFrame(wx.Frame):

    def __init__(self, parent, id=-1, title='RockPy rocks ...',
                 pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        # get xrc ressources
        self.xrc = xrc.XmlResource("rockpygui.xrc")

        # main study object
        self.study = None

        # last file directory used
        self.lastdir = rfo.default_folder


        self.InitMenu()
        self.InitStatusBar()
        self.InitAuiManager()

        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def InitMenu(self):
        self.SetMenuBar(self.xrc.LoadMenuBar("mainmenubar"))

        # initial check of menu items
        self.GetMenuBar().FindItemById(xrc.XRCID("PythonConsoleMenuItem")).Check(False)
        self.GetMenuBar().FindItemById(xrc.XRCID("NavigatorMenuItem")).Check(True)
        self.GetMenuBar().FindItemById(xrc.XRCID("InspectorMenuItem")).Check(True)

        # Data
        self.Bind(wx.EVT_MENU, self.OnLoadFile, id=xrc.XRCID("LoadFileMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnSaveFile, id=xrc.XRCID("SaveFileMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnExit, id=xrc.XRCID("ExitMenuItem"))
        # View
        self.Bind(wx.EVT_MENU, self.OnTogglePane, id=xrc.XRCID("PythonConsoleMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnTogglePane, id=xrc.XRCID("NavigatorMenuItem"))
        self.Bind(wx.EVT_MENU, self.OnTogglePane, id=xrc.XRCID("InspectorMenuItem"))
        # Help

    def InitStatusBar(self):
        self.CreateStatusBar()
        self.SetStatusText("Welcome to RockPy")

    def InitAuiManager(self):
        # make aui manager to manage docking window layout
        self._mgr = wx.aui.AuiManager(self)

        self.maintext = wx.TextCtrl(self, -1, 'hier soll mal was Wichtiges rein ....',
                            wx.DefaultPosition, wx.Size(200, 150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
        # add the panes to the manager
        self.navpanel = self.xrc.LoadPanel(self, "navpanel")
        self.inspectorpanel = self.xrc.LoadPanel(self, "inspectorpanel")
        self.createTree()

        self._mgr.AddPane(self.navpanel, wx.aui.AuiPaneInfo().
                          Name("Navigator").Caption("Navigator").Left().
                          CloseButton(True).MaximizeButton(True).BestSize((300, 500)))

        self._mgr.AddPane(self.inspectorpanel, wx.aui.AuiPaneInfo().
                          Name("Inspector").Caption("Inspector").Right().
                          CloseButton(True).MaximizeButton(True).BestSize((300, 500)))

        locals = {"ShowFigure": self.ShowFigure, "study": self.study}
        self.shell = Shell(parent=self, introText='Welcome to the RockPy shell ...', locals=locals)
        self._mgr.AddPane(self.shell, wx.aui.AuiPaneInfo().Name("Console").Bottom().BestSize((300, 400)).Hide(), 'Console')
        self.nb = wx.aui.AuiNotebook(self)
        self.grid = wx.grid.Grid(self.nb)
        self.grid.CreateGrid(12, 8)

        self.nb.AddPage(self.grid, "Data Table")
        self.nb.AddPage(self.maintext, "Wichtig")

        self.createTestPlot()

        self._mgr.AddPane(self.nb, wx.CENTER)

        # Bind aui manager events
        self._mgr.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnAuiPaneClose)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        # define panes to toggle as dict menuitemid: panename
        self.toggle_panes = {xrc.XRCID("PythonConsoleMenuItem"): "Console", xrc.XRCID("InspectorMenuItem"): "Inspector",
                 xrc.XRCID("NavigatorMenuItem"): "Navigator"}

    def createTree(self):
        # Create a CustomTreeCtrl instance and putit within a boxsizer in navtreepanel from xrc
        p = xrc.XRCCTRL(self.navpanel, 'navtreepanel')
        self.navtree = ctc.CustomTreeCtrl(p, agwStyle=wx.TR_DEFAULT_STYLE)
        bsizer = wx.BoxSizer()
        bsizer.Add(self.navtree, 1, wx.EXPAND)
        p.SetSizerAndFit(bsizer)

        # Add a root node to it
        root = self.navtree.AddRoot("Study", ct_type=1)

        # Create an image list to add icons next to an item
        il = wx.ImageList(16, 16)
        fldridx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        fldropenidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))

        self.navtree.SetImageList(il)

        self.navtree.SetItemImage(root, fldridx, wx.TreeItemIcon_Normal)
        self.navtree.SetItemImage(root, fldropenidx, wx.TreeItemIcon_Expanded)

        for x in range(15):
            child = self.navtree.AppendItem(root, "Sample Group %d" % x, ct_type=1)
            self.navtree.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
            self.navtree.SetItemImage(child, fldropenidx, wx.TreeItemIcon_Expanded)

            for y in range(5):
                last = self.navtree.AppendItem(child, "Sample %d-%s" % (x, chr(ord("a")+y)), ct_type=1)
                self.navtree.SetItemImage(last, fldridx, wx.TreeItemIcon_Normal)
                self.navtree.SetItemImage(last, fldropenidx, wx.TreeItemIcon_Expanded)

                for z in range(5):
                    item = self.navtree.AppendItem(last,  "Measurement %d-%s-%d" % (x, chr(ord("a")+y), z), ct_type=1)
                    self.navtree.SetItemImage(item, fileidx, wx.TreeItemIcon_Normal)

        self.navtree.Expand(root)

    def UpdateStudyNavTree(self):
        self.navtree.DeleteAllItems()  # clear the tree
        if self.study == None:
            # no study do nothing
            return

        # Add a study as root node
        root = self.navtree.AddRoot("Study", ct_type=1)

        self.navtree.SetItemImage(root, 0, wx.TreeItemIcon_Normal)
        self.navtree.SetItemImage(root, 1, wx.TreeItemIcon_Expanded)

        # iterate over all samplegroups
        for sg in self.study.samplegroups:
            child = self.navtree.AppendItem(root, sg.name, ct_type=1)
            self.navtree.SetItemImage(child, 0, wx.TreeItemIcon_Normal)
            self.navtree.SetItemImage(child, 1, wx.TreeItemIcon_Expanded)

            # iterate over all samples of each samplegroup
            for s in sg:
                last = self.navtree.AppendItem(child, s.name, ct_type=1)
                self.navtree.SetItemImage(last, 0, wx.TreeItemIcon_Normal)
                self.navtree.SetItemImage(last, 1, wx.TreeItemIcon_Expanded)

                # iterate over all measurements of each sample
                for m in s.measurements:
                    item = self.navtree.AppendItem(last, m.mtype, ct_type=1)
                    self.navtree.SetItemImage(item, 2, wx.TreeItemIcon_Normal)

        self.navtree.Expand(root)



    def ShowFigure(self, figure, title='plot'):
        # make a panel
        panel = wx.Panel(self.nb)

        self.canvas = FigureCanvas(panel, -1, figure)

        # make toolbar
        self.plottoolbar = NavigationToolbar2Wx(self.canvas)
        self.plottoolbar.Realize()

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Best to allow the toolbar to resize!
        sizer.Add(self.plottoolbar, 0, wx.GROW)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        # assign sizer to panel
        panel.SetSizer(sizer)
        panel.Fit()

        self.figure.canvas.mpl_connect('pick_event', self.on_pick)

        self.nb.AddPage(panel, title)

    def createTestPlot(self):
        # make figure for test
        self.figure = mpl.figure.Figure()
        self.axes = self.figure.add_subplot(111)
        t = np.arange(0.0, 3.0, 0.1)
        s = np.sin(2*np.pi*t)
        self.axes.scatter(t, s, c=[(1.0, 0, 0, 1.0) for i in range(len(t))], marker="o", picker=5)
        self.ShowFigure(self.figure)

    def on_pick(self, event):
        artist = event.artist
        #print artist
        #print event.ind
        fc = artist.get_facecolors()
        fc = [(1.0, 0, 0, 1.0) for i in range(len(fc))]
        fc[event.ind[0]] = (0, 1.0, 0, 1.0)
        artist.set_facecolors(fc)

        #artist.set_color(np.random.random(3))
        self.figure.canvas.draw()


    # data menu handlers
    def OnLoadFile(self, event):
        '''
        called when user clicks on Load from file menu item
        :param event:
        :return:
        '''
        dlg = wx.FileDialog(self, "Choose a RockPy file", self.lastdir, "", "*.rpy", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            self.lastdir = dirname

            obj = rfo.load(filename, dirname)
            if not isinstance(obj, RockPy.Study):
                wx.MessageBox('Could not read study from file', 'Error', wx.OK | wx.ICON_ERROR)
            else:  # got a proper Study object from the file
                # set the loaded study as the main study
                self.study = obj
                # update study object in shell window
                self.shell.interp.locals['study'] = self.study

                self.SetStatusText("%s loaded" % filename)

                self.UpdateStudyNavTree()

        dlg.Destroy()



    def OnSaveFile(self, event):
        '''
        called when user clicks on Save to file menu item
        :param event:
        :return:
        '''

        if self.study == None:
            wx.MessageBox('No study to save', 'Error', wx.OK | wx.ICON_ERROR)

        dlg = wx.FileDialog(self, "Choose a file", self.lastdir, "", "*.rpy", wx.SAVE | wx.OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            self.lastdir = dirname

            rfo.save(self.study, filename, dirname)

            self.SetStatusText("%s saved" % filename)

        # Get rid of the dialog to keep things tidy
        dlg.Destroy()


    def OnExit(self, event):
        self.Close()

    # view menu handlers
    def OnTogglePane(self, event):
        pane = self._mgr.GetPane(self.toggle_panes[event.GetId()])
        if pane.IsShown() and not event.IsChecked():
            pane.Hide()
        if not pane.IsShown() and event.IsChecked():
            pane.Show()
        self._mgr.Update()

    def OnClose(self, event):
        '''
        called when user tries to close the main frame
        :param event:
        :return:
        '''
        dlg = wx.MessageDialog(self,
              "Do you really want to close RockPy GUI?",
              "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            # deinitialize the frame manager
            self._mgr.UnInit()
            # delete the frame
            self.Destroy()

    def OnAuiPaneClose(self, event):
        '''
        called when an AUI Pane gets closed
        :param event:
        :return:
        '''
        pane = event.GetPane()
        rev_toggle_panes = {v: k for k, v in self.toggle_panes.iteritems()}
        try:
            menuitemid = rev_toggle_panes[pane.name]
        except IndexError:
            print("no matching menu item for pane %s" % pane.name)
        else:
            self.GetMenuBar().FindItemById(menuitemid).Check(False)  # uncheck corresponding menu item


def main():
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()



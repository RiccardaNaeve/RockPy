__author__ = 'wack'


import wx
import wx.aui
import wx.lib.agw.customtreectrl as ctc
import wx.py.crust
import wx.grid
import matplotlib as mpl
import numpy as np


import RockPy
import RockPy.file_operations as rfo
from rpshell import RPShell

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

        self.Maximize(True)

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

        # add the panes to the manager

        # inspector panel
        self.inspectorpanel = self.xrc.LoadPanel(self, "inspectorpanel")

        self._mgr.AddPane(self.inspectorpanel, wx.aui.AuiPaneInfo().
                          Name("Inspector").Caption("Inspector").Right().
                          CloseButton(True).MaximizeButton(True).BestSize((300, 500)))

        # shell panel
        locals = {"ShowFigure": self.ShowFigure, "study": self.study}
        self.shell = RPShell(parent=self, introText='Welcome to the RockPy shell ...', locals=locals)
        self.shell.registerPushCallBack(self.OnShellPush)
        self._mgr.AddPane(self.shell, wx.aui.AuiPaneInfo().Name("Console").Bottom().BestSize((300, 400)).Hide(), 'Console')


        # navigation notebook (no close buttons on tabs)
        self.nav_nb = wx.aui.AuiNotebook(self, style = wx.aui.AUI_NB_DEFAULT_STYLE & ~(wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB))

        self.CreateNavTree()

        self.nav_nb.AddPage(self.nav_tree, "Samples")
        self.nav_nb.AddPage(wx.Panel(self.nav_nb), "Measurements")
        self.nav_nb.AddPage(wx.Panel(self.nav_nb), "Treatments")


        self._mgr.AddPane(self.nav_nb, wx.aui.AuiPaneInfo().
                          Name("Navigator").Caption("Navigator").Left().
                          CloseButton(True).MaximizeButton(True).MinSize((350, 100)))

        # plotting notebook
        self.plot_nb = wx.aui.AuiNotebook(self)
        self.grid = wx.grid.Grid(self.plot_nb)
        self.grid.CreateGrid(12, 8)

        self.plot_nb.AddPage(self.grid, "Data Table")

        self.CreateTestPlot()

        self._mgr.AddPane(self.plot_nb, wx.CENTER)

        # Bind aui manager events
        self._mgr.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnAuiPaneClose)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        # define panes to toggle as dict menuitemid: panename
        self.toggle_panes = {xrc.XRCID("PythonConsoleMenuItem"): "Console", xrc.XRCID("InspectorMenuItem"): "Inspector",
                 xrc.XRCID("NavigatorMenuItem"): "Navigator"}

    def CreateNavTree(self):
        # Create a CustomTreeCtrl instance and putit within a boxsizer in navtreepanel from xrc
        self.nav_tree = ctc.CustomTreeCtrl(self.nav_nb, agwStyle=wx.TR_DEFAULT_STYLE)

        # Create an image list to add icons next to an item
        il = wx.ImageList(16, 16)
        il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))

        self.nav_tree.SetImageList(il)

        self.UpdateStudyNavTree()

        # register context menu
        self.nav_tree.Bind(wx.EVT_CONTEXT_MENU, self.onNavTreeContext)


    def UpdateStudyNavTree(self):
        self.nav_tree.DeleteAllItems()  # clear the tree

        # Add a study as root node
        root = self.nav_tree.AddRoot("Study", ct_type=1)

        if self.study == None:
            # no study do nothing
            return

        self.nav_tree.SetItemImage(root, 0, wx.TreeItemIcon_Normal)
        self.nav_tree.SetItemImage(root, 1, wx.TreeItemIcon_Expanded)

        # iterate over all samplegroups
        for sg in self.study.samplegroups:
            child = self.nav_tree.AppendItem(root, sg.name, ct_type=1)
            self.nav_tree.SetItemImage(child, 0, wx.TreeItemIcon_Normal)
            self.nav_tree.SetItemImage(child, 1, wx.TreeItemIcon_Expanded)

            # iterate over all samples of each samplegroup
            for s in sg:
                last = self.nav_tree.AppendItem(child, s.name, ct_type=1)
                self.nav_tree.SetItemImage(last, 0, wx.TreeItemIcon_Normal)
                self.nav_tree.SetItemImage(last, 1, wx.TreeItemIcon_Expanded)

                # iterate over all measurements of each sample
                for m in s.measurements:
                    if not 'parameters' in type(m).__module__:
                        item = self.nav_tree.AppendItem(last, m.mtype, ct_type=1)
                        self.nav_tree.SetItemImage(item, 2, wx.TreeItemIcon_Normal)

        self.nav_tree.Expand(root)



    def ShowFigure(self, figure, title='plot'):
        # make a panel
        panel = wx.Panel(self.plot_nb)

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

        self.plot_nb.AddPage(panel, title)

    def CreateTestPlot(self):
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

    def OnShellPush(self, command):
        print "%s executed in shell window" % command


    def onNavTreeContext(self, event):
        """
        Create and show dynamic context menu
        """

        # identify tree item
        hitobj, flags = self.nav_tree.HitTest(self.nav_tree.ScreenToClient(event.GetPosition()))
        if isinstance( hitobj, ctc.GenericTreeItem):
            print hitobj.GetText()

        # get some entries
        items = ('a', 'plots', 'delete')

        # make dict with unique ids
        self.popupnavtreeids = {i: wx.NewId() for i in items}

        # build the menu
        menu = wx.Menu()

        for item, id in self.popupnavtreeids.items():
            menu.Append(id, item)
            self.Bind(wx.EVT_MENU, self.onNavTreePopup, id=id)

        # show the popup menu
        self.PopupMenu(menu)
        self.popupnavtreeids = None
        menu.Destroy()

    def onNavTreePopup(self, event):
        l = event.GetEventObject().FindItemById(event.GetId()).GetLabel()

        wx.MessageBox('Context Menu %s selected' % l)


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



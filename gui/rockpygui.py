__author__ = 'wack'


import wx
import wx.aui
import wx.lib.agw.customtreectrl as ctc
import wx.py.crust
from wx import xrc

class MainFrame(wx.Frame):

    def __init__(self, parent, id=-1, title='RockPy rocks ...',
                 pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        # get xrc ressources
        self.xrc = xrc.XmlResource("rockpygui.xrc")

        self.InitMenu()
        self.InitStatusBar()
        self.InitAuiManager()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitMenu(self):
        self.SetMenuBar(self.xrc.LoadMenuBar("mainmenubar"))
        self.Bind(wx.EVT_MENU, self.OnExit, id=xrc.XRCID("ExitMenuItem"))

    def InitStatusBar(self):
        self.CreateStatusBar()
        self.SetStatusText("This is RockPy statusbar")

    def InitAuiManager(self):
        # make aui manager to manage docking window layout
        self._mgr = wx.aui.AuiManager(self)


        #self.text = wx.TextCtrl(self, -1, 'und hier auch',
        #                    wx.DefaultPosition, wx.Size(200,150),
        #                    wx.NO_BORDER | wx.TE_MULTILINE)

        self.maintext = wx.TextCtrl(self, -1, 'hier soll mal was Wichtiges rein ....',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
        # add the panes to the manager
        self.navpanel = self.xrc.LoadPanel(self, "navpanel")
        self.createTree()

        self._mgr.AddPane(self.navpanel, wx.aui.AuiPaneInfo().
                          Name("Navigator").Caption("Navigator").Left().
                          CloseButton(True).MaximizeButton(True).BestSize((300, 500)))
        self._mgr.AddPane( wx.py.crust.Crust(parent = self), wx.aui.AuiPaneInfo().Bottom().BestSize((300, 400)), 'Shell')
        #self._mgr.AddPane(self.text, wx.BOTTOM, 'Text...')
        self._mgr.AddPane(self.maintext, wx.CENTER)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

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


    def OnExit(self, event):
        self.Close()
    
    def OnClose(self, event):
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

def main():
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()



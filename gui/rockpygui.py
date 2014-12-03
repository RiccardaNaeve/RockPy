__author__ = 'wack'


import wx
import wx.aui
import wx.lib.agw.customtreectrl as ctc

class MainFrame(wx.Frame):

    def __init__(self, parent, id=-1, title='RockPy rocks ...',
                 pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = wx.aui.AuiManager(self)


        self.text = wx.TextCtrl(self, -1, 'und hier auch',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)

        self.maintext = wx.TextCtrl(self, -1, 'hier soll mal was Wichtiges rein ....',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
        self.createTree()

        # add the panes to the manager
        self._mgr.AddPane(self.custom_tree, wx.aui.AuiPaneInfo().
                          Name("Gadget").Caption("Gadget").Left().
                          CloseButton(True).MaximizeButton(True).BestSize((300, 500)))
        self._mgr.AddPane(self.text, wx.BOTTOM, 'Text...')
        self._mgr.AddPane(self.maintext, wx.CENTER)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def createTree(self):
        # Create a CustomTreeCtrl instance
        self.custom_tree = ctc.CustomTreeCtrl(self, agwStyle=wx.TR_DEFAULT_STYLE)

        # Add a root node to it
        root = self.custom_tree.AddRoot("Study", ct_type=1)

        # Create an image list to add icons next to an item
        il = wx.ImageList(16, 16)
        fldridx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        fldropenidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))

        self.custom_tree.SetImageList(il)

        self.custom_tree.SetItemImage(root, fldridx, wx.TreeItemIcon_Normal)
        self.custom_tree.SetItemImage(root, fldropenidx, wx.TreeItemIcon_Expanded)

        for x in range(15):
            child = self.custom_tree.AppendItem(root, "Sample Group %d" % x, ct_type=1)
            self.custom_tree.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
            self.custom_tree.SetItemImage(child, fldropenidx, wx.TreeItemIcon_Expanded)

            for y in range(5):
                last = self.custom_tree.AppendItem(child, "Measurement %d-%s" % (x, chr(ord("a")+y)), ct_type=1)
                self.custom_tree.SetItemImage(last, fldridx, wx.TreeItemIcon_Normal)
                self.custom_tree.SetItemImage(last, fldropenidx, wx.TreeItemIcon_Expanded)

                for z in range(5):
                    item = self.custom_tree.AppendItem(last,  "item %d-%s-%d" % (x, chr(ord("a")+y), z), ct_type=1)
                    self.custom_tree.SetItemImage(item, fileidx, wx.TreeItemIcon_Normal)

        self.custom_tree.Expand(root)

    
    def OnClose(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()
        # delete the frame
        self.Destroy()


app = wx.App()
frame = MainFrame(None)
frame.Show()
app.MainLoop()

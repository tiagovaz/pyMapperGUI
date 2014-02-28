import wx
from wx.lib.mixins.inspection import InspectionMixin
from Resources.mymapper import MyMapper
from Resources.panels import *

class MyFrame(wx.Frame):
    def __init__(self, parent, title, size):
        wx.Frame.__init__(self, parent, -1, title=title, size=size)

        ############### widgets & bindings ########################################3

        ## main panel
        self.main_panel = wx.Panel(self)

        ## connections panel
        self.connections_panel = ConnectionsPanel(parent=self.main_panel)

        ## signal trees panels
        self.sources_panel = MyTreeList(parent=self.main_panel, id=-1, which="sources")
        self.destinations_panel = MyTreeList(parent=self.main_panel, id=-1, which="destinations")

        ## Static texts
        sources_label = wx.StaticText(self.main_panel, -1, " Sources ")
        sources_label.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        sources_label.SetForegroundColour("grey")

        destinations_label = wx.StaticText(self.main_panel, -1, " Destinations ")
        destinations_label.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        destinations_label.SetForegroundColour("grey")

        conn_label = wx.StaticText(self.main_panel, -1, "Connections")
        conn_label.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        conn_label.SetForegroundColour("grey")

        ## toolbar
        icons_folder = "icons22x22/"

        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize((22,22))  # sets icon size

        load_ico = wx.Bitmap(icons_folder+'document-open.png')
        load_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, load_ico, "Load state file", "Loads a saved connections state.")
        self.Bind(wx.EVT_MENU, self.OnLoad, load_tool)

        save_ico = wx.Bitmap(icons_folder+'document-save-as.png')
        save_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, save_ico, "Save state file", "Saves the current connections.")
        self.Bind(wx.EVT_MENU, self.OnSave, save_tool)

        self.toolbar.AddSeparator()

        ### connect
        connect_ico = wx.Bitmap(icons_folder+'node-join-segment.png')
        connect_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, connect_ico, "Connect", "Connects selected source to selected destination.")
        self.Bind(wx.EVT_MENU, self.OnConnect, connect_tool)

        ### disconnect
        disconnect_ico = wx.Bitmap(icons_folder+'node-delete-segment.png')
        disconnect_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, disconnect_ico, "Disconnect", "Disconnects selected source from selected destination.")
        self.Bind(wx.EVT_MENU, self.OnDisconnect, disconnect_tool)

        ### disconnect all
        disconnect_all_ico = wx.Bitmap(icons_folder+'process-stop.png')
        disconnect_all_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, disconnect_all_ico, "Disconnect all", "Disconnects everything!")
        self.Bind(wx.EVT_MENU, self.OnDisconnectAll, disconnect_all_tool)

        ### refresh all
        refresh_ico = wx.Bitmap(icons_folder+'view-refresh.png')
        refresh_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, refresh_ico, "Refresh", "Refresh all devices, signals and connections.")
        self.Bind(wx.EVT_MENU, self.OnRefresh, refresh_tool)

        self.toolbar.AddSeparator()

        mute_ico = wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW, wx.ART_TOOLBAR, (16,16))
        mute_tool = self.toolbar.AddCheckLabelTool(wx.ID_ANY, "Checkable", mute_ico, shortHelp="Mute")

        bypass_ico = wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_TOOLBAR, (16,16))
        bypass_tool = self.toolbar.AddCheckLabelTool(wx.ID_ANY, "Checkable", bypass_ico, shortHelp="Bypass")

        linear_ico = wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR, wx.ART_TOOLBAR, (16,16))
        linear_tool = self.toolbar.AddCheckLabelTool(wx.ID_ANY, "Checkable", linear_ico, shortHelp="Linear")

        calib_ico = wx.ArtProvider.GetBitmap(wx.ART_GO_DIR_UP, wx.ART_TOOLBAR, (16,16))
        calib_tool = self.toolbar.AddCheckLabelTool(wx.ID_ANY, "Checkable", calib_ico, shortHelp="Calibrate")

        rev_ico = wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR, (16,16))
        rev_tool = self.toolbar.AddCheckLabelTool(wx.ID_ANY, "Checkable", rev_ico, shortHelp="Reverse")

        expr_ico = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_TOOLBAR, (16,16))
        expr_tool = self.toolbar.AddCheckLabelTool(wx.ID_ANY, "Checkable", expr_ico, shortHelp="Expression")

        # expression for mapping
        self.expression_y = wx.StaticText(self.toolbar, -1, " Expr ")
        self.expression_input = wx.TextCtrl(self.toolbar, -1, "", size=(220, 26))
        self.toolbar.AddControl(self.expression_y)
        self.toolbar.AddControl(self.expression_input)

        self.arrow_range = wx.StaticText(self.toolbar, -1, "-")
        self.arrow_range2 = wx.StaticText(self.toolbar, -1, "-")

        # source / dest range input
        self.toolbar.AddSeparator()
        self.src_range_label = wx.StaticText(self.toolbar, -1, " Source range: ")
        self.src_range_min = wx.TextCtrl(self.toolbar, -1, "", size=(100, 26))
        self.src_range_max = wx.TextCtrl(self.toolbar, -1, "", size=(100, 26))
        self.toolbar.AddControl(self.src_range_label)
        self.toolbar.AddControl(self.src_range_min)
        self.toolbar.AddControl(self.arrow_range)
        self.toolbar.AddControl(self.src_range_max)

        self.dest_range_label = wx.StaticText(self.toolbar, -1, " Dest. range: ")
        self.dest_range_min = wx.TextCtrl(self.toolbar, -1, "", size=(100, 26))
        self.dest_range_max = wx.TextCtrl(self.toolbar, -1, "", size=(100, 26))
        self.toolbar.AddControl(self.dest_range_label)
        self.toolbar.AddControl(self.dest_range_min)
        self.toolbar.AddControl(self.arrow_range2)
        self.toolbar.AddControl(self.dest_range_max)

        ## statusbar
        self.statusbar = self.CreateStatusBar()

        ## menubar #TODO: rename menus
        menu_bar = wx.MenuBar()
        menu1 = wx.Menu()
        menuItem = menu1.Append(-1, "&Quit")
        menu_bar.Append(menu1, "&File")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.OnQuit, menuItem)

        menu2 = wx.Menu()
        menu2.Append(wx.NewId(), "&Preferences...", "Set Preferences")
        menu_bar.Append(menu2, "&Edit")

        menu3 = wx.Menu()
        menu3.Append(wx.NewId(), "&About", "About")
        menu_bar.Append(menu3, "&Help")

        ## source/destination search
        self.sources_search = wx.SearchCtrl(self.main_panel, size=(240, -1), style=wx.TE_PROCESS_ENTER)
        self.destinations_search = wx.SearchCtrl(self.main_panel, size=(240,-1), style=wx.TE_PROCESS_ENTER)

        ## expand/collapse controls
        expand_icon = wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, (16,16))
        collapse_icon = wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, (16,16))

        ### expand all src
        expand_src_button = wx.BitmapButton(self.main_panel, -1, expand_icon, (16, 16), (expand_icon.GetWidth()+5, expand_icon.GetHeight()+5))
        expand_src_button.SetToolTipString("This is a bitmap button.")
        self.Bind(wx.EVT_BUTTON, self.sources_panel.OnExpand, expand_src_button)

        ### expand all dest
        expand_dest_button = wx.BitmapButton(self.main_panel, -1, expand_icon, (16, 16), (expand_icon.GetWidth()+5, expand_icon.GetHeight()+5))
        expand_dest_button.SetToolTipString("This is a bitmap button.")
        self.Bind(wx.EVT_BUTTON, self.destinations_panel.OnExpand, expand_dest_button)

        ### collapse all src
        collapse_src_button = wx.BitmapButton(self.main_panel, -1, collapse_icon, (16, 16), (collapse_icon.GetWidth()+5, collapse_icon.GetHeight()+5))
        collapse_src_button.SetToolTipString("This is a bitmap button.")
        self.Bind(wx.EVT_BUTTON, self.sources_panel.OnCollapse, collapse_src_button)

        ### collapse all dest
        collapse_dest_button = wx.BitmapButton(self.main_panel, -1, collapse_icon, (16, 16), (collapse_icon.GetWidth()+5, collapse_icon.GetHeight()+5))
        collapse_dest_button.SetToolTipString("This is a bitmap button.")
        self.Bind(wx.EVT_BUTTON, self.destinations_panel.OnCollapse, collapse_dest_button)

        ################ layout #########################################

        ## sizers
        main_box = wx.BoxSizer(wx.VERTICAL)
        h_box = wx.BoxSizer(wx.HORIZONTAL)
        main_box.Add(wx.StaticLine(self.main_panel,) ,0 , wx.ALL|wx.EXPAND, 5)
        main_box.Add(h_box, 1, wx.EXPAND)

        sources_label_box = wx.BoxSizer(wx.HORIZONTAL)
        destinations_label_box = wx.BoxSizer(wx.HORIZONTAL)
        connections_label_box = wx.BoxSizer(wx.HORIZONTAL)

        sources_label_box.Add(sources_label, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        sources_label_box.Add(expand_src_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        sources_label_box.Add(collapse_src_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        sources_label_box.Add((10,10))
        sources_label_box.Add(self.sources_search, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        connections_label_box.Add(conn_label, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        destinations_label_box.Add(destinations_label, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        destinations_label_box.Add(expand_dest_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        destinations_label_box.Add(collapse_dest_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        destinations_label_box.Add((10,10))
        destinations_label_box.Add(self.destinations_search, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        ## trees
        col1_box = wx.BoxSizer(wx.VERTICAL)
        col2_box = wx.BoxSizer(wx.VERTICAL)
        col3_box = wx.BoxSizer(wx.VERTICAL)

        h_box.Add(col1_box, 2, wx.ALL|wx.EXPAND)
        h_box.Add(col2_box, 1, wx.ALL|wx.EXPAND)
        h_box.Add(col3_box, 2, wx.ALL|wx.EXPAND)

        ## labels sizer
        col1_box.Add(sources_label_box, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        col1_box.Add((5, 5))
        col2_box.Add(connections_label_box, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        col2_box.Add((5, 5))
        col3_box.Add(destinations_label_box, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        col3_box.Add((5, 5))

        ## trees sizer
        col1_box.Add(self.sources_panel, 1, wx.EXPAND)
        col2_box.Add(self.connections_panel, 1, wx.EXPAND)
        col3_box.Add(self.destinations_panel, 1, wx.EXPAND)

        main_box.Fit(self)
        main_box.SetSizeHints(self)
        self.main_panel.SetSizer(main_box)

        # mapper object
        self.my_mapper = mymapper.MyMapper()

        # mapper poll
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(milliseconds=1000, oneShot=False)

        self.Show()

    def RefreshAll(self):
        self.sources_panel.RefreshAll()
        self.destinations_panel.RefreshAll()
        self.sources_panel.ExpandAll() #TODO: do not repeat code
        self.destinations_panel.ExpandAll()

    def redraw(self):
        wx.CallAfter(self.connections_panel.Refresh)

    def OnTimer(self, event):
        #self.connections_panel.DrawConnectionsLines()
        statusbar_text = str(len(self.my_mapper.getConnections())) + " connection(s)"
        self.statusbar.SetStatusText(statusbar_text)
        #self.RefreshAll()

    def OnSave(self, event):
        pass

    def OnLoad(self, event):
        pass

    def OnDelete(self, event):
        pass

    def OnConnect(self, event): #TODO: link just first connection
        self.my_mapper.setLink("/"+self.sources_panel.GetSignalAddress().split("/")[1], "/"+self.destinations_panel.GetSignalAddress().split("/")[1], {})
        self.my_mapper.setConnection(self.sources_panel.GetSignalAddress(), self.destinations_panel.GetSignalAddress(), action="connect", options={})
        self.connections_panel.DrawConnectionsLines()

    def OnDisconnect(self, event): #TODO: unlink if last connection
        self.my_mapper.setConnection(self.sources_panel.GetSignalAddress(), self.destinations_panel.GetSignalAddress(), action="disconnect", options={})
        self.connections_panel.DrawConnectionsLines()

    def OnDisconnectAll(self, event): #TODO: unlink if last connection
        for c in self.my_mapper.getConnections():
            self.my_mapper.setConnection(c["src_name"], c["dest_name"], action="disconnect", options={}) #TODO: unlink ?
        self.connections_panel.DrawConnectionsLines()

    def OnRefresh(self, event):
        self.RefreshAll()

    def OnExpandAll(self, event):
        self.sources_panel.ExpandAll()
        self.destinations_panel.ExpandAll()

    def OnCollapseAll(self, event): #FIXME: doesnt work :\
        self.sources_panel.CollapseAll()
        self.destinations_panel.CollapseAll()

    def OnQuit(self, event):
        self.Close(True)

class TestApp(wx.App, InspectionMixin):
   def OnInit(self):
       self.Init()
       mainFrame = MyFrame(None, title="pymapper", size=(1600, 768))
       self.SetTopWindow(mainFrame)
       mainFrame.Show()
       return 1

app = TestApp(0)
app.MainLoop()

#app = wx.App(False)
#frame = MyFrame(None, title="pymapper", size=(1400, 768))
#app.MainLoop()

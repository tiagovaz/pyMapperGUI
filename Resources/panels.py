import wx
import wx.gizmos
import mymapper
import math

class ConnectionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.my_mapper = mymapper.MyMapper()

    def OnSize(self, evt):
        wx.CallAfter(self.Refresh)

    def OnPaint(self, evt):
        self.DrawConnectionsLines()

    def Clear(self):
        self.dc.Clear()

    def DrawConnectionsLines(self):
        # loop source and dest trees to get y from each item connected
        conn_ids = []
        for c in self.my_mapper.getConnections():
            src = c["src_name"]
            dest = c["dest_name"]
            #TODO: draw red lines for linked devices
            src_item_id = self.GetParent().GetParent().sources_panel.GetItemByLabel(src, self.GetParent().GetParent().sources_panel.GetRootItem())
            dest_item_id = self.GetParent().GetParent().destinations_panel.GetItemByLabel(dest, self.GetParent().GetParent().destinations_panel.GetRootItem())
            conn_ids.append((src_item_id, dest_item_id))
        w,h = self.GetSize()
        self.dc = wx.PaintDC(self)
        gc = wx.GraphicsContext_Create(self.dc)
        self.dc.Clear()
        gc.SetPen(wx.Pen("blue", 1))
        for conn in conn_ids:
            y1 = self.GetParent().GetParent().sources_panel.getItemPos(conn[0])
            y2 = self.GetParent().GetParent().destinations_panel.getItemPos(conn[1])
            # +30 to compensate for the header row
            l = []
            y1 = y1[1]+y1[3]/2+26
            y2 = y2[1]+y2[3]/2+26
            for i in range(w):
                mu = float(i)/w
                mu2 = (1-math.cos(mu*math.pi))/2
                l.append([i, y1*(1-mu2)+y2*mu2])
            gc.DrawLines(l)
        wx.CallAfter(self.Refresh)

class MyTreeList(wx.Panel):
    def __init__(self, parent, id, which):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.my_mapper = mymapper.MyMapper()

        # sources or destinations tree
        self.which = which

        # Create the tree
        self.tree = wx.gizmos.TreeListCtrl(self, style =
                                           wx.TR_DEFAULT_STYLE
                                           | wx.TR_FULL_ROW_HIGHLIGHT
                                           | wx.TR_HAS_BUTTONS + wx.TR_HIDE_ROOT,
                                           size=(530, 600))

        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self.tree)
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.changed, self.tree)
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.changed, self.tree)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnItemChanged, self.tree)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        ### expand all
        expand_icon = wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, (16,16))
        expand_button = wx.BitmapButton(self, -1, expand_icon, (20, 20), (expand_icon.GetWidth()+10, expand_icon.GetHeight()+10))
        expand_button.SetToolTipString("This is a bitmap button.")
        self.Bind(wx.EVT_BUTTON, self.OnExpand, expand_button)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.tree, 1)

        # create some columns
        self.tree.AddColumn("Devices & signals")
        self.tree.AddColumn("type")
        self.tree.AddColumn("lengh")
        self.tree.AddColumn("units")
        self.tree.AddColumn("minimum")
        self.tree.AddColumn("maximum")
        self.tree.SetMainColumn(0) # the one with the tree in it...
        self.tree.SetColumnWidth(0, 200)
        self.tree.SetColumnWidth(1, 50)
        self.tree.SetColumnWidth(2, 50)
        self.tree.SetColumnWidth(3, 50)
        self.tree.SetColumnWidth(4, 80)

        # load the tree nodes
        self.RefreshAll()

        # Expand the first level by default
        self.tree.ExpandAll(self.root)


    def OnItemChanged(self, evt):
        # show the connection expression and src/dest min/max in the toolbar
        src = self.GetParent().GetParent().sources_panel.GetSignalAddress()
        dest = self.GetParent().GetParent().destinations_panel.GetSignalAddress()
        connection_data = self.my_mapper.getConnectionBySignalFullNames(src, dest)

        if connection_data is None:
            # disable controls
            self.GetParent().GetParent().mode_choice.Disable()
            self.GetParent().GetParent().mute_tool.Disable()
            self.GetParent().GetParent().expression_input.Disable()
            self.GetParent().GetParent().arrow_range.Disable()
            self.GetParent().GetParent().arrow_range2.Disable()
            self.GetParent().GetParent().src_range_label.Disable()
            self.GetParent().GetParent().src_range_min.Disable()
            self.GetParent().GetParent().src_range_max.Disable()
            self.GetParent().GetParent().dest_range_label.Disable()
            self.GetParent().GetParent().dest_range_min.Disable()
            self.GetParent().GetParent().dest_range_max.Disable()

            # set default values in the control panel
            self.GetParent().GetParent().expression_input.Clear()
            self.GetParent().GetParent().src_range_min.SetToDefaultValue()
            self.GetParent().GetParent().src_range_max.SetToDefaultValue()
            self.GetParent().GetParent().dest_range_min.SetToDefaultValue()
            self.GetParent().GetParent().dest_range_max.SetToDefaultValue()
        else:
            # enable controls
            self.GetParent().GetParent().mode_choice.Enable()
            self.GetParent().GetParent().mute_tool.Enable()
            self.GetParent().GetParent().expression_input.Enable()
            self.GetParent().GetParent().expression_y.Enable()
            self.GetParent().GetParent().arrow_range.Enable()
            self.GetParent().GetParent().arrow_range2.Enable()
            self.GetParent().GetParent().src_range_label.Enable()
            self.GetParent().GetParent().src_range_min.Enable()
            self.GetParent().GetParent().src_range_max.Enable()
            self.GetParent().GetParent().dest_range_label.Enable()
            self.GetParent().GetParent().dest_range_min.Enable()
            self.GetParent().GetParent().dest_range_max.Enable()

            # set connection values in the control panel
            src_min = connection_data["src_min"]
            src_max = connection_data["src_max"]
            dest_min = connection_data["dest_min"]
            dest_max = connection_data["dest_max"]
            if connection_data["muted"] == 1:
                self.GetParent().GetParent().mute_tool.SetValue(True)
            elif connection_data["muted"] == 0:
                self.GetParent().GetParent().mute_tool.SetValue(False)
            self.GetParent().GetParent().expression_input.SetValue(connection_data["expression"].split('=')[1])
            self.GetParent().GetParent().src_range_min.SetValue(src_min)
            self.GetParent().GetParent().src_range_max.SetValue(src_max)
            self.GetParent().GetParent().dest_range_min.SetValue(dest_min)
            self.GetParent().GetParent().dest_range_max.SetValue(dest_max)

        #TODO: toggle mute if connections is muted


    def changed(self, evt):
        self.GetParent().GetParent().redraw()

    def getItemPos(self, item):
        while not self.tree.IsVisible(item): # cool!
            item = self.tree.GetItemParent(item)
        return self.tree.GetBoundingRect(item)

    def getCurrentItem(self):
        return self.tree.GetCurrentItem()

    def OnActivate(self, evt):
        self.NewConnection()
        self.GetParent().GetParent().connections_panel.DrawConnectionsLines()

    def NewConnection(self):
        # set link and connection with libmapper
        # TODO: set link only if there's no link
        conns = self.my_mapper.getConnectionBySignalFullNames(self.GetParent().GetParent().sources_panel.GetSignalAddress(), self.GetParent().GetParent().destinations_panel.GetSignalAddress())
        if conns is None:
            self.my_mapper.setLink("/"+self.GetParent().GetParent().sources_panel.GetSignalAddress().split("/")[1], "/"+self.GetParent().GetParent().destinations_panel.GetSignalAddress().split("/")[1], {})
            self.my_mapper.Connect(self.GetParent().GetParent().sources_panel.GetSignalAddress(), self.GetParent().GetParent().destinations_panel.GetSignalAddress(), options={})
        else:
            self.my_mapper.Disconnect(self.GetParent().GetParent().sources_panel.GetSignalAddress(), self.GetParent().GetParent().destinations_panel.GetSignalAddress())

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())


    #TODO: put some brain here
    def AddTreeNodes(self, parentItem, items):
        for item in items:
            print item
            bg_color = 0
            if self.which == "destinations" and self.my_mapper.getInputsFromDevice(item):
                newItem = self.tree.AppendItem(parentItem, item)
                self.tree.SetItemBackgroundColour(newItem, "#D3D3D3")
                self.tree.SetItemBold(newItem)
                for i in self.my_mapper.getInputsFromDevice(item):
                    s_input = self.tree.AppendItem(newItem, i["name"])
                    if bg_color % 2 == 0:
                        self.tree.SetItemBackgroundColour(s_input, "#F5F5F5")
                    bg_color += 1
                    self.tree.SetItemText(s_input, i["type"], 1)
                    self.tree.SetItemText(s_input, str(i["length"]), 2)
                    self.tree.SetItemText(s_input, "", 3)
                    self.tree.SetItemText(s_input, str(i["min"]), 4)
                    self.tree.SetItemText(s_input, str(i["max"]), 5)

            elif self.which == "sources" and self.my_mapper.getOutputsFromDevice(item):
                newItem = self.tree.AppendItem(parentItem, item)
                self.tree.SetItemBackgroundColour(newItem, "#D3D3D3")
                self.tree.SetItemBold(newItem)
                for o in self.my_mapper.getOutputsFromDevice(item):
                    s_output = self.tree.AppendItem(newItem, o["name"])
                    if bg_color % 2 == 0:
                        self.tree.SetItemBackgroundColour(s_output, "#F5F5F5")
                    bg_color += 1
                    self.tree.SetItemText(s_output, o["type"], 1)
                    self.tree.SetItemText(s_output, str(o["length"]), 2)
                    self.tree.SetItemText(s_output, "", 3)
                    self.tree.SetItemText(s_output, str(o["min"]), 4)
                    self.tree.SetItemText(s_output, str(o["max"]), 5)

    def RefreshAll(self):
        # Add nodes (devices and their signals) to the trees
        # keep last devices list, compare with current and update if changed
        # same for removing item (DO NOT REBUILD ALL TREE)
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("") # hidden root
        self.devices = self.my_mapper.getAllDevices()
        self.AddTreeNodes(self.root, self.devices)
        self.tree.Refresh()


    def OnExpand(self, event):
        self.ExpandAll()

    def ExpandAll(self):
        self.tree.ExpandAll(self.root)

    def GetRootItem(self):
        return self.tree.GetRootItem()

    def CollapseAll(self): #TODO: Collapse doesnt work, why? Shouldn't be recursive?
        self.tree.Collapse(self.tree.GetRootItem())

    def OnCollapse(self, event):
        self.CollapseAll()

    def GetSelection(self):
        return self.tree.GetSelection()

    def GetSignalAddress(self): #TODO: make this more readable
        return str(self.tree.GetItemText(self.tree.GetItemParent(self.tree.GetSelection())) + self.tree.GetItemText(self.tree.GetSelection()))

    def GetItemText(self, item):
        if item:
            return self.tree.GetItemText(item)
        else:
            return ""

    def OnItemExpanded(self, evt):
        pass

    def OnItemCollapsed(self, evt):
        pass

    # HACK: better to store a dict{item_name: item_id} ??
    def GetItemByLabel(self, search_text, root_item):
        # receives as search_text a full libmapper address (ex: /device/signal)
        item, cookie = self.tree.GetFirstChild(root_item)
        while item.IsOk():
            text = self.tree.GetItemText(item)
            if text.lower() == search_text.lower():
                return item
            if self.tree.ItemHasChildren(item) and len(search_text.split("/")) > 2:
                string = "/"+"/".join(search_text.split("/")[2:])
                match = self.GetItemByLabel(string, item)
                # if parent is the device, since we can have same signal name for different devices
                if match.IsOk() and self.tree.GetItemText(self.tree.GetItemParent(match)) == "/"+search_text.split("/")[1]:
                    return match
            item, cookie = self.tree.GetNextChild(root_item, cookie)
        return wx.TreeItemId()

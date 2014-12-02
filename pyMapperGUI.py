#! /usr/bin/env python
# encoding: utf-8
"""
Copyright 2014 Tiago Bortoletto Vaz

This file is part of pyMapperGUI.

pyMapperGUI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyMapperGUI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyMapperGUI. If not, see <http://www.gnu.org/licenses/>.
"""

import wx
import netifaces
from wx.lib.mixins.inspection import InspectionMixin
from pymappergui.mymapper import MyMapper
# float spin for setting min/max values:
try:
    from agw import floatspin as FS
except ImportError:  # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.floatspin as FS
from pymappergui.panels import *
from pymappergui.dialogs import *
from pymappergui.storage import *
import os

class MyFrame(wx.Frame):
    def __init__(self, parent, title, size):
        wx.Frame.__init__(self, parent, -1, title=title, size=size)
        self.SetMinSize((1300, 600))

        # connections and expr preset files
        self.currentFile = None
        self.currentPresetFile = None

        # mapper object
        self.my_mapper = mymapper.MyMapper()
        self.modes_list = self.my_mapper.modes_dict.keys()
        self.boundaries_list = self.my_mapper.boundaries_dict.keys()

        # storage object
        self.mapper_storage = Storage()

        # network interfaces
        self.ifaces = netifaces.interfaces()

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
        icons_folder = "icons/"

        self.toolbar = self.CreateToolBar(wx.TB_FLAT)
        self.toolbar.SetToolBitmapSize((22, 22))  # sets icon size

        load_ico = wx.Bitmap(icons_folder + 'document-open.png')
        load_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, load_ico, "Open state file",
                                               "Open a state file")
        self.Bind(wx.EVT_MENU, self.OnOpen, load_tool)

        save_ico = wx.Bitmap(icons_folder + 'document-save-as.png')
        save_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, save_ico, "Save state file", "Saves the current connections")
        self.Bind(wx.EVT_MENU, self.OnSave, save_tool)

        self.toolbar.AddSeparator()

        ### refresh all
        refresh_ico = wx.Bitmap(icons_folder + 'view-refresh.png')
        refresh_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, refresh_ico, "Refresh",
                                                  "Refresh all devices, signals and connections.")
        self.Bind(wx.EVT_MENU, self.OnRefresh, refresh_tool)

        ### disconnect all
        disconnect_all_ico = wx.Bitmap(icons_folder + 'process-stop.png')
        disconnect_all_tool = self.toolbar.AddSimpleTool(wx.ID_ANY, disconnect_all_ico, "Disconnect all",
                                                         "Disconnects everything!")
        self.Bind(wx.EVT_MENU, self.OnDisconnectAll, disconnect_all_tool)

        self.toolbar.AddSeparator()

        # connections setup
        self.mode_choice = wx.Choice(self.toolbar, -1, (100, 50), choices=self.modes_list)
        self.mode_choice.SetToolTipString('Set the connection mode')
        self.mode_choice.Disable()
        self.toolbar.AddControl(self.mode_choice)
        self.Bind(wx.EVT_CHOICE, self.OnSetMode, self.mode_choice)

        # expression for mapping
        self.expression_y = wx.StaticText(self.toolbar, -1, " y = ")
        #self.expression_input = wx.TextCtrl(self.toolbar, -1, "",  style=wx.TE_PROCESS_ENTER, size=(220, 26))
        #self.expr_list = ['x - x{-1}', 'x + y{-1}', 'x * 0.01 + y{-1} * 0.99', 'y{-1} + 1']
        self.expr_list = []

        self.expression_input = wx.ComboBox(self.toolbar, -1, "", size=(220, 26),
                                            choices=self.expr_list, style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)

        self.expression_input.SetToolTipString('Type ENTER after writing your new expression')
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSetExpr, self.expression_input)
        self.expression_y.Disable()
        self.expression_input.Disable()
        self.toolbar.AddControl(self.expression_y)
        self.toolbar.AddControl(self.expression_input)

        # edit other connection parameters from a dialog
        self.edit_tool = wx.Button(self.toolbar, -1, "Edit all...", size=(60, 26))
        self.edit_tool.SetToolTipString('Edit connection parameters...')
        self.Bind(wx.EVT_BUTTON, self.OnEdit, self.edit_tool)

        # mute_ico = wx.Bitmap(icons_folder + 'audio-volume-muted-blocked-panel.png')
        self.mute_tool = wx.ToggleButton(self.toolbar, -1, "Mute", size=(50, 26))
        self.mute_tool.SetToolTipString('Mute/Unmute a connection')
        self.mute_tool.Disable()
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnMute, self.mute_tool)
        self.toolbar.AddControl(self.mute_tool)

        self.arrow_range = wx.StaticText(self.toolbar, -1, " - ")
        self.arrow_range.Disable()
        self.arrow_range2 = wx.StaticText(self.toolbar, -1, " - ")
        self.arrow_range2.Disable()

        # source / dest range input
        self.toolbar.AddSeparator()
        self.src_range_label = wx.StaticText(self.toolbar, -1, " Src. range: ")
        self.src_range_label.Disable()
        self.src_range_min = FS.FloatSpin(self.toolbar, -1, increment=0.01, agwStyle=FS.FS_CENTRE, size=(100, 26))
        self.src_range_min.Disable()
        self.src_range_min.SetFormat("%f")
        self.src_range_min.SetDigits(2)

        self.src_range_max = FS.FloatSpin(self.toolbar, -1, increment=0.01, agwStyle=FS.FS_CENTRE, size=(100, 26))
        self.src_range_max.Disable()
        self.src_range_max.SetFormat("%f")
        self.src_range_max.SetDigits(2)

        self.Bind(FS.EVT_FLOATSPIN, self.OnSetSourceMin, self.src_range_min)
        self.Bind(FS.EVT_FLOATSPIN, self.OnSetSourceMax, self.src_range_max)

        self.toolbar.AddControl(self.src_range_label)
        self.toolbar.AddControl(self.src_range_min)
        self.toolbar.AddControl(self.arrow_range)
        self.toolbar.AddControl(self.src_range_max)

        self.dest_range_label = wx.StaticText(self.toolbar, -1, " Dest. range: ")
        self.dest_range_label.Disable()
        self.dest_range_min = FS.FloatSpin(self.toolbar, -1, increment=0.01, agwStyle=FS.FS_CENTRE, size=(100, 26))
        self.dest_range_min.Disable()
        self.dest_range_min.SetFormat("%f")
        self.dest_range_min.SetDigits(2)

        self.dest_range_max = FS.FloatSpin(self.toolbar, -1, increment=0.01, agwStyle=FS.FS_CENTRE, size=(100, 26))
        self.dest_range_max.Disable()
        self.dest_range_max.SetFormat("%f")
        self.dest_range_max.SetDigits(2)

        self.Bind(FS.EVT_FLOATSPIN, self.OnSetDestMin, self.dest_range_min)
        self.Bind(FS.EVT_FLOATSPIN, self.OnSetDestMax, self.dest_range_max)

        self.toolbar.AddControl(self.dest_range_label)
        self.toolbar.AddControl(self.dest_range_min)
        self.toolbar.AddControl(self.arrow_range2)
        self.toolbar.AddControl(self.dest_range_max)

        self.toolbar.AddSeparator()

        self.toolbar.AddControl(self.edit_tool)

        ## statusbar
        self.statusbar = self.CreateStatusBar()

        ## menubar
        menu_bar = wx.MenuBar()
        menu1 = wx.Menu()
        menu1.Append(wx.ID_OPEN, "Open\tCtrl+O", "Open state file...")
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
        menu1.Append(wx.ID_SAVE, "Save\tCtrl+S", "Save current state file")
        self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
        menu1.Append(wx.ID_SAVEAS, "Save as...\tShift+Ctrl+S", "Save state file")
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=wx.ID_SAVEAS)
        menu1.AppendSeparator()
        menu1.Append(wx.ID_EXIT, "&Close", "Close application")
        self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
        menu_bar.Append(menu1, "&File")

        menu2 = wx.Menu()
        submenu_ifaces = wx.Menu()
        submenu_idx = 2011
        for i in self.ifaces:
            submenu_ifaces.Append(submenu_idx, i, "", wx.ITEM_RADIO)
            self.Bind(wx.EVT_MENU, self.OnIfaceMenu, id=submenu_idx)
            submenu_idx += 1
        menu2.AppendMenu(201, "Network interfaces", submenu_ifaces)
        menu2.Append(202, "Add OSC device", "Add OSC device")
        menu_bar.Append(menu2, "&Options")

        self.Bind(wx.EVT_MENU, self.OnAddOSCDevice, id=202)

        menu_expression = wx.Menu()
        menu_expression.Append(301, "Load preset...", "Open expression preset file...")
        self.Bind(wx.EVT_MENU, self.OnOpenPreset, id=301)
        menu_expression.Append(302, "Save preset...", "Save current expressions as a preset...")
        self.Bind(wx.EVT_MENU, self.OnSavePreset, id=302)
        menu_expression.Append(303, "Save preset as...", "Save current expressions as a new preset...")
        self.Bind(wx.EVT_MENU, self.OnSaveAsPreset, id=303)
        menu_bar.Append(menu_expression, "&Expressions")

        menu3 = wx.Menu()
        menu3.Append(401, "&Docs", "Documentation")
        menu3.Append(402, "&About", "About")
        menu_bar.Append(menu3, "&Help",)

        self.Bind(wx.EVT_MENU, self.OnAboutBox, id=402)

        self.SetMenuBar(menu_bar)

        ## source/destination search
        self.sources_search = wx.SearchCtrl(self.main_panel, size=(240, 21), style=wx.TE_PROCESS_ENTER)
        self.destinations_search = wx.SearchCtrl(self.main_panel, size=(240, 21), style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT, self.OnSourcesSearch, self.sources_search)
        self.Bind(wx.EVT_TEXT, self.OnDestinationsSearch, self.destinations_search)

        ## expand/collapse controls
        expand_icon = wx.Bitmap(icons_folder + 'expand.png')
        collapse_icon = wx.Bitmap(icons_folder + 'collapse.png')

        ### expand all src
        expand_src_button = wx.BitmapButton(self.main_panel, -1, expand_icon, (16, 16),
                                            (expand_icon.GetWidth() + 5, expand_icon.GetHeight() + 5))
        expand_src_button.SetToolTipString("Expand all")
        self.Bind(wx.EVT_BUTTON, self.sources_panel.OnExpand, expand_src_button)

        ### expand all dest
        expand_dest_button = wx.BitmapButton(self.main_panel, -1, expand_icon, (16, 16),
                                             (expand_icon.GetWidth() + 5, expand_icon.GetHeight() + 5))
        expand_dest_button.SetToolTipString("Expand all")
        self.Bind(wx.EVT_BUTTON, self.destinations_panel.OnExpand, expand_dest_button)

        ### collapse all src
        collapse_src_button = wx.BitmapButton(self.main_panel, -1, collapse_icon, (16, 16),
                                              (collapse_icon.GetWidth() + 5, collapse_icon.GetHeight() + 18))
        collapse_src_button.SetToolTipString("Collapse all")
        self.Bind(wx.EVT_BUTTON, self.sources_panel.OnCollapse, collapse_src_button)

        ### collapse all dest
        collapse_dest_button = wx.BitmapButton(self.main_panel, -1, collapse_icon, (16, 16),
                                               (collapse_icon.GetWidth() + 5, collapse_icon.GetHeight() + 18))
        collapse_dest_button.SetToolTipString("Collapse all")
        self.Bind(wx.EVT_BUTTON, self.destinations_panel.OnCollapse, collapse_dest_button)

        ################ layout #########################################

        ## sizers
        main_box = wx.BoxSizer(wx.VERTICAL)
        h_box = wx.BoxSizer(wx.HORIZONTAL)
        main_box.Add(wx.StaticLine(self.main_panel, ), 0, wx.ALL | wx.EXPAND, 5)
        main_box.Add(h_box, 1, wx.EXPAND)

        sources_label_box = wx.BoxSizer(wx.HORIZONTAL)
        destinations_label_box = wx.BoxSizer(wx.HORIZONTAL)
        connections_label_box = wx.BoxSizer(wx.HORIZONTAL)

        sources_label_box.Add(sources_label, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        sources_label_box.Add(expand_src_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        sources_label_box.Add(collapse_src_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        sources_label_box.Add((10, 10))
        sources_label_box.Add(self.sources_search, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        connections_label_box.Add(conn_label, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        destinations_label_box.Add(destinations_label, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        destinations_label_box.Add(expand_dest_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        destinations_label_box.Add(collapse_dest_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        destinations_label_box.Add((10, 10))
        destinations_label_box.Add(self.destinations_search, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

        ## trees
        col1_box = wx.BoxSizer(wx.VERTICAL)
        col2_box = wx.BoxSizer(wx.VERTICAL)
        col3_box = wx.BoxSizer(wx.VERTICAL)

        h_box.Add(col1_box, 2, wx.ALL | wx.EXPAND)
        h_box.Add(col2_box, 1, wx.ALL | wx.EXPAND)
        h_box.Add(col3_box, 2, wx.ALL | wx.EXPAND)

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

        self.main_panel.SetSizerAndFit(main_box)

        # mapper poll
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(milliseconds=1000, oneShot=False)

        self.Centre()
        self.Show()

    def OnSourcesSearch(self, event):
        text = event.GetString()
        root = self.sources_panel.tree.GetRootItem()
        item = self.sources_panel.GetItemByLabel(text, root)
        self.sources_panel.tree.EnsureVisible(item)
        try:
            self.sources_panel.tree.SelectItem(item)
        except:
            pass #FIXME: do something

    def OnDestinationsSearch(self, event):
        text = event.GetString()
        root = self.destinations_panel.tree.GetRootItem()
        item = self.destinations_panel.GetItemByLabel(text, root)
        self.destinations_panel.tree.EnsureVisible(item)
        try:
            self.destinations_panel.tree.SelectItem(item)
        except:
            pass #FIXME: do something




    def OnMute(self, event):
        if self.mute_tool.GetValue() is True:
            is_muted = True
        else:
            is_muted = False
        self.my_mapper.Modify(self.sources_panel.GetSignalAddress(),
                              self.destinations_panel.GetSignalAddress(),
                              options={'muted': is_muted})

    def OnEdit(self, event):
        if len(self.my_mapper.getConnections()) == 0:
            wx.MessageBox('No connection found', 'Info', wx.OK | wx.ICON_ERROR)
        else:
            dlg = EditConnections(self, -1, "Edit connection parameters", size=(450, 300),
                             #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
                             style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
                             useMetal=False,
                             )
            dlg.CenterOnScreen()
            # this does not return until the dialog is closed.
            val = dlg.ShowModal()
            dlg.Destroy()

    def OnSetExpr(self, event):
        expression = 'y=' + self.expression_input.GetValue()
        self.my_mapper.Modify(self.sources_panel.GetSignalAddress(),
                              self.destinations_panel.GetSignalAddress(),
                              options={'expression': str(expression)})

    def OnSetMode(self, event):
        mode_str = event.GetString()
        mode_mapper_index = self.my_mapper.modes_dict[mode_str]
        self.my_mapper.Modify(self.sources_panel.GetSignalAddress(),
                              self.destinations_panel.GetSignalAddress(),
                              options={'mode': mode_mapper_index})
        if mode_mapper_index == self.my_mapper.mo_expression:
            self.expression_input.Enable()
            self.expression_y.Enable()
        #            self.set_expr_tool.Enable()
        else:
            self.expression_input.Disable()
            self.expression_y.Disable()
        #            self.set_expr_tool.Disable()
        # update expression after changing mode
        connection_data = self.my_mapper.getConnectionBySignalFullNames(self.sources_panel.GetSignalAddress(),
                                                                        self.destinations_panel.GetSignalAddress())
        self.expression_input.SetValue(connection_data["expression"].split('=')[1])

    def OnSetSourceMin(self, event):
        f = event.GetEventObject().GetValue()
        print f
        self.my_mapper.Modify(self.sources_panel.GetSignalAddress(),
                              self.destinations_panel.GetSignalAddress(),
                              options={'src_min': f})

    def OnSetSourceMax(self, event):
        f = event.GetEventObject().GetValue()
        print f
        self.my_mapper.Modify(self.sources_panel.GetSignalAddress(),
                              self.destinations_panel.GetSignalAddress(),
                              options={'src_max': f})

    def OnSetDestMin(self, event):
        f = event.GetEventObject().GetValue()
        self.my_mapper.Modify(self.sources_panel.GetSignalAddress(),
                              self.destinations_panel.GetSignalAddress(),
                              options={'dest_min': f})

    def OnSetDestMax(self, event):
        f = event.GetEventObject().GetValue()
        self.my_mapper.Modify(self.sources_panel.GetSignalAddress(),
                              self.destinations_panel.GetSignalAddress(),
                              options={'dest_max': f})

    def OnAboutBox(self, e):

        description = """PyMapperGUI is a cross-platform graphical interface for managing libmapper sessions (http://libmapper.github.io/)"""

        licence = """PyMapperGUI is free software; you can redistribute
it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of the License,
or (at your option) any later version.

PyMapper is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details. You should have
received a copy of the GNU General Public License along with PyMapper;
if not, write to the Free Software Foundation, Inc., 59 Temple Place,
Suite 330, Boston, MA  02111-1307  USA"""

        info = wx.AboutDialogInfo()

   #     info.SetIcon(wx.Icon('pymapper.png', wx.BITMAP_TYPE_PNG))
        info.SetName('PyMapperGUI')
        info.SetVersion('1.0beta1')
        info.SetDescription(description)
        info.SetCopyright('(C) 2014 Tiago Bortoletto Vaz <tiago@debian.org>')
        info.SetWebSite('https://github.com/tiagovaz/pymapper')
        info.SetLicence(licence)
        #info.AddDeveloper('Tiago Bortoletto Vaz')
        #info.AddDocWriter('')
        #info.AddArtist('')
        #info.AddTranslator('')

        wx.AboutBox(info)

    def OnAddOSCDevice(self, evt):
        dlg = AddOSCDevice(self, -1, "Sample Dialog", size=(350, 200),
                         #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
                         style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
                         useMetal=False,
                         )
        dlg.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()

        #FIXME: broken
        if val == wx.ID_OK:
            self.t = self.my_mapper.createDevice("test")

        dlg.Destroy()

    def RefreshAll(self):
        wx.CallAfter(self.sources_panel.RefreshAll)
        wx.CallAfter(self.destinations_panel.RefreshAll)
#        wx.CallAfter(self.sources_panel.ExpandAll)
#        wx.CallAfter(self.destinations_panel.ExpandAll)
        self.redraw()

    # redraw the connections
    # try to call inside a Timer
    def redraw(self):
        wx.CallAfter(self.connections_panel.Refresh)

    def OnTimer(self, event):
        statusbar_text = str(len(self.my_mapper.getConnections())) + " connection(s)"
        self.statusbar.SetStatusText(statusbar_text)
        self.RefreshAll()
        self.my_mapper.poll(10)

    def OnSaveAs(self, event):
        wildcard = "PyMapper file (.pym)|*.pym"
        dlg = wx.FileDialog(self, "Save file as...", os.path.expanduser("~"), "connections.pym",
                            wildcard=wildcard, style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.currentFile = path # useful for OnSave()
            self.SetTitle("pyMapper - %s" % path)
            f = open(path, "w")
            f.write(str(self.mapper_storage.serialise(self.my_mapper.mon, self.my_mapper.getAllDevices())))
            f.close()
        dlg.Destroy()

    def OnSave(self, event):
        if self.currentFile == None:
            self.OnSaveAs(event)
        else:
            f = open(self.currentFile, "w")
            f.write(str(self.mapper_storage.serialise(self.my_mapper.mon, self.my_mapper.getAllDevices())))
            f.close()

    def OnOpen(self, event):
        wildcard = "pyMapper file (.pym)|*.pym"
        dlg = wx.FileDialog(self, "Open pyMapper file...", os.path.expanduser("~"), 
                            wildcard=wildcard, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path == "":
                return
            self.currentFile = path
            self.SetTitle("pyMapper - %s" % os.path.split(path)[1])
            f = open(path, "r")
            text = f.read()
            f.close()
            devices_list = self.my_mapper.getInputOutputDevices()
            self.mapper_storage.deserialise(self.my_mapper.mon, text, devices_list)
        dlg.Destroy()

    def OnOpenPreset(self, event):
        wildcard = "pyMapper file (.pre)|*.pre"
        dlg = wx.FileDialog(self, "Open preset file...", os.path.expanduser("~"),
                            wildcard=wildcard, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path == "":
                return
            self.currentPresetFile = path
            self.SetTitle("pyMapper - %s" % os.path.split(path)[1])
            f = open(path, "r")
            text = f.read()
            f.close()
            self.expr_list = eval(text)
            self.expression_input.Clear()
            self.expression_input.AppendItems(self.expr_list)
        dlg.Destroy()

    def OnSavePreset(self, event):
        if self.currentPresetFile == None:
            self.OnSaveAsPreset(event)
        else:
            f = open(self.currentPresetFile, "w")
            f.write(str(self.expr_list))
            f.close()

    def OnSaveAsPreset(self, event):
        wildcard = "PyMapper expression preset file (.pre)|*.pre"
        dlg = wx.FileDialog(self, "Save file as...", os.path.expanduser("~"), "expressions.pre",
                            wildcard=wildcard, style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.currentFile = path # useful for OnSave()
            self.SetTitle("pyMapper - %s" % path)
            f = open(path, "w")
            f.write(str(self.expr_list))
            f.close()
        dlg.Destroy()

    def OnDelete(self, event):
        pass

    def OnConnect(self, event):
        self.my_mapper.setLink("/" + self.sources_panel.GetSignalAddress().split("/")[1],
                               "/" + self.destinations_panel.GetSignalAddress().split("/")[1], {})
        self.my_mapper.Connect(self.sources_panel.GetSignalAddress(),
                               self.destinations_panel.GetSignalAddress())
        self.connections_panel.DrawConnectionsLines()

    def OnDisconnect(self, event):
        self.my_mapper.Disconnect(self.sources_panel.GetSignalAddress(),
                                  self.destinations_panel.GetSignalAddress())
        self.connections_panel.DrawConnectionsLines()

    def OnDisconnectAll(self, event):
        for c in self.my_mapper.getConnections():
            self.my_mapper.Disconnect(c["src_name"], c["dest_name"])
        self.connections_panel.DrawConnectionsLines()

    def OnRefresh(self, event):
        self.RefreshAll()

    def OnExpandAll(self, event):
        self.sources_panel.ExpandAll()
        self.destinations_panel.ExpandAll()

    def OnCollapseAll(self, event):  #FIXME: for some reason it doesnt work :\
        self.sources_panel.CollapseAll()
        self.destinations_panel.CollapseAll()

    def OnIfaceMenu(self, event):
        e = event.GetEventObject()
        i = event.GetId()
        self.my_mapper.setNetworkInterface(iface=str(e.GetLabel(i))) #FIXME: doesn't refresh properly

    def OnQuit(self, event):
        self.Close(True)


class TestApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init()
        mainFrame = MyFrame(None, title="pyMapperGUI")
        self.SetTopWindow(mainFrame)
        mainFrame.Show()
        return 1

#app = TestApp(0)
#app.MainLoop()

app = wx.App(False)
frame = MyFrame(None, title="pyMapperGUI", size=(1300, 600))
app.MainLoop()

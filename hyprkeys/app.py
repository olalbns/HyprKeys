from __future__ import annotations
import os, shutil, subprocess
from datetime import datetime
from pathlib import Path
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .parser import Binding, category, parse
APP_ID="io.github.olalbns.hyprkeys"
DEFAULT=Path.home()/".config/hypr/hyprland.conf"

class Window(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="HyprKeys")
        self.path=DEFAULT; self.bindings=[]; self.categories="All"; self.duplicates=False
        self.set_default_size(800, 620)
        root=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=16, margin_bottom=16, margin_start=16, margin_end=16); self.set_child(root)
        title=Gtk.Label(label="HyprKeys", xalign=0); title.add_css_class("title-1"); root.append(title)
        subtitle=Gtk.Label(label="Explore, search, and detect duplicate Hyprland shortcuts", xalign=0); subtitle.add_css_class("dim-label"); root.append(subtitle)
        controls=Gtk.Box(spacing=8); root.append(controls)
        self.search=Gtk.SearchEntry(placeholder_text="Search key, command, action, or comment…", hexpand=True); self.search.connect("search-changed", lambda _w:self.render()); controls.append(self.search)
        self.filter=Gtk.ComboBoxText(); [self.filter.append_text(item) for item in ("All", "Windows", "Workspaces", "Media", "System", "Other")]; self.filter.set_active(0); self.filter.connect("changed", self.category_changed); controls.append(self.filter)
        dup=Gtk.ToggleButton(label="Duplicates only"); dup.connect("toggled", self.duplicates_changed); controls.append(dup)
        for label, callback in (("Add shortcut", self.add_shortcut), ("Reload list", self.reload), ("Open config", self.open_config), ("Reload Hyprland", self.reload_hyprland)):
            button=Gtk.Button(label=label); button.connect("clicked", lambda _b, fn=callback:fn()); controls.append(button)
        self.list=Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE); scroll=Gtk.ScrolledWindow(vexpand=True); scroll.set_child(self.list); root.append(scroll)
        self.status=Gtk.Label(xalign=0, wrap=True); self.status.add_css_class("dim-label"); root.append(self.status)
        self.reload()
    def reload(self):
        try:
            self.bindings=parse(self.path)
            self.status.set_text(f"{len(self.bindings)} shortcuts found in {self.path} and sourced files.")
            self.render()
        except OSError as error:self.status.set_text(f"Unable to read configuration: {error}")
    def category_changed(self, widget): self.categories=widget.get_active_text() or "All"; self.render()
    def duplicates_changed(self, widget): self.duplicates=widget.get_active(); self.render()
    def duplicates_set(self):
        counts={}
        for binding in self.bindings: counts[binding.identity]=counts.get(binding.identity, 0)+1
        return {key for key, count in counts.items() if count>1}
    def render(self):
        while (child:=self.list.get_first_child()) is not None:self.list.remove(child)
        text=self.search.get_text().lower(); duplicate=self.duplicates_set(); visible=0
        for binding in self.bindings:
            fields=" ".join((binding.shortcut,binding.dispatcher,binding.argument,binding.comment,binding.source)).lower()
            if text and text not in fields: continue
            if self.categories!="All" and category(binding.dispatcher,binding.argument)!=self.categories: continue
            if self.duplicates and binding.identity not in duplicate: continue
            self.list.append(self.row(binding, binding.identity in duplicate)); visible+=1
        if not visible:self.status.set_text("No shortcuts match this filter.")
    def row(self, binding: Binding, duplicate: bool):
        row=Gtk.Box(spacing=12, margin_top=7, margin_bottom=7, margin_start=10, margin_end=10)
        key=Gtk.Label(label=binding.shortcut, xalign=0, width_chars=20); key.add_css_class("heading"); row.append(key)
        details=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, hexpand=True)
        action=Gtk.Label(label=f"{binding.dispatcher}  {binding.argument}".strip(), xalign=0, ellipsize=3); details.append(action)
        extra=f"{category(binding.dispatcher,binding.argument)} · {Path(binding.source).name}:{binding.line}"
        if binding.comment: extra+=f" · {binding.comment}"
        meta=Gtk.Label(label=extra, xalign=0, ellipsize=3); meta.add_css_class("dim-label"); details.append(meta); row.append(details)
        if duplicate:
            badge=Gtk.Label(label="Duplicate"); badge.add_css_class("error"); row.append(badge)
        return row
    def add_shortcut(self):
        """Open a small form and append a valid bind line to hyprland.conf."""
        dialog=Gtk.Dialog(title="Add Hyprland shortcut", transient_for=self, modal=True)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL); dialog.add_button("Add shortcut", Gtk.ResponseType.ACCEPT)
        content=dialog.get_content_area(); content.set_spacing(10); content.set_margin_top(14); content.set_margin_bottom(14); content.set_margin_start(14); content.set_margin_end(14)
        grid=Gtk.Grid(column_spacing=10, row_spacing=8); content.append(grid)
        kind=Gtk.ComboBoxText(); [kind.append_text(item) for item in ("bind", "bindl", "bindel", "bindm", "binde")]; kind.set_active(0)
        modifiers=Gtk.Entry(text="$mainMod", placeholder_text="$mainMod or SUPER SHIFT")
        key=Gtk.Entry(placeholder_text="RETURN, Q, XF86AudioRaiseVolume…")
        dispatcher=Gtk.Entry(text="exec", placeholder_text="exec, workspace, killactive…")
        argument=Gtk.Entry(placeholder_text="kitty, 1, or another dispatcher argument")
        comment=Gtk.Entry(placeholder_text="Optional description")
        fields=(("Binding type",kind),("Modifiers",modifiers),("Key",key),("Dispatcher",dispatcher),("Argument",argument),("Comment",comment))
        for row,(label,widget) in enumerate(fields): grid.attach(Gtk.Label(label=label, xalign=0),0,row,1,1); grid.attach(widget,1,row,1,1)
        dialog.connect("response", self.save_shortcut, kind, modifiers, key, dispatcher, argument, comment)
        dialog.present()
    def save_shortcut(self, dialog, response, kind, modifiers, key, dispatcher, argument, comment):
        if response!=Gtk.ResponseType.ACCEPT: dialog.destroy(); return
        values=[modifiers.get_text().strip(), key.get_text().strip(), dispatcher.get_text().strip(), argument.get_text().strip(), comment.get_text().strip()]
        if not all(values[:3]) or any("\n" in value or "\r" in value for value in values):
            self.status.set_text("Modifiers, key, and dispatcher are required; line breaks are not allowed."); dialog.destroy(); return
        binding_kind=kind.get_active_text() or "bind"
        line=f"{binding_kind} = {values[0]}, {values[1]}, {values[2]}"
        if values[3]: line+=f", {values[3]}"
        if values[4]: line+=f" # {values[4]}"
        try:
            if not self.path.is_file(): raise OSError(f"Configuration not found: {self.path}")
            stamp=datetime.now().strftime("%Y%m%d-%H%M%S")
            backup=self.path.with_name(f"{self.path.name}.hyprkeys-{stamp}.bak")
            shutil.copy2(self.path, backup)
            with self.path.open("a", encoding="utf-8") as config: config.write("\n# Added by HyprKeys\n"+line+"\n")
            self.status.set_text(f"Shortcut added. Backup created: {backup.name}. Click Reload Hyprland to apply it.")
            self.reload()
        except OSError as error:self.status.set_text(f"Unable to save shortcut: {error}")
        dialog.destroy()
    def open_config(self):
        try:
            subprocess.Popen(["xdg-open", str(self.path)])
        except FileNotFoundError:
            self.status.set_text("xdg-open is unavailable.")
    def reload_hyprland(self):
        try:
            subprocess.run(["hyprctl", "reload"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True); self.status.set_text("Hyprland configuration reloaded.")
        except (FileNotFoundError, subprocess.CalledProcessError) as error:self.status.set_text(f"Unable to reload Hyprland: {error}")
class App(Gtk.Application):
    def __init__(self):super().__init__(application_id=APP_ID)
    def do_activate(self):(self.props.active_window or Window(self)).present()
def main():App().run(None)
if __name__=="__main__":main()

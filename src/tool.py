import dearpygui.dearpygui as dpg
import components.server.entry_list as EntryList

dpg.create_context()

with dpg.window(tag="Primary Window"):
    with dpg.tab_bar():
        with dpg.tab(label="Client"):
            dpg.add_spacer(height=5)
            dpg.add_text("Nothing here yet")
        with dpg.tab(label="Server"):
            dpg.add_spacer(height=5)
            with dpg.tab_bar():
                with dpg.tab(label="entry_list"):
                    dpg.add_spacer(height=10)
                    entry_list = EntryList.EntryList()
                

dpg.create_viewport(title='ACToolbox', width=700, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
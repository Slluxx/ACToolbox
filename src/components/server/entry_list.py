import dearpygui.dearpygui as dpg
import configparser
import random, os, uuid


class EntryList:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.optionxform = str

        self.selectedEntryIniPath = ""
        self.selectedLocalCarPath = ""
        self.loadedCars = []

        self.gui()

    def gui(self):
        dpg.add_text(
            "Load an INI file before doing anything else, even if its empty.", wrap=0
        )
        dpg.add_text(
            "You can not edit multiple cars at the same time. Save before you select another.",
            wrap=0,
        )
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Load INI",
                width=100,
                callback=lambda: dpg.show_item("file_dialog_id"),
            )
            dpg.add_combo(
                tag="item_names",
                items=(),
                label="",
                width=392,
                callback=lambda s, d, u: self.combo_callback(s, d, u),
            )

        with dpg.group():
            # dpg.add_input_int(tag="curr_car_nr", label="Number", enabled=False)
            dpg.add_input_text(tag="curr_car_model", label="Model", width=500)
            dpg.add_input_text(tag="curr_car_skin", label="Skin", width=500)
            dpg.add_input_int(
                tag="curr_car_specMode",
                label="Spectator Mode",
                width=500,
                min_value=0,
                max_value=1,
                min_clamped=True,
                max_clamped=True,
                
            )
            dpg.add_input_text(
                tag="curr_car_driverName", label="Driver Name", width=500
            )
            dpg.add_input_text(tag="curr_car_team", label="Team", width=500)
            dpg.add_input_text(tag="curr_car_guid", label="GUID", width=500)
            dpg.add_input_int(tag="curr_car_ballast", label="Ballast", width=500)
            dpg.add_input_int(tag="curr_car_restrictor", label="Restrictor", width=500)
            dpg.add_button(
                label="Remove selected",
                callback=lambda s, d, u: self.btn_callback_remove(s, d, u),
                width=500,
            )

            dpg.add_separator()
            dpg.add_spacer(height=10)

            dpg.add_button(
                label="Load local cars",
                callback=lambda: dpg.show_item("folder_dialog_id"),
                width=500,
            )
            dpg.add_combo(tag="local_cars", items=(), label="", width=500)
            dpg.add_combo(tag="local_skins", items=(), label="", width=500)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Add selected",
                    callback=lambda s, d, u: self.btn_callback_addFromFolder(s, d, u),
                    width=246,
                )
                dpg.add_button(
                    label="Add blank",
                    callback=lambda s, d, u: self.btn_callback_addBlank(s, d, u),
                    width=246,
                )

            dpg.add_separator()
            dpg.add_spacer(height=10)

            dpg.add_button(
                label="Save changes",
                callback=lambda s, d, u: self.btn_callback_save(s, d, u),
                width=500,
            )

        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=lambda s, d, u: self.fileDialog_OkCallback(s, d, u),
            id="file_dialog_id",
            width=500,
            height=400,
            modal=True,
        ):
            dpg.add_file_extension(".ini")

        defaultPath = ""
        drives = ["C:\\", "D:\\", "E:\\", "F:\\", "G:\\"]
        path = "Program Files (x86)\\Steam\\steamapps\\common\\assettocorsa\\content\\cars"
        for drive in drives:
            if os.path.exists(drive + path):
                defaultPath = drive + path
                break

        with dpg.file_dialog(
            label="Select a car folder",
            directory_selector=True,
            show=False,
            callback=lambda s, d, u: self.folderDialog_OkCallback(s, d, u),
            id="folder_dialog_id",
            width=500,
            height=400,
            modal=True,
            default_path=defaultPath,
        ):
            pass

        with dpg.window(
            label="Error",
            modal=True,
            show=False,
            tag="error_modal",
            no_title_bar=True,
            width=250,
            height=100,
        ):
            dpg.add_text(tag="error_text", label="", wrap=0)
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="OK",
                    width=-1,
                    callback=lambda: dpg.configure_item("error_modal", show=False),
                )

    def gui_update_carComboBox(self, default=None):
        """
        value = dpg.get_value("item_names")
        items = dpg.get_item_configuration("item_names")["items"]
        try:
            index = items.index(value)
        except Exception as e:
            print(e)
            return
        """
        
        cars_processedNames = [
            f"{car['MODEL']} ({car['_ACTOOL_GUID']})" for car in self.loadedCars
        ]
        
        defaultValue = ""
        if len(cars_processedNames) > 0:
            defaultValue = cars_processedNames[0]
        if default != None:
            defaultValue = default

        print(default, defaultValue)
            
        dpg.configure_item(
            "item_names",
            items=cars_processedNames,
            default_value=defaultValue,
        )
        # self.gui_update_current_car(self.loadedCars[index])

    def gui_update_current_car(self, car):
        if car == None:
            car = {}
        dpg.set_value("curr_car_model", car.get("MODEL", ""))
        dpg.set_value("curr_car_skin", car.get("SKIN", ""))
        dpg.set_value("curr_car_specMode", int(car.get("SPECTATOR_MODE", 0)))
        dpg.set_value("curr_car_driverName", car.get("DRIVERNAME", ""))
        dpg.set_value("curr_car_team", car.get("TEAM", ""))
        dpg.set_value("curr_car_guid", car.get("GUID", ""))
        dpg.set_value("curr_car_ballast", int(car.get("BALLAST", 0)))
        dpg.set_value("curr_car_restrictor", int(car.get("RESTRICTOR", 0)))

    def gui_update_error_modal(self, text="", show=True):
        dpg.set_value("error_text", text)
        dpg.configure_item(
            "error_text",
            label=text,
            wrap=0,
        )
        dpg.configure_item("error_modal", show=show)
        dpg.set_item_pos(
            "error_modal",
            [
                int(
                    (
                        dpg.get_item_width("Primary Window") / 2
                        - dpg.get_item_width("error_modal") / 2
                    )
                ),
                int(
                    (
                        dpg.get_item_height("Primary Window") / 2
                        - dpg.get_item_height("error_modal") / 2
                    )
                ),
            ],
        )

    def combo_callback(self, sender, data, user_data):
        value = dpg.get_value("item_names")
        items = dpg.get_item_configuration("item_names")["items"]
        try:
            index = items.index(value)
        except Exception as e:
            print(e)
            return

        self.gui_update_current_car(self.loadedCars[index])

    def btn_callback_save(self, sender, data, user_data):
        value = dpg.get_value("item_names")
        items = dpg.get_item_configuration("item_names")["items"]
        try:
            index = items.index(value)
        except:
            self.save_ini(self.loadedCars)
            return

        self.loadedCars[index]["MODEL"] = dpg.get_value("curr_car_model")
        self.loadedCars[index]["SKIN"] = dpg.get_value("curr_car_skin")
        self.loadedCars[index]["SPECTATOR_MODE"] = dpg.get_value("curr_car_specMode")
        self.loadedCars[index]["DRIVERNAME"] = dpg.get_value("curr_car_driverName")
        self.loadedCars[index]["TEAM"] = dpg.get_value("curr_car_team")
        self.loadedCars[index]["GUID"] = dpg.get_value("curr_car_guid")
        self.loadedCars[index]["BALLAST"] = dpg.get_value("curr_car_ballast")
        self.loadedCars[index]["RESTRICTOR"] = dpg.get_value("curr_car_restrictor")

        self.save_ini(self.loadedCars)

    def btn_callback_remove(self, sender, data, user_data):
        value = dpg.get_value("item_names")
        items = dpg.get_item_configuration("item_names")["items"]
        try:
            index = items.index(value)
            if self.loadedCars[index]:
                self.loadedCars.pop(index)
        except Exception as e:
            print(e)
            return

        if len(self.loadedCars) == 0:
            dpg.configure_item("item_names", label="", items=[], default_value="")
            self.gui_update_current_car(None)
            return

        self.gui_update_carComboBox()
        self.gui_update_current_car(self.loadedCars[0])

    def btn_callback_addFromFolder(self, sender, data, user_data):
        localCar = dpg.get_value("local_cars")
        localCarSkin = dpg.get_value("local_skins")

        if localCar == "" or localCarSkin == "":
            self.gui_update_error_modal("Please select a car and skin.", True)
            return

        newCar = {
            "_ACTOOL_GUID": str(uuid.uuid4())[:8],
            "MODEL": localCar,
            "SKIN": localCarSkin + "/ACA3",
            "SPECTATOR_MODE": 0,
            "DRIVERNAME": "",
            "TEAM": "",
            "GUID": "",
            "BALLAST": 0,
            "RESTRICTOR": 0,
        }
        
        self.loadedCars.append(newCar)
        index = self.loadedCars.index(newCar)
        
        """
        cars_processedNames = [
            f"{car['MODEL']} ({car['_ACTOOL_GUID']})" for car in self.loadedCars
        ]
        defaultValue = cars_processedNames[0] if len(cars_processedNames) > 0 else ""

        dpg.configure_item(
            "item_names",
            items=cars_processedNames,
            default_value=defaultValue,
        )
        """
        print("Update combo", f"{newCar['MODEL']} ({newCar['_ACTOOL_GUID']})")
        self.gui_update_current_car(self.loadedCars[index])
        self.gui_update_carComboBox(default=f"{newCar['MODEL']} ({newCar['_ACTOOL_GUID']})")

    def btn_callback_addBlank(self, sender, data, user_data):

        newCar = {
            "_ACTOOL_GUID": str(uuid.uuid4())[:8],
            "MODEL": "MyNewCarModel",
            "SKIN": "MyNewCarSkin/ACA3",
            "SPECTATOR_MODE": 0,
            "DRIVERNAME": "",
            "TEAM": "",
            "GUID": "",
            "BALLAST": 0,
            "RESTRICTOR": 0,
        }
        self.loadedCars.append(newCar)
        index = self.loadedCars.index(newCar)
        
        cars_processedNames = [
            f"{car['MODEL']} ({car['_ACTOOL_GUID']})" for car in self.loadedCars
        ]
        defaultValue = cars_processedNames[index] if len(cars_processedNames) > 0 else ""

        dpg.configure_item(
            "item_names",
            items=cars_processedNames,
            default_value=defaultValue,
        )
        self.gui_update_current_car(self.loadedCars[index])

    def fileDialog_OkCallback(self, sender, app_data, user_data):
        self.load_ini(app_data["file_path_name"])

        if len(self.loadedCars) == 0:
            return

        cars_processedNames = [
            f"{car['MODEL']} ({car['_ACTOOL_GUID']})" for car in self.loadedCars
        ]
        defaultValue = cars_processedNames[0] if len(cars_processedNames) > 0 else ""

        dpg.configure_item(
            "item_names",
            items=cars_processedNames,
            default_value=defaultValue,
        )
        self.gui_update_current_car(self.loadedCars[0])

    def folderDialog_OkCallback(self, sender, app_data, user_data):
        self.selectedLocalCarPath = app_data["file_path_name"]

        folders_with_matching_kn5 = [
            folder
            for folder in os.listdir(self.selectedLocalCarPath)
            if os.path.exists(
                os.path.join(self.selectedLocalCarPath, folder, f"{folder}.kn5")
            )
        ]

        if len(folders_with_matching_kn5) == 0:
            dpg.configure_item("local_cars", label="", items=[])
            return

        dpg.configure_item(
            "local_cars",
            items=folders_with_matching_kn5,
            default_value=folders_with_matching_kn5[0],
            callback=lambda s, d, u: self.combo_callback_localCars(s, d, u),
        )
        self.combo_callback_localCars("local_cars", None, None)

    def combo_callback_localCars(self, sender, data, user_data):
        value = dpg.get_value(sender)
        items = dpg.get_item_configuration(sender)["items"]
        index = items.index(value)

        skinpath = os.path.join(self.selectedLocalCarPath, value, "skins")
        skins = [
            folder
            for folder in os.listdir(skinpath)
            if os.path.isdir(os.path.join(skinpath, folder))
        ]

        if len(skins) == 0:
            dpg.configure_item("local_skins", label="", items=[])
            return

        dpg.configure_item("local_skins", label="", items=skins, default_value=skins[0])

    def load_ini(self, filepath):
        try:
            self.loadedCars = []
            self.config.clear()
            self.config.read(filepath)
            self.gui_update_carComboBox()
            self.gui_update_current_car(None)
        except:
            return

        self.selectedEntryIniPath = filepath
        for section in self.config.sections():
            #print(self.config.get(section, "_ACTOOL_GUID"))
            self.loadedCars.append(
                {
                    "_ACTOOL_GUID": self.config.get(section, "_ACTOOL_GUID") if self.config.has_option(section, '_ACTOOL_GUID') else str(uuid.uuid4())[:8],
                    "MODEL": self.config[section]["MODEL"],
                    "SKIN": self.config[section]["SKIN"],
                    "SPECTATOR_MODE": self.config[section]["SPECTATOR_MODE"],
                    "DRIVERNAME": self.config[section]["DRIVERNAME"],
                    "TEAM": self.config[section]["TEAM"],
                    "GUID": self.config[section]["GUID"],
                    "BALLAST": self.config[section]["BALLAST"],
                    "RESTRICTOR": self.config[section]["RESTRICTOR"],
                }
            )

    def save_ini(self, cars):
        self.config.clear()
        for i, car in enumerate(cars):
            self.config.add_section(f"CAR_{str(i)}")
            self.config[f"CAR_{i}"]["_ACTOOL_GUID"] = str(car["_ACTOOL_GUID"])
            self.config[f"CAR_{i}"]["MODEL"] = str(car["MODEL"])
            self.config[f"CAR_{i}"]["SKIN"] = str(car["SKIN"])
            self.config[f"CAR_{i}"]["SPECTATOR_MODE"] = str(car["SPECTATOR_MODE"])
            self.config[f"CAR_{i}"]["DRIVERNAME"] = str(car["DRIVERNAME"])
            self.config[f"CAR_{i}"]["TEAM"] = str(car["TEAM"])
            self.config[f"CAR_{i}"]["GUID"] = str(car["GUID"])
            self.config[f"CAR_{i}"]["BALLAST"] = str(car["BALLAST"])
            self.config[f"CAR_{i}"]["RESTRICTOR"] = str(car["RESTRICTOR"])

        # save config
        with open(self.selectedEntryIniPath, "w") as configfile:
            self.config.write(configfile, space_around_delimiters=False)

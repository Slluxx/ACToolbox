import dearpygui.dearpygui as dpg
import configparser
import random, os

class EntryList:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.iniFilePath = None
        self.loadedCars = []
        self.localCarPath = None
        self.gui()

    def gui(self):
        dpg.add_text("Load an INI file before doing anything else, even if its empty.", wrap=0)
        dpg.add_text("You can not edit multiple cars at the same time. Save before you select another.", wrap=0)
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Load INI", width=100, callback=lambda: dpg.show_item("file_dialog_id"))
            dpg.add_combo(tag="item_names", items=(), label="", width=392, callback=lambda s,d,u: self.combo_callback(s,d,u))

        with dpg.group():
            #dpg.add_input_int(tag="curr_car_nr", label="Number", enabled=False)
            dpg.add_input_text(tag="curr_car_model", label="Model", width=500)
            dpg.add_input_text(tag="curr_car_skin", label="Skin", width=500)
            dpg.add_input_int(tag="curr_car_specMode", label="Spectator Mode", width=500)
            dpg.add_input_text(tag="curr_car_driverName", label="Driver Name", width=500)
            dpg.add_input_text(tag="curr_car_team", label="Team", width=500)
            dpg.add_input_text(tag="curr_car_guid", label="GUID", width=500)
            dpg.add_input_int(tag="curr_car_ballast", label="Ballast", width=500)
            dpg.add_input_int(tag="curr_car_restrictor", label="Restrictor", width=500)
            dpg.add_button(label="Remove selected", callback=lambda s,d,u: self.btn_callback_remove(s,d,u), width=500)

            dpg.add_separator()
            dpg.add_spacer(height=10)

            dpg.add_button(label="Load local cars", callback=lambda: dpg.show_item("folder_dialog_id"), width=500)
            dpg.add_combo(tag="local_cars", items=(), label="", width=500)
            dpg.add_combo(tag="local_skins", items=(), label="", width=500)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add selected", callback=lambda s,d,u: self.btn_callback_addFromFolder(s,d,u), width=246)
                dpg.add_button(label="Add blank", callback=lambda s,d,u: self.btn_callback_addNew(s,d,u), width=246)
            
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            dpg.add_button(label="Save changes", callback=lambda s,d,u: self.btn_callback_save(s,d,u), width=500)

        with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s,d,u: self.fileDialog_OkCallback(s,d,u), id="file_dialog_id", width=500 ,height=400, modal=True):
            dpg.add_file_extension(".ini")

        defaultPath = ""
        # if path exists "D:\Program Files (x86)\Steam\steamapps\common\assettocorsa\content\cars"
        if os.path.exists("D:\\Program Files (x86)\\Steam\\steamapps\\common\\assettocorsa\\content\\cars"):
            defaultPath = "D:\\Program Files (x86)\\Steam\\steamapps\\common\\assettocorsa\\content\\cars"
        elif os.path.exists("C:\\Program Files (x86)\\Steam\\steamapps\\common\\assettocorsa\\content\\cars"):
            defaultPath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\assettocorsa\\content\\cars"

        with dpg.file_dialog(label="Select a car folder", directory_selector=True, show=False, callback=lambda s,d,u: self.folderDialog_OkCallback(s,d,u), id="folder_dialog_id", width=500 ,height=400, modal=True, default_path=defaultPath):
            pass

        with dpg.window(label="Error", modal=True, show=False, tag="error_modal", no_title_bar=True, width=250, height=100):
            dpg.add_text(tag="error_text", label="", wrap=0)
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="OK", width=-1, callback=lambda: dpg.configure_item("error_modal", show=False))

    def gui_refreshCombo(self):
        value = dpg.get_value("item_names")
        items = dpg.get_item_configuration("item_names")["items"]
        try:
            index = items.index(value)
        except:
            return

        defValue = self.loadedCars[index]['MODEL'] + "@" + self.loadedCars[index]['SKIN']
        dpg.configure_item("item_names", label="", items=[car['MODEL']+"@"+car['SKIN'] for car in self.loadedCars], default_value=defValue)
        self.set_selected_model(self.loadedCars[index])

    def combo_callback(self, sender, data, user_data):
        value = dpg.get_value(sender)
        items = dpg.get_item_configuration(sender)["items"]
        index = items.index(value)
        self.set_selected_model(self.loadedCars[index])

    def set_selected_model(self, car):
        if car == None:
            car = {}
        dpg.set_value("curr_car_model",     car.get('MODEL', ''))
        dpg.set_value("curr_car_skin",      car.get('SKIN', ''))
        dpg.set_value("curr_car_specMode",  int(car.get('SPECTATOR_MODE', 0)))
        dpg.set_value("curr_car_driverName",car.get('DRIVERNAME', ''))
        dpg.set_value("curr_car_team",      car.get('TEAM', ''))
        dpg.set_value("curr_car_guid",      car.get('GUID', ''))
        dpg.set_value("curr_car_ballast",   int(car.get('BALLAST', 0)))
        dpg.set_value("curr_car_restrictor",int(car.get('RESTRICTOR', 0)))


    def fileDialog_OkCallback(self, sender, app_data, user_data):
        print('OK was clicked.')
        self.load_ini(app_data["file_path_name"])

        if len(self.loadedCars)>0:
            defValue = self.loadedCars[0]['MODEL'] + "@" + self.loadedCars[0]['SKIN']
            dpg.configure_item("item_names", label="", items=[car['MODEL']+"@"+car['SKIN'] for car in self.loadedCars], default_value=defValue)
            self.set_selected_model(self.loadedCars[0])
        else:
            dpg.configure_item("item_names", label="", items=[])
            self.set_selected_model(None)

    def folderDialog_OkCallback(self, sender, app_data, user_data):
        print('select car folder ok was clicked.')
        self.localCarPath = app_data["file_path_name"]
        
        # load subfolders into "local_cars" - not recursive and only if it has a kn5 file with the folder name inside
        directory_path = app_data["file_path_name"]
        folders_with_matching_kn5 = [folder for folder in os.listdir(directory_path) if os.path.exists(os.path.join(directory_path, folder, f"{folder}.kn5"))]

        if len(folders_with_matching_kn5)>0:
            dpg.configure_item("local_cars", label="", items=folders_with_matching_kn5, default_value=folders_with_matching_kn5[0], callback=lambda s,d,u: self.combo_callback_localCars(s,d,u))
            self.combo_callback_localCars("local_cars", None, None)
        else:
            dpg.configure_item("local_cars", label="", items=[])

    def combo_callback_localCars(self, sender, data, user_data):
        value = dpg.get_value(sender)
        items = dpg.get_item_configuration(sender)["items"]
        index = items.index(value)

        skinpath = os.path.join(self.localCarPath, value, "skins")

        # scan self.localCarPath / skins for subfolders
        skins = [folder for folder in os.listdir(skinpath) if os.path.isdir(os.path.join(skinpath, folder))]
        
        if len(skins)>0:
            dpg.configure_item("local_skins", label="", items=skins, default_value=skins[0])
        else:
            dpg.configure_item("local_skins", label="", items=[])

    def load_ini(self, filepath):
        try:
            self.config.clear()
            self.config.read(filepath)
        except:
            return
        self.iniFilePath = filepath
        self.loadedCars = self.ini_to_dict()

    def ini_to_dict(self):
        config = self.config
        cars = []
        for section in config.sections():
            cars.append({
                'MODEL': config[section]['MODEL'],
                'SKIN': config[section]['SKIN'],
                'SPECTATOR_MODE': config[section]['SPECTATOR_MODE'],
                'DRIVERNAME': config[section]['DRIVERNAME'],
                'TEAM': config[section]['TEAM'],
                'GUID': config[section]['GUID'],
                'BALLAST': config[section]['BALLAST'],
                'RESTRICTOR': config[section]['RESTRICTOR'],
            })
        return cars
    
    def dict_to_ini(self, cars):
        #clear config
        self.config.clear()
        for i, car in enumerate(cars):
            self.config.add_section(f"CAR_{str(i+1)}")
            self.config[f"CAR_{i+1}"]['MODEL'] = str(car['MODEL'])
            self.config[f"CAR_{i+1}"]['SKIN'] = str(car['SKIN'])
            self.config[f"CAR_{i+1}"]['SPECTATOR_MODE'] = str(car['SPECTATOR_MODE'])
            self.config[f"CAR_{i+1}"]['DRIVERNAME'] = str(car['DRIVERNAME'])
            self.config[f"CAR_{i+1}"]['TEAM'] = str(car['TEAM'])
            self.config[f"CAR_{i+1}"]['GUID'] = str(car['GUID'])
            self.config[f"CAR_{i+1}"]['BALLAST'] = str(car['BALLAST'])
            self.config[f"CAR_{i+1}"]['RESTRICTOR'] = str(car['RESTRICTOR'])

        # save config
        with open(self.iniFilePath, "w") as configfile:
            self.config.write(configfile)

        
    def btn_callback_addNew(self, sender, data, user_data):

        newCar = {
            'MODEL': 'MyNewCarModel'+"{:04d}".format(random.randint(0, 9999)),
            'SKIN': 'MyNewCarSkin/ACA3',
            'SPECTATOR_MODE': 0,
            'DRIVERNAME': '',
            'TEAM': '',
            'GUID': '',
            'BALLAST': 0,
            'RESTRICTOR': 0
        }
        self.loadedCars.append(newCar)
        index = self.loadedCars.index(newCar)
        defValue = self.loadedCars[index]['MODEL'] + "@" + self.loadedCars[index]['SKIN']
        dpg.configure_item("item_names", label="", items=[car['MODEL']+"@"+car['SKIN'] for car in self.loadedCars], default_value=defValue)
        self.set_selected_model(self.loadedCars[index])

    def btn_callback_save(self, sender, data, user_data):
        value = dpg.get_value("item_names")
        items = dpg.get_item_configuration("item_names")["items"]
        try:
            index = items.index(value)
        except:
            self.dict_to_ini(self.loadedCars)
            self.gui_refreshCombo()
            return
        
        self.loadedCars[index]['MODEL'] = dpg.get_value("curr_car_model")
        self.loadedCars[index]['SKIN'] = dpg.get_value("curr_car_skin")
        self.loadedCars[index]['SPECTATOR_MODE'] = dpg.get_value("curr_car_specMode")
        self.loadedCars[index]['DRIVERNAME'] = dpg.get_value("curr_car_driverName")
        self.loadedCars[index]['TEAM'] = dpg.get_value("curr_car_team")
        self.loadedCars[index]['GUID'] = dpg.get_value("curr_car_guid")
        self.loadedCars[index]['BALLAST'] = dpg.get_value("curr_car_ballast")
        self.loadedCars[index]['RESTRICTOR'] = dpg.get_value("curr_car_restrictor")

        self.dict_to_ini(self.loadedCars)
        self.gui_refreshCombo()

    def btn_callback_remove(self, sender, data, user_data):
        value = dpg.get_value("item_names")
        items = dpg.get_item_configuration("item_names")["items"]
        try:
            index = items.index(value)
        except:
            return

        if self.loadedCars[index]:
            self.loadedCars.pop(index)
    
        if len(self.loadedCars) == 0:
            dpg.configure_item("item_names", label="", items=[], default_value="")
            self.set_selected_model(None)
        else:
            defValue = self.loadedCars[index]['MODEL'] + "@" + self.loadedCars[index]['SKIN']
            dpg.configure_item("item_names", label="", items=[car['MODEL']+"@"+car['SKIN'] for car in self.loadedCars], default_value=defValue)
            self.set_selected_model(self.loadedCars[0])

    def btn_callback_addFromFolder(self, sender, data, user_data):
        localCar = dpg.get_value("local_cars")
        localCarSkin = dpg.get_value("local_skins")

        if localCar == "" or localCarSkin == "":
            return
        
        

        for car in self.loadedCars:
            if car['MODEL'] == localCar and car['SKIN'] == localCarSkin + "/ACA3":
                dpg.set_value("error_text", "A car with this model and skin already exists.")
                dpg.configure_item("error_text", label="A car with this model and skin already exists.", wrap=0)
                dpg.configure_item("error_modal", show=True)
                MainWindow_width = dpg.get_item_width("Primary Window")
                MainWindow_height = dpg.get_item_height("Primary Window")
                ModalWindow_width = dpg.get_item_width("error_modal")
                ModalWindow_height = dpg.get_item_height("error_modal")
                dpg.set_item_pos("error_modal", [int((MainWindow_width/2 - ModalWindow_width/2)), int((MainWindow_height/2 - ModalWindow_height/2))])
                return

        newCar = {
            'MODEL': localCar,
            'SKIN': localCarSkin + "/ACA3",
            'SPECTATOR_MODE': 0,
            'DRIVERNAME': '',
            'TEAM': '',
            'GUID': '',
            'BALLAST': 0,
            'RESTRICTOR': 0
        }
        self.loadedCars.append(newCar)
        index = self.loadedCars.index(newCar)

        defValue = self.loadedCars[index]['MODEL'] + "@" + self.loadedCars[index]['SKIN']
        dpg.configure_item("item_names", label="", items=[car['MODEL']+"@"+car['SKIN'] for car in self.loadedCars], default_value=defValue)
        self.set_selected_model(self.loadedCars[index])

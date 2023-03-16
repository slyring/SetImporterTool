import unreal

import tkinter as tk
from tkinter import filedialog, simpledialog

import sys
from PyQt6.QtWidgets import QApplication,  QFileDialog, QInputDialog, QStyle

from os import walk
import time


class AssetInfo:
    def __init__(self):
        self.mesh = None
        self.t_bc = None
        self.t_n = None
        self.t_rma = None
        self.name = ""


def show_select_folder():
    qtApp = QApplication(sys.argv)
    dir_name = QFileDialog.getExistingDirectory(
        None, "Select a Directory")
    if dir_name != '':
        print(dir_name)
        qtApp.exit()
        return dir_name
    else:
        print("No directory selected")
        qtApp.exit()
        exit()


def show_import_folder_path():
    qtApp = QApplication(sys.argv)

    in_dlg = QInputDialog()
    in_dlg.resize(300, 100)
    in_dlg.setMinimumSize(300, 100)
    in_dlg.setMaximumSize(300, 100)
    in_dlg.setWindowTitle('Destination path/folder name')
    in_dlg.setLabelText("Enter path/folder name:")

    pixmapi = QStyle.StandardPixmap.SP_MessageBoxQuestion
    icon = qtApp.style().standardIcon(pixmapi)
    in_dlg.setWindowIcon(icon)
    ok = in_dlg.exec()
    text = in_dlg.textValue()

    if ok and text != '':
        print(text)
        qtApp.exit()
        return text
    else:
        print("No path/folder set")
        qtApp.exit()
        exit()


# Select folder with prompt
filePath = show_select_folder()


# Exit on cancel
if filePath == '':
    exit(0)

# Set destination folder/path name
asset_folder_name = show_import_folder_path()

# unreal.log(asset_folder_name)

# Exit if empty or cancel
if asset_folder_name == '' or asset_folder_name is None:
    exit(0)


# Setting Import Properties
def set_import_properties(filename, destination_path):
    task = unreal.AssetImportTask()
    fbx_import_options = unreal.FbxImportUI()
    fbx_import_options.import_materials = False
    task.set_editor_property("options", fbx_import_options)
    task.set_editor_property("automated", True)
    task.set_editor_property("filename", filename)
    task.set_editor_property("destination_path", destination_path)
    return task


def update_frame_progress(l_import_task, label):
    l_import_task.enter_progress_frame(1, label)
    time.sleep(0.5)


# Progress updater for the entire task
task_updater_state = 4

with unreal.ScopedSlowTask(task_updater_state) as importer_task:
    importer_task.make_dialog(True)
    # ----------------------------------------------------
    # IMPORTING PART
    # Read the folder and add contents' names to list
    # ----------------------------------------------------
    importer_task.enter_progress_frame(1, 'Importing Assets')
    getFolderContents = []
    for (dir_path, dir_names, filenames) in walk(filePath):
        # contents' names added by extending the empty list
        getFolderContents.extend(filenames)
        break

    # Import path as in UE content directory
    path = '/Game/Assets/' + asset_folder_name

    # List to store all import task
    tasks = []

    # x is an item in getFolderContents list
    for x in getFolderContents:
        # checking if the path with filename is working for all items
        unreal.log("Assets Imported: " + filePath + "/" + x)
        # adding items to tasks list with proper path and name
        tasks.append(set_import_properties(filePath + "/" + x, path))

    # import all the assets that are in the list
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    unreal.log("------------------IMPORT FINISH--------------------------")

    unreal.log("------------------SETTING UP-----------------------------")
    # ----------------------------------------------------
    # SETTING ASSET PROPERTIES FOR IMPORTED ASSETS
    # ----------------------------------------------------

    # List of valid textures to set as masked on postfix
    validMaskedTextureSuffix = ["_RMA", "_R", "_M", "_MK", "_AO"]

    def create_material_instance(in_asset_info):
        update_frame_progress(importer_task, 'Setting up material instance')

        asset_helper = unreal.AssetToolsHelpers.get_asset_tools()
        new_factory = unreal.MaterialInstanceConstantFactoryNew()
        created_instance = asset_helper.create_asset("MI_" + in_asset_info.name, path, unreal.MaterialInstanceConstant,
                                                     new_factory)

        # Set reference of master material here. MI will be created out of this MM
        parent_material = unreal.EditorAssetLibrary.load_asset(
            "Material'/Game/Materials/MM_TestMaterial.MM_TestMaterial'")
        unreal.MaterialEditingLibrary.set_material_instance_parent(
            created_instance, parent_material)

        # Set Color to material instance
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(created_instance, "Color",
                                                                                    in_asset_info.t_bc)

        # Set Normal to material instance
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(created_instance, "Normal",
                                                                                    in_asset_info.t_n)

        # Set RMA to material instance
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(created_instance, "RMA",
                                                                                    in_asset_info.t_rma)

        in_asset_info.mesh.set_material(0, created_instance)

    def create_asset_set(in_assets):
        update_frame_progress(importer_task, 'Setting up asset set')

        # store current asset set as object for further access
        current_asset_info = AssetInfo()

        # loop all assets in folder
        for eachAsset in in_assets:

            # load all assets in folder
            loaded_asset = unreal.EditorAssetLibrary.load_asset(eachAsset)
            current_asset_info.name = str(
                loaded_asset.get_name()).split("_")[1]

            if type(loaded_asset) == unreal.StaticMesh:
                unreal.log("Static Mesh found:" + loaded_asset.get_name())
                current_asset_info.mesh = loaded_asset
                update_frame_progress(importer_task, 'Setting up mesh')

            else:
                update_frame_progress(importer_task, 'Setting up textures')
                # loop all checks for linear textures
                for linType in validMaskedTextureSuffix:

                    # condition: if there is a linear texture
                    if unreal.StringLibrary.ends_with(loaded_asset.get_name(), linType):
                        # tell which are linear
                        unreal.log("Linear Texture Assets Found: " +
                                   loaded_asset.get_name())
                        # change compression settings to masks
                        loaded_asset.set_editor_property("CompressionSettings",
                                                         unreal.TextureCompressionSettings.TC_MASKS)
                        # tell which assets are changed
                        unreal.log(
                            "Has set mask compression settings for {}".format(eachAsset))
                        break

                # Set asset info as per tex type
                if unreal.StringLibrary.ends_with(loaded_asset.get_name(), "_RMA"):
                    current_asset_info.t_rma = loaded_asset
                elif unreal.StringLibrary.ends_with(loaded_asset.get_name(), "_N"):
                    current_asset_info.t_n = loaded_asset
                elif unreal.StringLibrary.ends_with(loaded_asset.get_name(), "_BC"):
                    current_asset_info.t_bc = loaded_asset

        create_material_instance(current_asset_info)

    access_imported_assets = unreal.EditorAssetLibrary.list_assets(
        path, True, False)
    create_asset_set(access_imported_assets)

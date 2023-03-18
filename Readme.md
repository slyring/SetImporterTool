# SetImporterTool

Pipeline specific auto Static Mesh Set importer script in python to save time and enhance workflow.

## How it works

Place all assets in a folder with following naming convention

- SM\_[Name fo asset].fbx -> Static Mesh
- T\_[Name fo asset]\_BC.png -> Base color texture
- T\_[Name fo asset]\_N.png -> Normal Texture
- T\_[Name fo asset]\_RMA.png -> RMA Packed Texture or equivalent based on your Mater material in UE5
- Run importer.py from UE Python
- Select folder containing these assets.

  ![Select folder dialog](/.res/img_select_folder_dialog.png)

- Set folder path/name to import asset to under /Game/Assets/.

  ![Path/name dialog](/.res/img_set_folder_import_path.png)

- Post import.

  ![Post import content browser](/.res/img_post_import.png)

## Setup required in UE

Master material setup in this scenario.

![Master material in UE](/.res/img_master_material.png)

## Further modifications to fit other pipeline

The parameter name need to match the naming in python code. Any mask pack can be used instead of just RMA as long as the names are matching.

https://github.com/slyring/SetImporterTool/blob/abfd644ae3a954b369f2307561a2ea067ab708f2/Importer.py#L152-L161

Add the suffix to this array. Doing this will set such texture asset as mask automatically

https://github.com/slyring/SetImporterTool/blob/abfd644ae3a954b369f2307561a2ea067ab708f2/Importer.py#L135-L136

Match the suffix with the respective texture file name's suffix

https://github.com/slyring/SetImporterTool/blob/abfd644ae3a954b369f2307561a2ea067ab708f2/Importer.py#L203-L209

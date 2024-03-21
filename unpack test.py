import electrovoyage_asset_unpacker as pack
from PIL import Image

PATH = "C:/Users/Артём/Desktop/python programs/executable data packer/assets.packed"

bundle = pack.AssetPack(PATH)
f = bundle.getfile('resources/tiles/jungle.png')

Image.open(f).convert('RGBA').show()
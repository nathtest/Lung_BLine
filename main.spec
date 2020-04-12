# -*- mode: python ; coding: utf-8 -*-
import os
import scipy

scipy_libs = os.path.join(os.path.dirname(scipy.__file__), '.libs')


block_cipher = None

added_files = [
         ( '.\Resource\\about-icon.png', 'Resource' ),
         ( '.\Resource\\add-icon.png', 'Resource' ),
         ( '.\Resource\\close-icon.png', 'Resource' ),
         ( '.\Resource\\delete-icon.png', 'Resource' ),
         ( '.\Resource\\Grey_close_x.png', 'Resource' ),
         ( '.\Resource\\lung_icon.png', 'Resource' ),
         ( '.\Resource\\no-image-icon.png', 'Resource' ),
         ( '.\\Resource\\open-icon.png','Resource')
         ]

a = Analysis(['main.py'],
             pathex=['C:\\Users\\nath\\PycharmProjects\\Lung_BLine',scipy_libs],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Lung BLine',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='C:\\Users\\nath\\PycharmProjects\\Lung_BLine\\Resource\\lung_ico.ico')
; Script de Inno Setup para instalar BYSROT

[Setup]
AppName=BYSROT
AppVersion=2.0
DefaultDirName={pf}\BYSROT
DefaultGroupName=BYSROT
OutputDir=dist
OutputBaseFilename=BysRot_2.0.0_setup
SetupIconFile=logo_icon.ico
UninstallDisplayIcon={app}\BYSROT.exe
Compression=lzma
SolidCompression=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\BYSROT.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\BYSROT"; Filename: "{app}\BYSROT.exe"
Name: "{commondesktop}\BYSROT"; Filename: "{app}\BYSROT.exe"; Tasks: desktopicon

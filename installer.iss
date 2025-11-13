
#define MyAppName "BysRot"
#define MyAppVersion "2.0.3"
#define MyAppPublisher "Byspro"
#define MyAppExeName "BysRot.exe"
#define MyAppIcon "icon.ico"

[Setup]
AppId={{A1B2C3D4-E5F6-1234-5678-9ABCDEF01234}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppIcon}
SetupIconFile={#MyAppIcon}
Compression=lzma
SolidCompression=yes
OutputDir=dist\installer
OutputBaseFilename=BysRot_Installer
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
Source: "dist\BysRot\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

#ifndef Arch
  #define Arch "x64"
#endif

#define AppName "Pinterest Downloader GUI"
#define AppExeName "pinterest-dl.exe"
#define AppPublisher "Zeke Zhang"
#define AppURL "https://github.com/sean1832/pinterest-dl-gui"

[Setup]
; AppId uniquely identifies the app for upgrades and uninstall. Keep it stable.
AppId={{B7E4D2A1-9C3F-4E8A-A6D5-1F2E3C4B5A60}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
DefaultDirName={autopf}\Pinterest Downloader GUI
DefaultGroupName=Pinterest Downloader GUI
DisableProgramGroupPage=yes
LicenseFile=EULA.txt
OutputDir=dist
OutputBaseFilename=pinterest-dl-gui_{#AppVersion}_{#Arch}_setup
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\app.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

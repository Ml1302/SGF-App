[Setup]
AppId={{B8E20B53-F50B-4438-9BD3-396BEAE526AF}}
AppName=SGF-App
AppVersion=1.0.1
AppVerName=Sistema de Gestión Financiera 1.0.1
AppPublisher=Your Company
AppPublisherURL=https://www.yourcompany.com
AppSupportURL=https://www.yourcompany.com/support
AppUpdatesURL=https://www.yourcompany.com/updates
DefaultDirName={pf}\SGF-App
DefaultGroupName=SGF-App
OutputDir=output
OutputBaseFilename=SGF-App-Setup
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\SGF-App.exe
PrivilegesRequired=admin
WizardStyle=modern

[Files]
Source: "dist\SGF-App.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "data\db.sqlite3"; DestDir: "{app}\data"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs createallsubdirs
Source: "calculos.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "graficos.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "apis.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "exportacion.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SGF-App"; Filename: "{app}\SGF-App.exe"
Name: "{commondesktop}\SGF-App"; Filename: "{app}\SGF-App.exe"

[Dirs]
Name: "{app}\data"

[Run]
Filename: "{app}\SGF-App.exe"; Parameters: "--init-db"; Flags: nowait postinstall skipifsilent
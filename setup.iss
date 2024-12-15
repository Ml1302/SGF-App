[Setup]
AppId={{B8E20B53-F50B-4438-9BD3-396BEAE526AF}}
AppName=Sistema de Gestión Financiera
AppVersion=1.0.1
AppVerName=Sistema de Gestión Financiera 1.0.1
AppPublisher=Your Company
AppPublisherURL=https://www.yourcompany.com
AppSupportURL=https://www.yourcompany.com/support
AppUpdatesURL=https://www.yourcompany.com/updates
DefaultDirName={commonpf64}\SGF-App
DefaultGroupName=Sistema de Gestión Financiera
OutputDir=output
OutputBaseFilename=SGF-App-Setup-1.0.1
Compression=lzma2/ultra64
SolidCompression=yes
UninstallDisplayIcon={app}\SGF-App.exe
PrivilegesRequired=admin
WizardStyle=modern

[Files]
Source: "dist\SGF-App.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "db.sqlite3"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\SGF-App"; Filename: "{app}\SGF-App.exe"
Name: "{commondesktop}\SGF-App"; Filename: "{app}\SGF-App.exe"
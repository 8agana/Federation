"use strict";

const path = require("path");
const proc  = require("process");
const { app, Menu, BrowserWindow, ipcMain, shell, screen } = require("electron");
const { autoUpdater } = require("electron-updater");
const jetpack   = require("fs-jetpack");
const isOnline  = require("is-online");

const menuTemplate = (appName) => ([
  {
    label: appName,
    submenu: [
      { role: "about" },
      { type: "separator" },
      { role: "services", submenu: [] },
      { type: "separator" },
      { role: "hide" },
      { role: "hideothers" },
      { role: "unhide" },
      { type: "separator" },
      { role: "quit" }
    ]
  },
  {
    label: "Edit",
    submenu: [
      { role: "undo" }, { role: "redo" }, { type: "separator" },
      { role: "cut" },  { role: "copy" }, { role: "paste" },
      { role: "pasteandmatchstyle" }, { role: "delete" }, { role: "selectall" }
    ]
  },
  {
    label: "Window",
    submenu: [
      { label: "Close",     accelerator: "CmdOrCtrl+W", role: "close" },
      { label: "Minimize",  accelerator: "CmdOrCtrl+M", role: "minimize" },
      { label: "Bring All to Front", role: "front" }
    ]
  },
  {
    label: "Help",
    submenu: [
      { label: "Knowledge Base", click: () => shell.openExternal("https://kb.shootproof.com/help/desktop-uploader") }
    ]
  }
]);

// This helper function creates the window
function createWindowState(name, defaults) {
  const store = jetpack.cwd(app.getPath("userData"));
  const stateFile = `window-state-${name}.json`;
  const def = { width: defaults.width, height: defaults.height };
  let state = {};
  let win;

  // --- Helper functions inside createWindowState (unchanged) ---
  const getStored = () => {
    try { return store.read(stateFile, "json"); }
    catch { return {}; }
  };
  const getCurrent = () => {
    const [x, y] = win.getPosition();
    const [w, h] = win.getSize();
    return { x, y, width: w, height: h };
  };
  const within = (b, m) =>
    b.x >= m.x && b.y >= m.y && b.x + b.width <= m.x + m.width && b.y + b.height <= m.y + m.height;
  const center = () => {
    const { bounds } = screen.getPrimaryDisplay();
    return { x: (bounds.width - def.width) / 2, y: (bounds.height - def.height) / 2, ...def };
  };
  const ensureVisible = (b) =>
    screen.getAllDisplays().some(d => within(b, d.bounds)) ? b : center();
  const saveState = () => {
    if (!win || win.isDestroyed() || win.isMinimized() || win.isMaximized()) return; // Added checks for safety
      Object.assign(state, getCurrent());
      store.write(stateFile, state, { atomic: true });
  };
  // --- End Helper functions ---

  state = ensureVisible({ ...def, ...getStored() });

  // Create the BrowserWindow instance
  win   = new BrowserWindow({
    ...defaults, // Spread existing defaults first
    ...state,    // Spread saved state
    webPreferences: {
      // --- MODIFIED webPreferences ---
      ...defaults.webPreferences, // Keep original prefs like webviewTag if they exist

      nodeIntegration: true,  // <-- ALLOWS require() in renderer
      contextIsolation: false, // <-- NEEDED for nodeIntegration=true usually

      // Keep preload for now, might be needed for other things or @electron/remote
      preload: require('path').join(__dirname, "preload.js")
      // --- END MODIFIED webPreferences ---
    }
  });

  win.on("close", saveState);
  return win;
} // End of createWindowState function

/* ---------- env & setup ---------- */
const env = jetpack.cwd(__dirname).read("env.json", "json");
require("@electron/remote/main").initialize();

let mainWin = null; // Initialize mainWin to null
let feedURL = null;

app.on("ready", () => {
  if (proc.platform === "darwin")
    Menu.setApplicationMenu(Menu.buildFromTemplate(menuTemplate(app.getName())));

  // --- Feed URL logic (unchanged) ---
  if (env.name === "development")
    feedURL = `https://s3.amazonaws.com/${env.UPDATE_S3_BUCKET}/desktop-uploader/${platformKey()}`;
  else if (env.name === "beta")
    feedURL = `https://s3.amazonaws.com/${env.UPDATE_S3_BUCKET}/${platformKey()}`;
  // --- End Feed URL logic ---

  if (env.name !== "production")
    app.setPath("userData", `${app.getPath("userData")} (${env.name})`);

  let title = app.getName();
  if (env.name !== "production") title += ` v${app.getVersion()}`;

  // Call createWindowState to create the main window
  mainWin = createWindowState("main", { // Pass defaults object
    width: 1000,
    height: 600,
    minWidth: 478,
    minHeight: 416,
    title,
    webPreferences: { // Pass original webPreferences here
      // nodeIntegration and webviewTag were likely here originally
      // createWindowState will merge these with the modified security settings
      nodeIntegration: true, // Ensure it's passed if needed by original defaults
      webviewTag: true
    }
  });

  mainWin.on("page-title-updated", e => e.preventDefault());
  require("@electron/remote/main").enable(mainWin.webContents);

  mainWin.loadURL(`file://${__dirname}/app.html`);
  mainWin.webContents.openDevTools(); // FORCE OPEN DEVTOOLS

  // Redundant check, but harmless
  if (env.name !== "production") mainWin.webContents.openDevTools();

  /* -------- auto‑update handlers (unchanged) -------- */
  autoUpdater.on("checking-for-update", () =>
    mainWin.webContents.send("update-status", { status: "CHECKING" })
  );
  autoUpdater.on("update-not-available", info =>
    mainWin.webContents.send("update-status", { status: "NO_UPDATE", info: env.name === "development" ? info : null })
  );
  autoUpdater.on("update-available", info =>
    mainWin.webContents.send("update-status", { status: "UPDATE_AVAILABLE", info: env.name === "development" ? info : null })
  );
  autoUpdater.on("update-downloaded", () =>
    mainWin.webContents.send("update-status", { status: "UPDATE_DOWNLOADED" })
  );
  /* -------- End auto-update handlers -------- */
});

app.on("window-all-closed", () => {
  // Standard macOS behavior
  if (proc.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // Standard macOS behavior
  if (BrowserWindow.getAllWindows().length === 0) {
    // Re-create window if dock icon is clicked and no windows exist
    if (app.isReady()) { // Ensure app is ready before trying to create window
       // Re-call the ready handler logic or a dedicated createWindow function if you refactor
       // For now, we assume 'ready' event logic handles creation if mainWin is null
    }
  }
});


// --- IPC Handlers (unchanged) ---
ipcMain.on("check-update", () => checkUpdate(feedURL));
ipcMain.on("install-update", () => autoUpdater.quitAndInstall());
ipcMain.on("inspectTree", (ev, p) => {
  if (mainWin) { // Check if mainWin exists
     ev.sender.send("inspectTree-tree", jetpack.inspectTree(p))
  }
});
// --- End IPC Handlers ---


// --- checkUpdate function (unchanged, added safety check for mainWin) ---
function checkUpdate(url) {
  isOnline().then(yes => {
    if (!yes || !mainWin) return; // Check if online and window exists
    if (url) {
      autoUpdater.setFeedURL(url);
      autoUpdater.channel = "canary";
    }
    autoUpdater.checkForUpdates().catch(err => {
       if (mainWin) { // Check if mainWin still exists before sending
         mainWin.webContents.send("update-status", { status: "UPDATE_ERROR", error: env.name === "development" ? err : null })
       }
    });
  });
}
// --- End checkUpdate function ---


// --- platformKey function (unchanged) ---
function platformKey() {
  return { darwin: "mac", win32: "win" }[proc.platform];
}
// --- End platformKey function ---
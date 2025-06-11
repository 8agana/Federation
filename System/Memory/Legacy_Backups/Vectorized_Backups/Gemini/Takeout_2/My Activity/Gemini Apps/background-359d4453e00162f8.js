"use strict";

const path = require("path");                 //  ←  added
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

/* ---------- window‑state helper (unchanged) ---------- */
function createWindowState(name, defaults) {
  const store = jetpack.cwd(app.getPath("userData"));
  const stateFile = `window-state-${name}.json`;
  const def = { width: defaults.width, height: defaults.height };
  let state = {};
  let win;

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
    if (!win.isMinimized() && !win.isMaximized())
      Object.assign(state, getCurrent()), store.write(stateFile, state, { atomic: true });
  };

  state = ensureVisible({ ...def, ...getStored() });
  win   = new BrowserWindow({
    ...defaults,
    ...state,
    webPreferences: {
      ...defaults.webPreferences,

      /* ---------- preload added ---------- */
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js")
    }
  });
  win.on("close", saveState);
  return win;
}

/* ---------- env & setup ---------- */
const env = jetpack.cwd(__dirname).read("env.json", "json");
require("@electron/remote/main").initialize();

let mainWin, feedURL = null;

app.on("ready", () => {
  if (proc.platform === "darwin")
    Menu.setApplicationMenu(Menu.buildFromTemplate(menuTemplate(app.getName())));

  if (env.name === "development")
    feedURL = `https://s3.amazonaws.com/${env.UPDATE_S3_BUCKET}/desktop-uploader/${platformKey()}`;
  else if (env.name === "beta")
    feedURL = `https://s3.amazonaws.com/${env.UPDATE_S3_BUCKET}/${platformKey()}`;

  if (env.name !== "production")
    app.setPath("userData", `${app.getPath("userData")} (${env.name})`);

  let title = app.getName();
  if (env.name !== "production") title += ` v${app.getVersion()}`;

  mainWin = createWindowState("main", {
    width: 1000,
    height: 600,
    minWidth: 478,
    minHeight: 416,
    title,
    webPreferences: {
      nodeIntegration: true,
      webviewTag: true
      /* contextIsolation & preload already injected by createWindowState */
    }
  });

  mainWin.on("page-title-updated", e => e.preventDefault());
  require("@electron/remote/main").enable(mainWin.webContents);

  mainWin.loadURL(`file://${__dirname}/app.html`);
  mainWin.webContents.openDevTools(); // <--- FORCE OPEN DEVTOOLS

  // This line might be redundant now, but leave it for consistency
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
});

app.on("window-all-closed", () => app.quit());

ipcMain.on("check-update", () => checkUpdate(feedURL));
ipcMain.on("install-update", () => autoUpdater.quitAndInstall());
ipcMain.on("inspectTree", (ev, p) =>
  ev.sender.send("inspectTree-tree", jetpack.inspectTree(p))
);

function checkUpdate(url) {
  isOnline().then(yes => {
    if (!yes) return;
    if (url) {
      autoUpdater.setFeedURL(url);
      autoUpdater.channel = "canary";
    }
    autoUpdater.checkForUpdates().catch(err =>
      mainWin.webContents.send("update-status", { status: "UPDATE_ERROR", error: env.name === "development" ? err : null })
    );
  });
}

function platformKey() {
  return { darwin: "mac", win32: "win" }[proc.platform];
}
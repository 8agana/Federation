+ "use strict";
const L = require("angular");
require("angular-ui-router");
require("angular-localforage");
require("angular-translate");
require("angular-ui-bootstrap");
const re = require("electron"),
  de = require("@electron/remote"),
  he = require("process"),
  ie = require("fs-jetpack"),
  T = require("path"),
  ge = require("read-chunk"),
  fe = require("file-type"),
  me = require("d3"),
  be = require("nanoid"),
  ye = require("escape-string-regexp"),
  ve = require("stream-throttle"),
  Ce = require("request"),
  U = require("lodash"),
  we = require("is-online"),
  Ie = require("junk");
require("angular-sanitize");
require("ui-select");
const le = require("ng-infinite-scroll"),
  Ue = require("file-url"),
  Ee = ["$localForage", "$rootScope", "$state", "spAuth", "spLogger", Ae];
function Ae(n, o, s, e, a) {
  o.$on("$stateChangeStart", (t, i, r) => {
    if (!i.public)
      return e
        .check()
        .then(() => (a.append(`Going to state: ${i.name}`), s.go(i, r)))
        .catch(
          () => (
            t.preventDefault(),
            a.append("User is not logged in"),
            s.go("auth.check")
          ),
        );
  });
}
const _e = ["$state", "spQueue", "spJobStatus", "spPhotoStatus", $e];
function $e(n, o, s, e) {
  const a = (t) => t.status !== s.COMPLETED || t.errors;
  o.restore([a])
    .then(
      (t) => (o.resume(), o.jobs.length ? n.go("queue") : n.go("upload.new")),
    )
    .catch(() => n.go("upload.new"));
}
const ke = ["$rootScope", "spQueue", Le];
function Le(n, o) {
  n.$on("spApi:uploadCompleted", o.uploadCompleteHandler);
}
const Pe = ["$localForage", "spConfig", "spLogger", Oe];
function Oe(n, o, s) {
  return n
    .getItem("settings", !0)
    .then((e) => o.loadSettings(e))
    .catch(o.restoreDefaultSettings)
    .finally(() => {
      s.append(`Initialized with settings: ${JSON.stringify(o.settings)}`);
    });
}
const Se = ["electron", De];
function De(n) {
  return {
    restrict: "A",
    transclude: !1,
    link: (o, s, e) => {
      s.on("click", (a) => {
        const t = e.ngHref || e.href;
        a.preventDefault(), t && n.shell.openExternal(t);
      });
    },
  };
}
const Te = ["$document", "electron", "electron.remote", Ne];
function Ne(n, o, s) {
  return {
    link: (e, a) => {
      (e.menu = new s.Menu()),
        e.menu.append(
          new s.MenuItem({
            label: "Copy",
            role: "copy",
            accelerator: "CmdOrCtrl+C",
          }),
        ),
        a.on("contextmenu", (t) => {
          const i =
            t.target.nodeName === "TEXTAREA" || t.target.nodeName === "INPUT";
          i &&
            (e.menu.append(
              new s.MenuItem({
                label: "Cut",
                role: "cut",
                accelerator: "CmdOrCtrl+X",
              }),
            ),
            e.menu.append(
              new s.MenuItem({
                label: "Paste",
                role: "paste",
                accelerator: "CmdOrCtrl+V",
              }),
            )),
            (i || n[0].getSelection().toString() !== "") &&
              e.menu.popup(s.getCurrentWindow());
        });
    },
  };
}
const ue = "spWebview",
  Fe = ["$interval", "spUtils", "spConfig", Re];
function Re(n, o, s) {
  return {
    restrict: "E",
    scope: { src: "<spWebviewSrc" },
    template: `<webview src="about:blank" useragent="ShootProof Desktop Uploader v${s.version}"></webview>`,
    link: (e, a) => {
      const t = a[0].querySelector("webview"),
        i = o.domEventScopeEmitter(e, ue);
      let r = !1;
      [
        "load-commit",
        "did-finish-load",
        "did-fail-load",
        "did-frame-finish-load",
        "did-start-loading",
        "did-stop-loading",
        "did-get-response-detail",
        "did-get-redirect-request",
        "dom-ready",
        "page-title-updated",
        "page-favicon-updated",
        "enter-html-full-screen",
        "leave-html-full-screen",
        "console-message",
        "found-in-page",
        "new-window",
        "will-navigate",
        "did-navigate",
        "did-navigate-in-page",
        "close",
        "ipc-message",
        "crashed",
        "gpu-crashed",
        "plugin-crashed",
        "destroyed",
        "media-started-playing",
        "media-paused",
        "did-change-theme-color",
        "devtools-opened",
        "devtools-closed",
        "devtools-focused",
      ].forEach((c) => angular.element(t).on(c, i)),
        e.$on(`${ue}:dom-ready`, () => {
          r = !0;
        }),
        e.$watch("src", (c) => {
          if (c) {
            let g = n(() => {
              r && (t.loadURL(c), (r = !1), n.cancel(g));
            }, 200);
          }
        });
    },
  };
}
const Ge = "spDropzone",
  je = "sp-dropzone",
  Me = ["spUtils", qe];
function qe(n) {
  return { restrict: "EA", link: o };
  function o(e, a) {
    const t = n.domEventScopeBroadcaster(e, Ge),
      i = {
        drag: null,
        dragstart: null,
        dragend: null,
        dragover: null,
        dragenter: [{ modifier: "over", state: !0 }],
        dragleave: [{ modifier: "over", state: !1 }],
        drop: [{ modifier: "drop", state: !0 }],
      };
    Object.keys(i).forEach((r) => a.on(r, t)),
      Object.keys(i).forEach((r) =>
        a.on(r, (c) => {
          c.stopPropagation(), c.preventDefault();
        }),
      ),
      Object.keys(i).forEach((r) => a.on(r, s(je, i, r, a)));
  }
  function s(e, a, t, i) {
    return () => {
      a[t] !== null &&
        a[t].forEach((r) => {
          const c = `${e}--${r.modifier}`;
          r.state ? i.addClass(c) : i.removeClass(c);
        });
    };
  }
}
const Be = "spBrowseDirectory",
  ze = ["$timeout", "spUtils", He];
function He(n, o) {
  return {
    restrict: "E",
    scope: { label: "=" },
    transclude: !0,
    template: `
<button
    class="button--primary sp-browse-directory__button">
    {{ label }}
</button>
<input
    class="sp-browse-directory__input"
    type="file">`,
    link: s,
  };
  function s(e, a, t) {
    const i = o.domEventScopeEmitter(e, Be),
      r = a.find("input"),
      c = { change: null, click: null };
    L.isUndefined(t.directory)
      ? r.attr("multiple", !0)
      : r.attr("webkitdirectory", !0),
      Object.keys(c).forEach((g) => r.on(g, i));
  }
}
const xe = [
    function () {
      return {
        restrict: "A",
        link: (o, s) => {
          s[0].focus();
        },
      };
    },
  ],
  We = {
    transclude: !0,
    templateUrl: "spCommon/components/accordion/sp-accordion.nghtml",
    controller: Je,
  };
function Je() {
  (this.$onInit = n.bind(this)),
    (this.closeOthers = o.bind(this)),
    (this.addGroup = s.bind(this)),
    (this.removeGroup = e.bind(this)),
    (this.openFirst = a.bind(this));
  function n() {
    this.groups = [];
  }
  function o(t) {
    this.groups = this.groups.map((i) => (i !== t && i.close(), i));
  }
  function s(t) {
    this.groups.length === 0 && t.open(), (this.groups = this.groups.concat(t));
  }
  function e(t) {
    (this.groups = this.groups.filter((i) => i !== t)),
      t.isOpen && this.groups.length > 0 && this.openFirst();
  }
  function a() {
    this.groups.length > 0 && this.groups[0].open();
  }
}
const Ye = {
  transclude: {
    heading: "spAccordionGroupHeading",
    content: "spAccordionGroupContent",
  },
  require: { accordion: "^spAccordion" },
  templateUrl: "spCommon/components/accordion/sp-accordion-group.nghtml",
  controller: ["$element", "$scope", Ke],
};
function Ke(n, o) {
  (this.$onInit = s.bind(this)),
    (this.$onDestroy = e.bind(this)),
    (this.open = a.bind(this)),
    (this.close = t.bind(this)),
    o.$watch(
      () => this.isOpen,
      (i) => {
        i
          ? n.addClass("sp-accordion-group--open")
          : n.removeClass("sp-accordion-group--open");
      },
    );
  function s() {
    (this.isOpen = !1),
      this.accordion.addGroup(this),
      n.addClass("sp-accordion-group");
  }
  function e() {
    this.accordion.removeGroup(this);
  }
  function a() {
    (this.isOpen = !0), this.accordion.closeOthers(this);
  }
  function t() {
    this.isOpen = !1;
  }
}
const Xe = {
  bindings: {
    listItem: "<",
    listItemProgress: "<",
    listItemSize: "<",
    listItemGlyph: "<?",
    listItemIcon: "<?",
  },
  templateUrl: "spCommon/components/fileList/sp-file-list-item.nghtml",
  controller: Ze,
};
function Ze() {
  this.$onInit = () => {
    (this.showGlyph = !!this.listItemGlyph),
      (this.showIcon = !!this.listItemIcon),
      (this.showPercentage = !this.showGlyph && !this.showIcon);
  };
}
const Qe = {
    transclude: !0,
    template: `
<div
    class="sp-loader">

    <div
        class="sp-loader__message"
        ng-transclude>
    </div>

    <div
        ng-include="'svg/crop.svg'">
    </div>

</div>`,
  },
  Ve = {
    bindings: { backgroundImage: "@?", completed: "<" },
    templateUrl: "spCommon/components/progress/sp-progress.nghtml",
    controller: ["$element", "$scope", "d3", et],
  };
function et(n, o, s) {
  const e = 2 * Math.PI,
    a = n[0].querySelector(".sp-progress__svg"),
    t = s.select(a),
    i = a.getBoundingClientRect().width,
    r = a.getBoundingClientRect().height,
    c = t.append("g").attr("transform", `translate(${i / 2},${r / 2})`),
    g = s.arc().innerRadius(24).outerRadius(35).startAngle(0),
    p = c
      .append("path")
      .datum({ endAngle: this.completed * e })
      .classed("sp-progress__arc", !0)
      .attr("d", g);
  (this.$onInit = l.bind(this)),
    o.$watch(() => this.completed, U.debounce(u)),
    o.$watch(
      () => this.backgroundImage,
      (b) => {
        b && (this.coverStyle.backgroundImage = `url('${b}')`);
      },
    );
  function l() {
    this.backgroundImage &&
      (this.coverStyle = {
        backgroundSize: "cover",
        backgroundPosition: "center center",
      });
  }
  function u(b) {
    L.isNumber(b) &&
      (p
        .transition()
        .duration(50)
        .attrTween("d", m(b * e)),
      b >= 1
        ? (n.addClass("sp-progress--completed"),
          n.removeClass("sp-progress--pending"))
        : b === 0
          ? (n.addClass("sp-progress--pending"),
            n.removeClass("sp-progress--completed"))
          : (n.removeClass("sp-progress--completed"),
            n.removeClass("sp-progress--pending")));
    function m(v) {
      return (E) => (_) => (
        (E.endAngle = s.interpolate(E.endAngle, v)(_)), g(E)
      );
    }
  }
}
const tt = {
    bindings: {
      isActive: "<",
      headingTitle: "<",
      headingSubtitle: "<?",
      progressBackgroundImage: "<?",
      progressValue: "<",
    },
    templateUrl: "spCommon/components/jobs/sp-job.nghtml",
  },
  nt = {
    bindings: { heading: "<?" },
    template: `
<div
    class="sp-separator__heading"
    ng-if="$ctrl.heading"
    ng-bind="$ctrl.heading">
</div>

<div
    class="sp-separator__line">
</div>
`,
  };
function ot() {
  return {
    isOnline: we,
    domEventScopeEmitter: n,
    domEventScopeBroadcaster: o,
    searchContains: s,
    getSearchParamsFromUrl: e,
    addSecondsToEpoch: a,
  };
  function n(t, i) {
    return (r) => t.$emit(`${i ? i + ":" : ""}${r.type}`, r);
  }
  function o(t, i) {
    return (r) => t.$broadcast(`${i ? i + ":" : ""}${r.type}`, r);
  }
  function s(t, i = !1) {
    return function (r) {
      let c;
      try {
        c = new URL(r.toLowerCase());
      } catch (p) {
        if (p instanceof TypeError) return !1;
        throw p;
      }
      const g = e(c);
      return i ? !!g.get(t.toLowerCase()) : g.has(t.toLowerCase());
    };
  }
  function e(t) {
    const i = new URL(t);
    return new URLSearchParams(i.search.slice(1));
  }
  function a(t, i) {
    return t ? i + t * 1e3 : i || 0;
  }
}
const st = ["$http", "$localForage", "$q", "spConfig", "spUtils", rt];
function rt(n, o, s, e, a) {
  return { check: t, logout: i, tokensFromCode: r };
  function t() {
    return o.getItem("auth", !0).then(c(new Date().getTime()));
  }
  function i() {
    return o.getItem("auth").then(l).then(u);
    function l({ accessToken: b }) {
      return n.get(e.auth.logoutUrl, { params: { access_token: b } });
    }
    function u() {
      return o.removeItem([
        "accessToken",
        "refreshToken",
        "tokenExpirationEpoch",
      ]);
    }
  }
  function r(l) {
    return n
      .post(e.auth.tokenUrl, null, {
        params: {
          grant_type: "authorization_code",
          client_id: e.auth.clientId,
          code: l,
          redirect_uri: e.auth.redirectUri,
          scope: e.auth.scope,
        },
      })
      .then(p);
  }
  function c(l) {
    return function (u) {
      return u.expirationDate === null
        ? s.reject(new Error("No expiration date"))
        : l >= u.expirationDate
          ? g(u).then(p)
          : u;
    };
  }
  function g(l) {
    return l.refreshToken === null
      ? s.reject(new Error("No refresh token found"))
      : n.post(e.auth.url, {
          grant_type: "refresh_token",
          refresh_token: l.refreshToken,
          scope: e.auth.scope,
        });
  }
  function p(l) {
    const u = a.addSecondsToEpoch(l.data.expires_in, new Date().getTime());
    if (l.data.stat === "ok") {
      const { access_token: b, refresh_token: m } = l.data;
      return o.setItem("auth", {
        accessToken: b,
        refreshToken: m,
        expirationDate: u,
      });
    }
    return s.reject(l.data);
  }
}
const it = [
  "$http",
  "$localForage",
  "$q",
  "$rootScope",
  "online",
  "spConfig",
  "spAuth",
  "spLogger",
  "spPhotoStatus",
  "fs",
  "path",
  "request",
  at,
];
function at(n, o, s, e, a, t, i, r, c, g, p, l) {
  const u = "sp-api-at-plan-photo-count-limit",
    b = "sp-api-at-gallery-photo-count-limit",
    m = U.throttle(() => e.$apply(), 66),
    v = {},
    E = {
      AT_PLAN_PHOTO_LIMIT_ERROR: u,
      AT_GALLERY_PHOTO_LIMIT_ERROR: b,
      getStudioInfo: M,
      getBrands: W,
      getGalleryDefaults: C,
      getGalleries: h,
      getAlbums: k,
      createGallery: O,
      createAlbum: J,
      nestAlbum: S,
      photoExists: N,
      getWatermarks: j,
      uploadPhoto: z,
      abortRequest: Y,
    };
  return E;
  function _(w, A = {}) {
    if (a.status) return F();
    {
      let D;
      return s((R) => {
        D = e.$on("isOnline", (K, te) => {
          te && (D(), R(F()));
        });
      });
    }
    function F() {
      return i
        .check()
        .then(() => o.getItem("auth"))
        .then(({ accessToken: D }) => {
          const R = new FormData();
          return (
            U.isEmpty(A) ||
              Object.keys(A).forEach((K) => {
                R.append(K, A[K]);
              }),
            R.append("method", w),
            R.append("access_token", D),
            n({
              method: "POST",
              url: t.api.url,
              headers: { "Content-type": void 0 },
              data: R,
            })
          );
        })
        .then(({ data: D }) => (D.stat === "ok" ? s.resolve(D) : s.reject(D)));
    }
  }
  function M() {
    return _("sp.studio.info").then(({ plan: w, user: A }) => ({
      plan: w,
      user: A,
    }));
  }
  function W() {
    return _("sp.brand.get_list").then(({ brands: w }) => w);
  }
  function C(w) {
    return _("sp.brand.get_event_defaults", { brand_id: w }).then(
      ({ event_defaults: A }) => A,
    );
  }
  function h(w, A) {
    const F = {
      include_archived: 1,
      order_by: "last_updated",
      order_by_descending: 1,
      limit: 100,
    };
    return (
      w && (F.brand_id = w),
      _("sp.event.get_list", angular.extend(F, A)).then(({ events: D }) => D)
    );
  }
  function k(w) {
    return _("sp.album.get_list", { event_id: w }).then(({ albums: A }) => A);
  }
  function O(w) {
    return L.isUndefined(w.event_name)
      ? s.reject(new Error("Must provide a name when creating a gallery."))
      : _("sp.event.create", w).then(({ event: A }) => A);
  }
  function J(w) {
    return _("sp.album.create", w).then(({ album: A }) => A);
  }
  function S(w, A) {
    return _("sp.album.move", { album_id: A, parent_id: w }).then(
      ({ album: F }) => F,
    );
  }
  function N(w) {
    return _("sp.event.photo_exists", {
      event_id: w.galleryId,
      photo_name: p.parse(w.path).base,
      album_id: w.albumId,
    }).then(({ photo_exists: A }) => A);
  }
  function j(w) {
    return _("sp.watermark.get_list", { brand_id: w }).then(
      ({ watermarks: A }) => A,
    );
  }
  function z(w) {
    return i
      .check()
      .then(() => o.getItem("auth"))
      .then(({ accessToken: A }) => {
        const F = {
          method: "sp.photo.upload",
          access_token: A,
          event_id: w.galleryId,
          watermark_id: w.watermarkId ? w.watermarkId : "no",
          photo: g.createReadStream(w.path),
        };
        w.albumId && (F.album_id = w.albumId);
        const D = () => {
          const R = { url: t.api.url, formData: F };
          t.throttleGroup && (R.streamTransform = t.throttleGroup.throttle()),
            K(R, w);
          function K(te, P) {
            r.append(`${P.path}: Attempting to upload photo`),
              (P.socketError = void 0),
              (v[P.requestId] = l
                .post(te)
                .on("progress", (q) => {
                  const X = q.loaded / q.total;
                  (P.transferred = X),
                    X === 0
                      ? (P.status = c.PENDING)
                      : X > 0 && X < 1 && (P.status = c.IN_PROGRESS),
                    m();
                })
                .on("error", (q) => {
                  r.append(`${P.path}: Stream error: ${q}`),
                    (P.socketError = q),
                    (P.shouldRetry = !0),
                    e.$applyAsync(() => {
                      e.$broadcast("spApi:retryUpload", { photo: P });
                    });
                })
                .on("response", (q) => {
                  if (
                    (r.append(`${P.path}: Server response: ${q.statusCode}`),
                    q.statusCode === 504)
                  ) {
                    (P.shouldRetry = !0),
                      e.$applyAsync(() => {
                        e.$broadcast("spApi:retryUpload", { photo: P });
                      });
                    return;
                  }
                  const se = [];
                  q.on("data", (ne) => se.push(ne)).on("end", () => {
                    const ne = Buffer.concat(se).toString();
                    let H;
                    try {
                      H = L.fromJson(ne);
                    } catch {
                      H = null;
                    }
                    return (
                      e.$applyAsync(() => {
                        const ee = H && H.stat !== "ok",
                          d = ee && H.code === "limit_reached",
                          f =
                            d &&
                            H.msg ===
                              "Studio has reached the photo plan limit, please upgrade your plan or delete photos.",
                          y =
                            d &&
                            H.msg ===
                              "The event has reached the maximum photo limit of 100000, please delete photos and retry your upload.";
                        if (f || y)
                          (P.status = c.PENDING),
                            (P.transferred = 0),
                            (P.error = f
                              ? E.AT_PLAN_PHOTO_LIMIT_ERROR
                              : E.AT_GALLERY_PHOTO_LIMIT_ERROR);
                        else {
                          const I = q.statusCode > 399;
                          (P.status = c.COMPLETED),
                            (P.transferred = 1),
                            (ee || I) && (P.error = H);
                        }
                        e.$broadcast("spApi:uploadCompleted", { photo: P });
                      }),
                      delete v[P.requestId],
                      H
                    );
                  });
                }));
          }
        };
        return w.skipDuplicates
          ? N(w).then((R) =>
              R
                ? (e.$applyAsync(() => {
                    (w.transferred = 1),
                      (w.duplicate = !0),
                      (w.status = c.COMPLETED),
                      e.$broadcast("spApi:uploadCompleted", { photo: w });
                  }),
                  s.resolve())
                : s.resolve(D()),
            )
          : s.resolve(D());
      });
  }
  function Y(w) {
    const A = v[w];
    return A ? (A.abort(), delete v[w], !0) : !1;
  }
}
const lt = [
  "$localForage",
  "$q",
  "$rootScope",
  "$timeout",
  "fileType",
  "fs",
  "ipcRenderer",
  "nanoid",
  "readChunk",
  "spAlbum",
  "spAlert",
  "spApi",
  "spConfig",
  "spJobStatus",
  "spLogger",
  "spPhotoStatus",
  "stringRegexp",
  ut,
];
function ut(n, o, s, e, a, t, i, r, c, g, p, l, u, b, m, v, E) {
  const M = {
      galleryOptions: {
        brand: null,
        gallery: null,
        watermark: null,
        skipDuplicates: !0,
      },
      basePath: null,
      pathList: [],
      fromFolder: !1,
    },
    W = U.throttle(() => {
      C.active = C.activeFromJobs(C.active, C.jobs, [
        (d) => d.status === v.PENDING,
      ]);
    }, 16),
    C = {
      isPaused: !1,
      isCreatingMissingAlbums: !1,
      pause: h,
      resume: k,
      cancel: O,
      staging: L.copy(M),
      jobs: [],
      uploadCompleteHandler: J,
      active: [],
      activeFromJobs: S,
      activateNext: W,
      basePathFromPathList: N,
      pathListFromTree: j,
      folderListFromTree: z,
      pathListFromFileList: Y,
      checkPathList: w,
      maybeGetPathListFromDataTransfer: A,
      maybeGetPathListFromFolder: F,
      pathListToStaging: P,
      resetStaging: q,
      jobFromStaging: X,
      enqueueJobFromStaging: se,
      persist: U.throttle(ne, 5e3),
      restore: H,
    };
  return C;
  function h() {
    C.isPaused = !0;
  }
  function k() {
    (C.isPaused = !1),
      C.active.forEach((f) => {
        f.shouldRetry && (d(f), (f.shouldRetry = !1));
      }),
      (C.active = U.reject(C.active, { status: v.PENDING })),
      C.activateNext();
    function d(f) {
      (f.status = v.PENDING), (f.transferred = 0);
    }
  }
  function O(d) {
    (C.active = []),
      (d.progress = 1),
      (d.status = b.CANCELED),
      (d.photos = d.photos.map(
        (f) => (
          f.status <= v.IN_PROGRESS &&
            (l.abortRequest(f.requestId),
            (f.status = v.CANCELED),
            (f.transferred = 1)),
          f
        ),
      )),
      C.persist();
  }
  function J(d, f) {
    const y = U.find(C.jobs, { id: f.photo.jobId });
    (y.progress = y.photos.reduce(I, 0) / y.photos.length),
      (y.status === b.PENDING || y.status === b.IN_PROGRESS) &&
        (y.progress === 0
          ? (y.status = b.PENDING)
          : y.progress > 0 && y.progress < 1
            ? (y.status = b.IN_PROGRESS)
            : ((y.status = b.COMPLETED),
              s.$broadcast("spQueue:uploadComplete", { job: y }))),
      f.photo.status === v.COMPLETED &&
        ((C.active = U.reject(C.active, { path: f.photo.path })), W()),
      C.persist();
    function I($, x) {
      return $ + x.transferred;
    }
  }
  function S(d, f, y = []) {
    if (C.isPaused) return d;
    const I = 5,
      $ = f.reduce(
        (x, B) =>
          !x && B.status !== b.COMPLETED && B.status !== b.CANCELED ? B : x,
        null,
      );
    if ($ !== null) {
      if (d.length === I || U.isEmpty($.photos)) return d;
      const x = y.concat((ae) => d.indexOf(ae) === -1),
        B = $.photos.filter(ee(x)),
        oe = U.take(B, I - d.length);
      if (!U.isEmpty(oe)) return oe.forEach(l.uploadPhoto), d.concat(oe);
    }
    return d;
  }
  function N(d) {
    if (U.isEmpty(d)) return null;
    const f = d.reduce(
      (y, I) =>
        U.takeWhile(T.dirname(I.path).split(T.sep), ($, x) => y[x] === $),
      T.dirname(d[0].path).split(T.sep),
    );
    return T.join("/", ...f);
  }
  function j(d, f) {
    return U.flatten(
      f.children.map((y) =>
        y.type === "dir"
          ? j(T.join(d, y.name), y)
          : { path: T.join(d, y.name), size: y.size },
      ),
    );
  }
  function z(d, f) {
    return U.flatten(
      f.children.map((y) => {
        let I = [];
        return (
          y.type === "dir" &&
            ((I = I.concat(T.join(d, y.name))),
            U.isEmpty(y.children.filter(($) => $.type === "dir")) ||
              (I = I.concat(z(T.join(d, y.name), y)))),
          I
        );
      }),
    );
  }
  function Y(d, f) {
    C.staging.fromFolder = !1;
    let y = [];
    for (let I = 0; I < f.length; I++) {
      const $ = T.join(d, f.item(I).name);
      y.push({ path: $, size: t.inspect($).size });
    }
    return { pathList: y, folderList: [] };
  }
  function w(d) {
    return d.reduce(
      (f, y) => {
        let I = null;
        try {
          const $ = c.sync(y.path, 0, 262);
          I = a.check($);
        } catch {}
        return (
          !I || (I && I.mime !== "image/jpeg")
            ? f.invalid.unsupported.push(y)
            : y.size > 50 * Math.pow(1024, 2)
              ? f.invalid.filesize.push(y)
              : f.valid.push(y),
          f
        );
      },
      { valid: [], invalid: { unsupported: [], filesize: [] } },
    );
  }
  function A(d) {
    const y = te(d.items)
      .filter((I) => K(I.name))
      .reduce(
        (I, $) => (
          $ !== null &&
            ($.isDirectory ? (I.folders += 1) : $.isFile && (I.files += 1)),
          I
        ),
        { files: 0, folders: 0 },
      );
    if (y.files > 0 && y.folders > 0)
      return o.reject("upload.new.errors.mixedType");
    if (y.files > 0) {
      const I = T.parse(d.files.item(0).path).dir;
      return o.resolve(C.pathListFromFileList(I, d.files));
    } else if (y.folders === 1) {
      const I = d.files.item(0).path;
      return C.maybeGetPathListFromFolder(I);
    }
    return o.reject("upload.new.errors.mixedType");
  }
  function F(d) {
    return (
      (C.staging.fromFolder = !0),
      (C.staging.basePath = d),
      D(d)
        .then(R)
        .then((f) => ({ pathList: j(d, f), folderList: z("", f) }))
    );
  }
  function D(d) {
    return o((f) => {
      i.once("inspectTree-tree", (y, I) => f(I)), i.send("inspectTree", d);
    });
  }
  function R(d, f = 1) {
    if (((d.children = d.children.filter(($) => K($.name))), f > 4))
      return o.reject("upload.new.errors.tooNested");
    const y = d.children.filter(($) => $.type === "file"),
      I = d.children.filter(($) => $.type === "dir");
    return y.length > 0 && I.length > 0
      ? o.reject("upload.new.errors.mixedType")
      : I.length > 0
        ? o.all(I.map(($) => R($, f + 1))).then(() => o.resolve(d))
        : o.resolve(d);
  }
  function K(d) {
    return !/^\./.test(d) && Ie.not(d);
  }
  function te(d) {
    let f = [];
    for (let y = 0; y < d.length; y++) f = f.concat(d[y].webkitGetAsEntry());
    return f;
  }
  function P(d) {
    return {
      basePath: C.staging.basePath || C.basePathFromPathList(d),
      checked: C.checkPathList(d),
      pathList: d,
    };
  }
  function q() {
    C.staging = L.copy(M);
  }
  function X(d, f) {
    const y = r(),
      I = g.albumPathsFromAlbums("", f),
      $ = g.getMissingAlbums(I, d.folderList),
      x = o.defer();
    let B;
    return (
      e(() => {
        x.resolve();
      }, 300),
      g
        .createMissingAlbums(d.galleryOptions.gallery.id, I, $)
        .then(
          (Z) => (
            (B = {
              id: y,
              gallery: d.galleryOptions.gallery,
              watermark: d.galleryOptions.watermark,
              status: 0,
              progress: 0,
              totalFilesize: d.checked.valid.reduce(
                (Q, pe) => (Q += pe.size),
                0,
              ),
              basePath: d.basePath,
              photos: d.checked.valid.map(oe),
            }),
            (B.albumPaths = Z || I),
            (B.photos = B.photos.map((Q) =>
              Object.assign({}, Q, {
                albumId: g.albumFromPhoto(B.albumPaths, Q),
              }),
            )),
            x.promise
          ),
        )
        .then(() => ((C.isCreatingMissingAlbums = !1), B))
    );
    function oe(Z) {
      return {
        requestId: r(),
        path: Z.path,
        jobId: y,
        galleryId: d.galleryOptions.gallery.id,
        watermarkId: d.galleryOptions.watermark.id,
        albumPath: ae(d.basePath, Z.path),
        size: Z.size,
        transferred: 0,
        status: 0,
        skipDuplicates: d.galleryOptions.skipDuplicates,
      };
    }
    function ae(Z, Q) {
      return T.dirname(Q).replace(new RegExp("^" + E.escape(Z)), "");
    }
  }
  function se(d) {
    return (
      m.append(`Enqueueing job: ${JSON.stringify(d)}`),
      (C.isCreatingMissingAlbums = !0),
      l
        .getAlbums(d.galleryOptions.gallery.id)
        .then((f) => C.jobFromStaging(d, f))
        .then(
          (f) => (
            (C.jobs = C.jobs.concat(f)), C.resetStaging(), C.persist(), f
          ),
        )
        .catch(() => {
          C.isCreatingMissingAlbums = !1;
        })
    );
  }
  function ne() {
    return n.setItem("queue", C.jobs);
  }
  function H(d = []) {
    return n
      .getItem("queue", !0)
      .then((f) => ((C.jobs = f.filter(ee(d))), C.jobs));
  }
  function ee(d) {
    return (f) => d.every((y) => y(f));
  }
}
const ct = ["$q", "path", "spApi", "stringRegexp", pt];
function pt(n, o, s, e) {
  return {
    albumPathsFromAlbums: t,
    getMissingAlbums: i,
    createMissingAlbums: r,
    albumFromPhoto: c,
  };
  function t(g, p) {
    return U.flatten(
      p.map((l) => {
        let u = [{ path: o.join(g, l.name), album: U.omit(l, "sub_albums") }];
        return (
          (l.sub_albums || !U.isEmpty(l.sub_albums)) &&
            (u = u.concat(t(o.join(g, l.name), l.sub_albums))),
          u
        );
      }),
    );
  }
  function i(g, p) {
    return U.difference(
      p,
      g.map((l) => l.path),
    );
  }
  function r(g, p, l) {
    return U.isEmpty(l)
      ? n.resolve()
      : n
          .all(
            l.map((u) => {
              const b = o.parse(u).base;
              return s.createAlbum({ event_id: g, album_name: b });
            }),
          )
          .then((u) =>
            n.all(
              u.map((b, m) => {
                const v = o.parse(l[m]);
                if (v.dir !== v.root) {
                  const E = l.indexOf(v.dir),
                    _ = E === -1 ? U.find(p, { path: v.dir }).album : u[E];
                  return s
                    .nestAlbum(_.id, b.id)
                    .then((M) => ({ album: M, path: l[m] }));
                }
                return n.resolve({ album: b, path: l[m] });
              }),
            ),
          )
          .then((u) => p.concat(u));
  }
  function c(g, p) {
    const { root: l, dir: u, base: b } = o.parse(p.albumPath),
      m = u.replace(new RegExp("^" + e.escape(l)), ""),
      v = U.find(g, { path: o.join(m, b) });
    return (v && v.album.id) || null;
  }
}
const dt = ["spApi", ht];
function ht(n) {
  return {
    newGallery: null,
    create: n.createGallery,
    isWithinPhotoCountLimit: (o) => o.photo_count < 1e5,
  };
}
const G = ie.cwd(__dirname).read("env.json", "json"),
  gt = ["$localForage", "streamThrottle", "process", ft];
function ft(n, o, s) {
  const e = {
    version: G.APP_VERSION,
    auth: {
      url: G.AUTH_URL,
      tokenUrl: G.AUTH_TOKEN_URL,
      logoutUrl: G.AUTH_TOKEN_LOGOUT_URL,
      clientId: G.AUTH_CLIENT_ID,
      redirectUri: G.AUTH_REDIRECT_URI,
      scope: G.AUTH_SCOPE.join(" "),
    },
    api: { url: G.API_BASE_URL },
    plan: { url: G.STUDIO_BASE_URL + "/account/planbilling" },
    gallery: { getUrl: r },
    settings: {},
    restoreDefaultSettings: a,
    update: {
      feedUrl: `${G.API_BASE_URL}${G.UPDATE_FEED_URL}`,
      platform: s.platform,
      currentVersion: G.APP_VERSION,
    },
    log: { url: G.LOG_URL },
    settingsForm: {},
    loadSettings: t,
    saveSettings: i,
    throttleGroup: null,
  };
  return e;
  function a() {
    return (e.settings = {
      alerts: {
        allow: !0,
        events: { complete: !0, error: !0 },
        notifications: { sound: !0, icon: !0, notify: !0 },
      },
      speed: { isThrottled: !1, throttle: 1 },
    });
  }
  function t(c) {
    if (
      (c &&
        ((e.settings = c),
        c.speed &&
          c.speed.throttle &&
          (e.settings.speed.throttle = parseInt(c.speed.throttle, 10))),
      e.settings.speed &&
        e.settings.speed.isThrottled &&
        e.settings.speed.throttle)
    ) {
      const g = e.settings.speed.throttle * 1024;
      e.throttleGroup = new o.ThrottleGroup({ rate: g });
    } else e.throttleGroup = null;
  }
  function i(c) {
    return n.setItem("settings", c);
  }
  function r(c, g) {
    return `${G.STUDIO_BASE_URL}/v2/${c}/gallery/edit/${g}`;
  }
}
const mt = [
  "electron",
  "electron.remote",
  "notification",
  "process",
  "spConfig",
  bt,
];
function bt(n, o, s, e, a) {
  const t = { icon: i, sound: r, notify: c, completed: g, hasError: p };
  return t;
  function i() {
    if (e.platform === "darwin") o.app.dock.bounce("informational");
    else if (e.platform === "win32") {
      const l = o.getCurrentWindow();
      l.flashFrame(!0), l.once("focus", () => l.flashFrame(!1));
    }
  }
  function r() {
    n.shell.beep();
  }
  function c({ title: l, body: u }) {
    return new s(l, { body: u });
  }
  function g(l, u) {
    a.settings.alerts.allow &&
      a.settings.alerts.events.complete &&
      (a.settings.alerts.notifications.sound && t.sound(),
      a.settings.alerts.notifications.icon && t.icon(),
      a.settings.alerts.notifications.notify &&
        t.notify({
          title: "ShootProof Upload Complete",
          body: `Your photos have finished uploading to the ${u.job.gallery.name} gallery!`,
        }));
  }
  function p(l) {
    a.settings.alerts.allow &&
      a.settings.alerts.events.error &&
      (a.settings.alerts.notifications.sound && t.sound(),
      a.settings.alerts.notifications.icon && t.icon(),
      a.settings.alerts.notifications.notify &&
        t.notify({
          title: "ShootProof Upload Error",
          body: `There was a problem with your photo upload to the ${l.gallery.name} gallery.`,
        }));
  }
}
const yt = ["ipcRenderer", "$rootScope", "spLogger", vt];
function vt(n, o, s) {
  const e = {
    lastChecked: null,
    status: "IDLE",
    info: null,
    checkForUpdates: a,
    quitAndInstall: t,
  };
  return (
    n.on("update-status", (i, r) => {
      o.$apply(() => {
        (e.status = r.status),
          (e.info = r.info || r.error || null),
          s.append(`Update status: ${JSON.stringify(r.status)}`);
      });
    }),
    e
  );
  function a(i = new Date().getTime()) {
    s.append("Checking for updates"),
      n.send("check-update"),
      (e.lastChecked = i);
  }
  function t() {
    s.append("Restarting to install update"), n.send("install-update");
  }
}
const Ct = ["$http", "$interval", "$localForage", "$q", "spConfig", wt];
function wt(n, o, s, e, a) {
  const t = {
    locked: !1,
    queue: [],
    append: i,
    persist: c,
    sendLog: p,
    clear: g,
    transact: r,
  };
  return t;
  function i(l, u = new Date().toISOString()) {
    return t.transact(
      5,
      1e3,
      () => ((t.queue = t.queue.concat({ ts: u, m: l })), e.resolve()),
    );
  }
  function r(l, u, b) {
    if (!t.locked) return m();
    return e((v, E) => {
      let _ = o(() => {
        if (l === 0) return o.cancel(_), E();
        if ((l--, !t.locked)) return v(m());
      }, u);
    });
    function m() {
      return (
        (t.locked = !0),
        b().finally(() => {
          t.locked = !1;
        })
      );
    }
  }
  function c() {
    return r(5, 1e3, () =>
      s
        .getItem("debugLog", !0)
        .catch(() => s.setItem("debugLog", []))
        .then((l) => s.setItem("debugLog", l.concat(t.queue)))
        .then(() => {
          t.queue = [];
        }),
    );
  }
  function g() {
    return r(5, 1e3, () =>
      s.setItem("debugLog", []).then(() => ((t.queue = []), e.resolve())),
    );
  }
  function p() {
    return s.getItem("debugLog", !0).then((l) => {
      if (!U.isEmpty(l)) {
        let u,
          b = !1;
        try {
          (u = JSON.stringify(l)), (b = !0);
        } catch {
          u = "There was an error stringifying the debug log";
        }
        return n.post(a.log.url, u).then((m) => (b ? t.clear() : m));
      }
      return e.resolve();
    });
  }
}
const It = { PENDING: 0, IN_PROGRESS: 1, COMPLETED: 2, CANCELED: 3 },
  Ut = { PENDING: 0, IN_PROGRESS: 1, COMPLETED: 2, CANCELED: 3 };
function Et() {
  var n = ["bytes", "KB", "MB", "GB", "TB", "PB"];
  return function (o, s = 0) {
    if (isNaN(parseFloat(o)) || !isFinite(o)) return "?";
    for (var e = 0; o >= 1024 && e < n.length - 1; ) (o /= 1024), e++;
    return o.toFixed(+s) + " " + n[e];
  };
}
const At = ["path", _t];
function _t(n) {
  return function (o) {
    return n.parse(o).base;
  };
}
function $t() {
  return (n, o = 0) => {
    const s = +n * 100;
    return U.isNaN(s)
      ? `---${o ? "." + "-".repeat(o) : ""}%`
      : s.toFixed(o) + "%";
  };
}
const V = L.module("spDesktopUploader.common", ["LocalForageModule"])
    .value("electron", re)
    .value("electron.remote", de)
    .value("process", he)
    .value("fs", ie)
    .value("path", T)
    .value("readChunk", ge)
    .value("fileType", { check: fe })
    .value("d3", me)
    .value("nanoid", be)
    .value("stringRegexp", { escape: ye })
    .value("streamThrottle", ve)
    .value("request", Ce)
    .value("notification", Notification)
    .value("ipcRenderer", re.ipcRenderer)
    .value("online", { status: !1 })
    .constant("spPhotoStatus", It)
    .constant("spJobStatus", Ut)
    .directive("spExternalLink", Se)
    .directive("spContextMenu", Te)
    .directive("spWebview", Fe)
    .directive("spDropzone", Me)
    .directive("spBrowseDirectory", ze)
    .directive("spFocus", xe)
    .component("spAccordion", We)
    .component("spAccordionGroup", Ye)
    .component("spFileListItem", Xe)
    .component("spLoader", Qe)
    .component("spProgress", Ve)
    .component("spJob", tt)
    .component("spSeparator", nt)
    .factory("spUtils", ot)
    .factory("spAuth", st)
    .factory("spApi", it)
    .factory("spQueue", lt)
    .factory("spAlbum", ct)
    .factory("spGallery", dt)
    .factory("spConfig", gt)
    .factory("spAlert", mt)
    .factory("spUpdate", yt)
    .factory("spLogger", Ct)
    .filter("filesize", Et)
    .filter("filename", At)
    .filter("percentage", $t).name,
  kt = { templateUrl: "spAuth/header/sp-auth-header.nghtml" },
  Lt = {
    templateUrl: "spAuth/check/sp-auth-check.nghtml",
    controller: ["$localForage", "$state", Pt],
  };
function Pt(n, o) {
  this.authorize = s;
  function s() {
    return o.go("auth.new");
  }
}
const Ot = {
  templateUrl: "spAuth/new/sp-auth-new.nghtml",
  controller: [
    "$http",
    "$localForage",
    "$state",
    "$q",
    "$scope",
    "spAuth",
    "spConfig",
    "spUtils",
    St,
  ],
};
function St(n, o, s, e, a, t, i, r) {
  const c = r.searchContains("code", !0),
    g = r.searchContains("error", !0);
  (this.oauthUrl = l(
    i.auth.url,
    i.auth.clientId,
    i.auth.redirectUri,
    i.auth.scope,
  )),
    a.$on("spWebview:load-commit", p);
  function p(b, m) {
    const v = m.url || m.newURL || "";
    let E;
    if (g(v))
      return r.getSearchParamsFromUrl(v).get("error_reason") === "user_denied"
        ? s.go("auth.check")
        : e.reject();
    if (
      (c(v)
        ? (E = r.getSearchParamsFromUrl(v).get("code"))
        : u(v) && (E = u(v)[1]),
      E)
    )
      return t.tokensFromCode(E).then(() => s.go("upload.new"));
  }
  function l(b, m, v, E) {
    return (
      b +
      "?response_type=code&client_id=" +
      m +
      "&redirect_uri=" +
      v +
      "&scope=" +
      E
    );
  }
  function u(b) {
    return b.match(/showcode\/code\/(.*)/);
  }
}
const Dt = {
  template: "&copy; {{ $ctrl.thisYear }} ShootProof, LLC",
  controller: Tt,
};
function Tt() {
  this.thisYear = new Date().getFullYear();
}
const Nt = ["$stateProvider", Ft];
function Ft(n) {
  n.state("auth", {
    public: !0,
    abstract: !0,
    url: "/auth",
    template: `
                <sp-auth-header class="sp-app__header"></sp-auth-header>
                <div ui-view="body" class="sp-app__body"></div>
                <div class="sp-app__footer" ui-view="footer"></div>`,
  })
    .state("auth.check", {
      public: !0,
      url: "/check",
      views: {
        body: {
          template:
            '<sp-auth-check class="sp-auth-check__container"></sp-auth-check>',
        },
        footer: { template: "<sp-auth-check-footer></sp-auth-check-footer>" },
      },
    })
    .state("auth.new", {
      public: !0,
      url: "/new",
      views: {
        body: {
          template:
            '<sp-auth-new class="sp-auth-new__container"></sp-auth-new>',
        },
      },
    });
}
const Rt = {
    authorizeHeading:
      "Uploading your photos to ShootProof has never been easier. Let's get started!",
    authorizeButton: "Authorize Uploader",
  },
  Gt = ["$translateProvider", jt];
function jt(n) {
  n.useSanitizeValueStrategy("escape")
    .translations("en", { auth: { check: Rt } })
    .preferredLanguage("en");
}
const Mt = L.module("spDesktopUploader.auth", [
    "ui.router",
    "LocalForageModule",
    "pascalprecht.translate",
    V,
  ])
    .config(Nt)
    .config(Gt)
    .component("spAuthHeader", kt)
    .component("spAuthCheck", Lt)
    .component("spAuthNew", Ot)
    .component("spAuthCheckFooter", Dt).name,
  qt = {
    templateUrl: "./spUpload/header/sp-upload-header.nghtml",
    controller: ["$uibModal", "spApi", "spLogger", Bt],
  };
function Bt(n, o, s) {
  (this.$onInit = e.bind(this)), (this.openSettings = a);
  function e() {
    o.getStudioInfo().then((t) => {
      (this.studioInfo = t),
        t.plan.type === "photo_count" &&
          (this.remainingCount = t.plan.allowed - t.plan.used),
        s.append(`Studio info: ${JSON.stringify(t)}`);
    });
  }
  function a() {
    return n.open({ component: "sp-settings" });
  }
}
const zt = {
  templateUrl: "./spUpload/new/sp-upload-new.nghtml",
  controller: [
    "$element",
    "$q",
    "$scope",
    "$state",
    "$timeout",
    "$translate",
    "fs",
    "path",
    "spLogger",
    "spQueue",
    Ht,
  ],
};
function Ht(n, o, s, e, a, t, i, r, c, g) {
  (this.$onInit = p.bind(this)),
    s.$on("spDropzone:drop", l.bind(this)),
    s.$on("spBrowseDirectory:change", u.bind(this));
  function p() {
    return (
      (this.isBusy = !1),
      t("upload.new.browseFolderButton")
        .then((m) => (this.browseFolderButtonLabel = m))
        .then(() => t("upload.new.browseFileButton"))
        .then((m) => (this.browseFileButtonLabel = m))
    );
  }
  function l(m, v) {
    let E = a(() => {
      this.isBusy = !0;
    }, 200);
    c.append("Dropped files/folders"),
      g
        .maybeGetPathListFromDataTransfer(v.dataTransfer)
        .then(b)
        .catch((_) => {
          a.cancel(E),
            n.removeClass("sp-dropzone--over"),
            n.removeClass("sp-dropzone--drop"),
            (this.isBusy = !1),
            (this.error = _);
        });
  }
  function u(m, v) {
    if (!v.target.files || v.target.files.length === 0) return;
    const E = v.target.files.item(0);
    if (v.target.webkitdirectory) {
      const _ = r.normalize(E.webkitRelativePath),
        M = _.split(r.sep).shift(),
        W = E.path.slice(0, -_.length),
        C = r.join(W, M);
      let h = a(() => {
        this.isBusy = !0;
      }, 200);
      g.maybeGetPathListFromFolder(C)
        .then(b)
        .catch((k) => {
          a.cancel(h), (this.isBusy = !1), (this.error = k);
        });
    } else {
      c.append("Browsed for files.");
      const _ = r.dirname(E.path);
      b(g.pathListFromFileList(_, v.target.files));
    }
  }
  function b({ pathList: m, folderList: v }) {
    return (
      (g.staging = U.assign({}, g.staging, g.pathListToStaging(m), {
        folderList: v,
      })),
      c.append(`Files to enqueue: ${g.staging.pathList.length}`),
      g.staging.pathList.length !== g.staging.checked.valid.length
        ? (c.append(
            `Skippable errors count: ${g.staging.pathList.length - g.staging.checked.valid.length}`,
          ),
          e.go("upload.errors"))
        : e.go("upload.options")
    );
  }
}
const xt = {
  template: `
        <div
            class="sp-upload-new__footer"
            ng-if="$ctrl.hasJobs()">

            <a
                class="sp-upload-new__footer__progress"
                ui-sref="queue"
                translate="upload.new.footer.progress">
            </a>

        </div>`,
  controller: ["spQueue", Wt],
};
function Wt(n) {
  this.hasJobs = () => n.jobs && !!n.jobs.length;
}
const Jt = {
  templateUrl: "spUpload/errors/sp-upload-errors.nghtml",
  controller: ["$state", "$timeout", "electron", "spQueue", Yt],
};
function Yt(n, o, s, e) {
  (this.$onInit = a.bind(this)),
    (this.showItemInFolder = s.shell.showItemInFolder),
    (this.basePath = e.staging.basePath),
    (this.recheck = t.bind(this)),
    (this.increaseRepeatLimit = r.bind(this)),
    (this.nextChunk = c),
    (this.canIgnore = g),
    (this.ignore = p.bind(this));
  function a() {
    (this.checked = e.staging.checked),
      (this.isBusy = !1),
      (this.groupLimit = 100),
      (this.errorCount = {
        total:
          this.checked.invalid.filesize.length +
          this.checked.invalid.unsupported.length,
        filesize: this.checked.invalid.filesize.length,
        unsupported: this.checked.invalid.unsupported.length,
      });
  }
  function t() {
    return (
      (this.isBusy = !0),
      e.staging.fromFolder
        ? e.maybeGetPathListFromFolder(e.staging.basePath).then(i)
        : i({ pathList: e.staging.pathList, folderList: e.staging.folderList })
    );
  }
  function i({ pathList: l, folderList: u }) {
    return (
      (e.staging = U.assign({}, e.staging, e.pathListToStaging(l), {
        folderList: u,
      })),
      e.staging.pathList.length !== e.staging.checked.valid.length
        ? o(() => n.reload(), 1e3)
        : n.go("upload.options")
    );
  }
  function r(l, u) {
    l - this.groupLimit > 0 && o(() => (this.groupLimit += u), 1e3);
  }
  function c(l, u) {
    return { from: l + 1, to: l + u };
  }
  function g() {
    return (
      e.staging &&
      e.staging.checked &&
      e.staging.checked.valid &&
      e.staging.checked.valid.length > 0
    );
  }
  function p() {
    this.canIgnore() && n.go("upload.options");
  }
}
const Kt = {
  templateUrl: "spUpload/options/sp-upload-options.nghtml",
  controller: [
    "lodash",
    "$localForage",
    "$q",
    "$scope",
    "$state",
    "spApi",
    "spPhotoStatus",
    "spQueue",
    "spGallery",
    Xt,
  ],
};
function Xt(n, o, s, e, a, t, i, r, c) {
  const g = { id: "no", name: "No Watermark" };
  (this.$onInit = p.bind(this)),
    (this.showBrands = l.bind(this)),
    e.$watch(
      () => this.galleryOptions.brand,
      (u) => {
        L.isDefined(u) &&
          ((r.staging.galleryOptions.brand = u),
          u !== null &&
            s
              .all([
                t.getGalleries(this.galleryOptions.brand.id),
                t.getWatermarks(this.galleryOptions.brand.id),
              ])
              .then(([b, m]) => {
                const v =
                  this.galleryOptions.gallery &&
                  this.galleryOptions.gallery.brand_id;
                (this.galleries = b),
                  (this.watermarks = [g].concat(m)),
                  (this.galleryOptions.gallery =
                    v === u.id ? this.galleryOptions.gallery : null),
                  (this.galleryOptions.watermark = this.watermarks[0]);
              }));
      },
    ),
    e.$watch(
      () => this.galleryOptions.gallery,
      (u) => {
        L.isDefined(u) &&
          ((r.staging.galleryOptions.gallery = u),
          n.isNull(u) ||
            (this.isGalleryWithinPhotoCountLimit =
              c.isWithinPhotoCountLimit(u)));
      },
    ),
    e.$watch(
      () => this.galleryOptions.skipDuplicates,
      (u) => {
        L.isDefined(u) && (r.staging.galleryOptions.skipDuplicates = u);
      },
    ),
    e.$watch(
      () => this.galleryOptions.watermark,
      (u) => {
        L.isDefined(u) && (r.staging.galleryOptions.watermark = u);
      },
    ),
    e.$watch("$ctrl.gallerySearch", (u, b) => {
      L.isDefined(u) &&
        u !== b &&
        ((this.isSearching = !0),
        t
          .getGalleries(this.galleryOptions.brand.id, { search_name: u })
          .then((m) => {
            (this.galleries = m), (this.isSearching = !1);
          }));
    }),
    e.$watch(
      () => r.isCreatingMissingAlbums,
      (u, b) => {
        u !== b && (this.isCreatingMissingAlbums = u);
      },
    );
  function p() {
    return (
      (this.isWorking = !0),
      (this.isCreatingMissingAlbums = !1),
      (this.isSearching = !1),
      (this.isGalleryWithinPhotoCountLimit = !0),
      (this.brands = []),
      (this.galleries = []),
      (this.watermarks = [g]),
      (this.galleryOptions = { skipDuplicates: !0 }),
      (this.stagingCount = {
        count: (r.staging.pathList && r.staging.pathList.length) || 0,
      }),
      t
        .getBrands()
        .then((u) => {
          const b = n.find(u, "is_default") || u[0] || null;
          return (
            (this.brands = u),
            (this.galleryOptions.brand = r.staging.galleryOptions.brand || b),
            t.getGalleries(this.galleryOptions.brand.id).then((m) => {
              (this.galleries = m),
                (this.galleryOptions.gallery = r.staging.galleryOptions.gallery
                  ? n.find(this.galleries, {
                      id: r.staging.galleryOptions.gallery.id,
                    })
                  : null);
            })
          );
        })
        .finally(() => {
          this.isWorking = !1;
        })
    );
  }
  function l() {
    return this.brands.length > 1;
  }
}
const Zt = {
  templateUrl: "spUpload/options/sp-upload-options-header.nghtml",
  controller: [
    "$scope",
    "$state",
    "lodash",
    "spLogger",
    "spQueue",
    "spGallery",
    Qt,
  ],
};
function Qt(n, o, s, e, a, t) {
  let i;
  (this.canStartUpload = c),
    (this.startUpload = g.bind(this)),
    (this.$onInit = r),
    n.$watch(
      () => a.staging.galleryOptions,
      () => {
        i = a.staging.galleryOptions;
      },
      !0,
    ),
    n.$watch(
      () => a.isCreatingMissingAlbums,
      (p, l) => {
        p !== l && (this.isCreatingMissingAlbums = p);
      },
    );
  function r() {
    this.isCreatingMissingAlbums = !1;
  }
  function c() {
    let p = i.gallery;
    return (
      !this.isCreatingMissingAlbums &&
      !s.isNil(i.brand) &&
      !s.isNil(p) &&
      t.isWithinPhotoCountLimit(p)
    );
  }
  function g() {
    return a
      .enqueueJobFromStaging(a.staging)
      .then((p) => (a.activateNext(), o.go("queue", { job: p.id })));
  }
}
const Vt = {
  template: `
        <div
            class="sp-upload-options__add-and-new"
            ng-click="$ctrl.addAndNew($ctrl.galleryOptions)"
            translate="upload.options.addAndNew">
        </div>`,
  controller: [
    "$scope",
    "$state",
    "lodash",
    "spPhotoStatus",
    "spQueue",
    "spGallery",
    en,
  ],
};
function en(n, o, s, e, a, t) {
  (this.addAndNew = i),
    n.$watch(
      () => a.staging.galleryOptions,
      (r) => {
        this.galleryOptions = r;
      },
    );
  function i(r) {
    let c = r.gallery;
    if (!s.isNil(c) && t.isWithinPhotoCountLimit(c) && r.brand)
      return a
        .enqueueJobFromStaging(a.staging)
        .then(() => (a.activateNext(), o.go("upload.new")));
  }
}
const tn = {
  templateUrl: "spUpload/gallery/sp-upload-gallery.nghtml",
  controller: ["$localForage", "$scope", "spApi", "spGallery", "spQueue", nn],
};
function nn(n, o, s, e, a) {
  (this.$onInit = t.bind(this)),
    o.$watch(
      () => this.newGalleryForm && this.newGalleryForm.$valid,
      (i) => {
        i ? (e.newGallery = this.newGalleryOptions) : (e.newGallery = null);
      },
    ),
    o.$watch(
      () => this.newGalleryOptions.brand,
      (i) => {
        if (i)
          return (
            (this.isWorking = !0),
            s
              .getGalleryDefaults(this.newGalleryOptions.brand.id)
              .then((r) => {
                const c = U.find(r, "is_default") || r[0] || null;
                (this.galleryDefaults = r),
                  (this.newGalleryOptions.galleryDefault = c),
                  (this.isWorking = !1);
              })
              .catch(() => {
                this.isWorking = !1;
              })
          );
      },
    );
  function t() {
    (this.isWorking = !0),
      (this.newGalleryOptions = {
        brand: null,
        name: null,
        shootDate: new Date(),
      }),
      (this.brands = []),
      s
        .getBrands()
        .then((i) => {
          const r = U.find(i, { id: a.staging.galleryOptions.brand.id });
          (this.brands = i), (this.newGalleryOptions.brand = r);
        })
        .catch(() => {
          this.isWorking = !1;
        });
  }
}
const on = {
  templateUrl: "spUpload/gallery/sp-upload-gallery-header.nghtml",
  controller: [
    "$localForage",
    "$q",
    "$scope",
    "$state",
    "spApi",
    "spGallery",
    "spLogger",
    "spQueue",
    sn,
  ],
};
function sn(n, o, s, e, a, t, i, r) {
  (this.$onInit = c.bind(this)),
    (this.canCreate = (p, l) => p !== null && !l),
    (this.create = g.bind(this)),
    s.$watch(
      () => t.newGallery,
      (p) => {
        this.gallery = p;
      },
    );
  function c() {
    (this.gallery = null), (this.isCreating = !1);
  }
  function g(p) {
    if (!this.canCreate(this.gallery, this.isCreating)) return o.reject();
    const l = p.shootDate;
    return (
      (this.isCreating = !0),
      i.append(`Creating gallery "${p.name}"`),
      t
        .create({
          brand_id: p.brand.id,
          event_name: p.name,
          brand_event_default_id: p.galleryDefault.id,
          event_date: `${l.getFullYear()}-${l.getMonth() + 1}-${l.getDate()}`,
          archive: p.archive,
        })
        .then(
          (u) => (
            (r.staging.galleryOptions.gallery = u),
            (this.isCreating = !1),
            e.go("upload.options")
          ),
        )
    );
  }
}
const rn = {
    greetingText: "Hello, {{ firstName }}!",
    remainingCount: "You can upload {{ remainingCount | number }} more photos",
    storageUsed: "{{ storageUsed | filesize:2 }} space used",
    settingsText: "Settings",
  },
  an = {
    helpText: "Drag Photos Here to Upload",
    separator: "or",
    browseFolderButton: "Upload Folder",
    browseFileButton: "Upload Files",
    errors: {
      tooNested: {
        title: "Too nested: ",
        description:
          "folder structures more than four levels deep are not supported.",
        link: "Learn more",
      },
      mixedType: {
        title: "Invalid folder structure: ",
        description:
          "folders can contain either photos or other folders, but not both.",
        link: "Learn more",
      },
    },
    footer: { progress: "View progress of current uploads" },
  },
  ln = {
    header: {
      title: "Upload Options",
      startUploadButton: "Start Upload",
      cancelUploadButton: "Cancel",
    },
    form: {
      brandLabel: "Brand",
      galleryAtPhotoCountLimit:
        "No more photos can be added to this gallery. 100K limit has been reached. Remove photos to continue uploading.",
      galleryLabel: "Gallery",
      newGallery: "Add New Gallery",
      recentGalleries: "Recently Updated Galleries",
      searching: "Searching...",
      searchPlaceholder: "Search All Galleries",
      searchResults:
        'Found {{ results }} result{{ results !== 1 ? "s" : "" }} for search "{{ term }}"',
      shootDateLabel: "Shoot Date",
      skipDuplicatesLabel: "Skip files that have already been uploaded",
      watermarkLabel: "Watermark",
    },
    headingTitle: "Upload Options",
    headingSubtitle: '{{ count }} Photo{{ count !== 1 ? "s" : "" }}',
    addAndNew: "Start Upload and Create New Job",
  },
  un = {
    headerTitle: "File Check Errors",
    title: "File Errors",
    totalLabel: "{{ total }} Total",
    unsupported: "Unsupported file type",
    unsupportedImagesLabel: "{{ unsupported }} Images",
    filesize: "File size exceeds 50MB",
    filesizeImagesLabel: "{{ filesize }} Images",
    cancelButton: "Cancel Upload",
    recheckButton: "Recheck Files",
    ignoreButton: "Ignore and Upload",
    andMore: "Loading photos {{from}}-{{to}}...",
  },
  cn = {
    headingTitle: "Add New Gallery",
    form: {
      brandLabel: "Brand",
      nameLabel: "Gallery Name",
      shootDateLabel: "Shoot Date",
      galleryDefaultLabel: "Gallery Default",
      archiveLabel: "Upload as Archived Gallery?",
      archiveHelpText:
        "Immediately Archive this gallery upon upload. Archived galleries are not visible to clients and do not count towards your photo plan.",
    },
    advanced: "Advanced Options",
    hideAdvanced: "Hide Advanced Options",
    header: {
      title: "Add New Gallery",
      createGalleryButton: "Create Gallery",
      cancelButton: "Cancel",
    },
  },
  pn = ["$translateProvider", dn];
function dn(n) {
  n.useSanitizeValueStrategy("escape")
    .translations("en", {
      upload: { header: rn, new: an, options: ln, errors: un, gallery: cn },
    })
    .preferredLanguage("en");
}
const hn = ["$stateProvider", gn];
function gn(n) {
  n.state("upload", {
    abstract: !0,
    url: "/upload",
    template: `
                <div ui-view="header">
                    <sp-upload-header class="sp-app__header"></sp-upload-header>
                </div>
                <div class="sp-app__body" ui-view="body"></div>
                <div class="sp-app__footer" ui-view="footer"></div>`,
  })
    .state("upload.new", {
      url: "/new",
      views: {
        body: {
          template:
            '<sp-upload-new class="sp-upload-new__container" sp-dropzone></sp-upload-new>',
        },
        footer: {
          template:
            '<sp-upload-new-footer class="sp-upload-new-footer__container"></sp-upload-new-footer>',
        },
      },
    })
    .state("upload.errors", {
      url: "/errors",
      views: {
        header: {
          templateUrl: "spUpload/errors/sp-upload-errors-header.nghtml",
        },
        body: {
          template:
            '<sp-upload-errors class="sp-upload-errors__container"></sp-upload-errors>',
        },
      },
    })
    .state("upload.options", {
      url: "/options",
      views: {
        header: {
          template:
            '<sp-upload-options-header class="sp-app__header"></sp-upload-options-header>',
        },
        body: {
          template:
            '<sp-upload-options class="sp-upload-options__container"></sp-upload-options>',
        },
        footer: {
          template: "<sp-upload-options-footer></sp-upload-options-footer>",
        },
      },
    })
    .state("upload.gallery", {
      url: "/gallery",
      views: {
        header: {
          template:
            '<sp-upload-gallery-header class="sp-app__header"></sp-upload-options-header>',
        },
        body: {
          template:
            '<sp-upload-gallery class="sp-upload-gallery__container"></sp-upload-gallery>',
        },
      },
    });
}
const fn = L.module("spDesktopUploader.upload", [
    "ngSanitize",
    "ui.router",
    "ui.select",
    "ui.bootstrap",
    "LocalForageModule",
    "pascalprecht.translate",
    le,
    V,
  ])
    .config(pn)
    .config(hn)
    .value("electron", re)
    .value("fs", ie)
    .value("lodash", U)
    .value("path", T)
    .component("spUploadHeader", qt)
    .component("spUploadNew", zt)
    .component("spUploadNewFooter", xt)
    .component("spUploadErrors", Jt)
    .component("spUploadOptions", Kt)
    .component("spUploadOptionsHeader", Zt)
    .component("spUploadOptionsFooter", Vt)
    .component("spUploadGallery", tn)
    .component("spUploadGalleryHeader", on).name,
  mn = {
    templateUrl: "spQueue/sp-queue-root.nghtml",
    controller: ["$scope", "$stateParams", "spJobStatus", "spQueue", bn],
  };
function bn(n, o, s, e) {
  (this.$onInit = a.bind(this)),
    (this.selectJob = t.bind(this)),
    n.$watch(
      () => e.jobs,
      (i) => {
        this.jobs = i;
      },
    );
  function a() {
    (this.jobs = e.jobs),
      (this.selectedJob =
        U.find(e.jobs, { id: o.job }) ||
        U.find(e.jobs, { status: s.IN_PROGRESS }) ||
        this.jobs[0]);
  }
  function t(i) {
    this.selectedJob = i;
  }
}
const yn = {
  templateUrl: "spQueue/header/sp-queue-header.nghtml",
  controller: ["$uibModal", "spApi", vn],
};
function vn(n, o) {
  (this.$onInit = s.bind(this)), (this.openSettings = e);
  function s() {
    return o.getStudioInfo().then((a) => {
      (this.studioInfo = a),
        a.plan.type === "photo_count" &&
          (this.remainingCount = a.plan.allowed - a.plan.used);
    });
  }
  function e() {
    return n.open({ component: "spSettings" });
  }
}
const Cn = {
  bindings: { jobs: "<", jobClick: "&?", selectedJob: "<" },
  templateUrl: "spQueue/jobs/sp-queue-jobs.nghtml",
  controller: ["$q", "$state", "$translate", "spJobStatus", wn],
};
function wn(n, o, s, e) {
  (this.$onInit = a.bind(this)),
    (this.jobsComplete = t(e.COMPLETED)),
    (this.jobsInProgress = t(e.IN_PROGRESS)),
    (this.jobsInQueue = t(e.PENDING)),
    (this.jobsCanceled = t(e.CANCELED)),
    (this.goToNewUpload = () => o.go("upload.new")),
    (this.selectJob = i.bind(this)),
    (this.jobErrorCount = c),
    (this.completedSubtitle = r),
    (this.getCoverPhoto = g);
  function a() {
    return n
      .all({
        separatorComplete: s("queue.jobs.separator.complete"),
        separatorInProgress: s("queue.jobs.separator.inProgress"),
        separatorInQueue: s("queue.jobs.separator.inQueue"),
        separatorCanceled: s("queue.jobs.separator.canceled"),
        separatorNewUpload: s("queue.jobs.separator.newUpload"),
      })
      .then((p) => {
        this.translated = p;
      });
  }
  function t(p) {
    return (l) => l.filter((u) => u.status === p);
  }
  function i(p) {
    this.jobClick && this.jobClick({ job: p });
  }
  function r(p) {
    return "queue.jobs.subtitles." + (!!c(p) ? "completeErrors" : "complete");
  }
  function c(p) {
    return (p.photos && p.photos.filter((l) => !!l.error).length) || 0;
  }
  function g(p) {
    return (
      (p.gallery.cover_photo && p.gallery.cover_photo.large) ||
      (p.photos && p.photos[0] && Ue(p.photos[0].path)) ||
      ""
    );
  }
}
const In = {
  bindings: { job: "<", jobSelect: "&" },
  templateUrl: "spQueue/job-detail/sp-queue-job-detail.nghtml",
  controller: [
    "$uibModal",
    "$scope",
    "$state",
    "electron",
    "spConfig",
    "spJobStatus",
    "spQueue",
    "spPhotoStatus",
    Un,
  ],
};
function Un(n, o, s, e, a, t, i, r) {
  (this.getLabelFor = p.bind(this)),
    (this.photosError = (h) => h.photos.filter(l)),
    (this.photosDuplicate = (h) => h.photos.filter(u)),
    (this.photosComplete = (h) => h.photos.filter(m)),
    (this.photosUploading = (h) => h.photos.filter(v(h))),
    (this.photosInQueue = (h) => h.photos.filter(E(h))),
    (this.photosCanceled = (h) => h.photos.filter(b)),
    (this.jobProgressCount = (h) => ({
      finished: _([
        this.photosError(h),
        this.photosDuplicate(h),
        this.photosComplete(h),
      ]),
      total: h.photos.length,
    })),
    (this.pause = M),
    (this.clear = W),
    (this.resume = i.resume),
    (this.resubmit = C.bind(this)),
    (this.$onInit = c.bind(this)),
    (this.showPause = (h) => h.status === t.IN_PROGRESS),
    (this.showClear = (h) => h.status !== t.IN_PROGRESS),
    (this.showResubmit = (h) => h.status === t.CANCELED),
    (this.showManagePhotos = (h) =>
      h.status === t.COMPLETED || h.status === t.CANCELED),
    (this.showItemInFolder = e.shell.showItemInFolder),
    o.$on("spApi:uploadCompleted", (h, k) => {
      k.photo, g.call(this, this.job);
    }),
    o.$watch(
      () => this.job.status,
      () => {
        g.call(this, this.job);
      },
    ),
    o.$watch(
      () => this.job.id,
      () => {
        g.call(this, this.job),
          (this.galleryUrl = a.gallery.getUrl(
            this.job.gallery.brand_id,
            this.job.gallery.id,
          ));
      },
    );
  function c() {
    (this.galleyUrl = ""), g.call(this, this.job);
  }
  function g(h) {
    (this.duplicates = this.photosDuplicate(h)),
      (this.errors = this.photosError(h)),
      (this.completed = this.photosComplete(h)),
      (this.uploading = this.photosUploading(h)),
      (this.queued = this.photosInQueue(h)),
      (this.canceled = this.photosCanceled(h));
  }
  function p(h) {
    return h.status === t.COMPLETED
      ? "queue.jobDetail.label.complete"
      : h.status === t.IN_PROGRESS
        ? "queue.jobDetail.label.inProgress"
        : h.status === t.PENDING
          ? "queue.jobDetail.label.inQueue"
          : h.status === t.CANCELED
            ? "queue.jobDetail.label.canceled"
            : "";
  }
  function l(h) {
    return h.status === r.COMPLETED && h.error;
  }
  function u(h) {
    return h.duplicate;
  }
  function b(h) {
    return h.status === r.CANCELED;
  }
  function m(h) {
    return h.status === r.COMPLETED && !(l(h) || u(h));
  }
  function v(h) {
    return function (k) {
      return (
        h.status !== t.PENDING &&
        (k.status === r.IN_PROGRESS || k.status === r.PENDING)
      );
    };
  }
  function E(h) {
    return function (k) {
      return (
        h.status === t.PENDING &&
        k.status !== r.COMPLETED &&
        k.status !== r.CANCELED
      );
    };
  }
  function _(h) {
    return h.reduce((k, O) => (k += O.length), 0);
  }
  function M(h) {
    return (
      i.pause(h),
      n.open({
        template: `
                <sp-queue-pause
                    jobs="$ctrl.jobs"
                    job="$ctrl.job"
                    close="$ctrl.close()"
                    dismiss="$ctrl.dismiss()">
                </sp-queue-pause>`,
        controller: [
          "$uibModalInstance",
          "spQueue",
          function (O, J) {
            (this.jobs = J.jobs),
              (this.job = h),
              (this.close = O.close),
              (this.dismiss = O.dismiss);
          },
        ],
        controllerAs: "$ctrl",
      })
    );
  }
  function W(h) {
    const k = U.findIndex(i.jobs, { id: h.id });
    if (
      ((i.jobs = i.jobs.filter((O) => O.id !== h.id)),
      i.persist(i.jobs),
      U.isEmpty(i.jobs))
    )
      return s.go("upload.new");
    this.jobSelect({
      job: i.jobs.length > k ? i.jobs[k] : i.jobs[i.jobs.length - 1],
    });
  }
  function C(h) {
    return (
      (i.jobs = i.jobs
        .filter((O) => h.id !== O.id)
        .concat(
          Object.assign({}, h, k("status", t.PENDING)(h), {
            photos: h.photos
              .map(k("status", r.PENDING))
              .map(k("transferred", 0)),
          }),
        )),
      (this.job = i.jobs[i.jobs.length - 1]),
      i.resume()
    );
    function k(O, J) {
      return (S) => Object.assign({}, S, { [O]: J });
    }
  }
}
const En = {
  bindings: {
    groupTitle: "@",
    groupSubtitle: "@",
    listItemClass: "@",
    listItemGlyph: "<?",
    listItemIcon: "<?",
    photos: "<",
  },
  require: { accordion: "^spAccordion" },
  templateUrl: "spQueue/job-detail/sp-queue-job-detail-group.nghtml",
  controller: ["$element", "$scope", "$timeout", "electron", An],
};
function An(n, o, s, e) {
  (this.$onInit = a.bind(this)),
    (this.$onDestroy = t.bind(this)),
    (this.open = i.bind(this)),
    (this.close = r.bind(this)),
    (this.increaseRepeatLimit = c.bind(this)),
    (this.nextChunk = g.bind(this)),
    (this.showItemInFolder = e.shell.showItemInFolder),
    o.$watch(
      () => this.isOpen,
      (p) => {
        p
          ? n.addClass("sp-accordion-group--open")
          : n.removeClass("sp-accordion-group--open");
      },
    );
  function a() {
    (this.isOpen = !1),
      this.accordion.addGroup(this),
      (this.groupLimit = 100),
      n.addClass("sp-accordion-group");
  }
  function t() {
    this.accordion.removeGroup(this);
  }
  function i() {
    (this.isOpen = !0), this.accordion.closeOthers(this);
  }
  function r() {
    this.isOpen = !1;
  }
  function c(p, l) {
    p - this.groupLimit > 0 && s(() => (this.groupLimit += l), 1e3);
  }
  function g(p, l) {
    return { from: p + 1, to: p + l };
  }
}
const _n = {
  bindings: {
    jobs: "<",
    job: "<",
    close: "&",
    dismiss: "&",
    isGalleryAtPhotoCountLimit: "@?",
  },
  templateUrl: "spQueue/pause/sp-queue-pause.nghtml",
  controller: ["$uibModal", "spJobStatus", "spPhotoStatus", "spQueue", $n],
};
function $n(n, o, s, e) {
  (this.remainingPhotos = (r) =>
    U.reject(r.photos, { status: s.COMPLETED }).length),
    (this.confirmCancelAll = t.bind(this)),
    (this.cancel = (r) => a.call(this, [r])),
    (this.resume = () => a.call(this, [])),
    (this.activeJobsCount = (r) => r.filter(i).length);
  function a(r) {
    L.forEach(r, (c) => e.cancel(c)), e.resume(), this.close();
  }
  function t(r) {
    return n
      .open({ component: "spQueueConfirm" })
      .result.then(() => a.call(this, r.filter(i)))
      .catch(() => {});
  }
  function i(r) {
    return r.status === o.PENDING || r.status === o.IN_PROGRESS;
  }
}
const kn = {
    bindings: { close: "&", dismiss: "&" },
    templateUrl: "./spQueue/confirm/sp-queue-confirm.nghtml",
  },
  Ln = {
    uploadProgress: "Upload Progress",
    remainingCount: "You can upload {{ remainingCount | number }} more photos",
    storageUsed: "{{ storageUsed | filesize:2 }} space used",
    settingsText: "Settings",
  },
  Pn = {
    separator: {
      complete: "Uploads Complete",
      inProgress: "Uploads In Progress",
      inQueue: "Uploads In Queue",
      canceled: "Uploads Canceled",
      newUpload: "New Upload",
    },
    subtitles: {
      complete: "Completed",
      completeErrors: "Completed – {{ errorCount }} Images Failed to Upload",
      inProgress: "{{ progress }}% Completed",
      inQueue: "In Queue",
      canceled: "Canceled",
      newUpload: "Add New Upload",
    },
    newUploadTitle: "New Upload",
  },
  On = {
    heading: {
      error: "Upload Errors",
      duplicate: "Skipped Duplicates",
      complete: "Uploads Completed",
      uploading: "Currently Uploading",
      inQueue: "In Queue",
      canceled: "Canceled",
      count: '{{ count }} IMAGE{{ count !== 1 ? "S" : "" }}',
      jobProgressCount: "{{ finished }} of {{ total }}",
    },
    label: {
      complete: "Uploads Complete",
      inProgress: "Upload In Progress",
      inQueue: "Upload In Queue",
      canceled: "Uploads Canceled",
    },
    footer: {
      pauseButton: "Pause Upload",
      clearButton: "Clear from Queue",
      resubmitButton: "Resubmit Upload",
      managePhotosButton: "Manage Photos",
    },
    status: { canceled: "Canceled" },
    andMore: "Loading photos {{from}}-{{to}}...",
  },
  Sn = {
    header: { title: "Upload Paused" },
    body: {
      title: "Upload for {{ gallery }} Paused",
      subtitle: '{{ count }} photo{{ count !== 1 ? "s" : "" }} remaining',
      cancelButton: "Cancel Upload",
      resumeButton: "Resume",
    },
    footer: { cancel: "Cancel All Uploads In Queue ({{ count }})" },
    error: {
      atGalleryPhotoCountLimit:
        "No more photos can be added to this gallery. 100K limit has been reached. Remove photos to continue uploading.",
    },
  },
  Dn = {
    header: { title: "Cancel All" },
    body: {
      title:
        "Are you sure you want to cancel all uploads remaining in the queue?",
      noButton: "No",
      yesButton: "Yes",
    },
  };
ce.$inject = ["$translateProvider"];
function ce(n) {
  n.useSanitizeValueStrategy("escape")
    .translations("en", {
      queue: { header: Ln, jobs: Pn, jobDetail: On, pause: Sn, confirm: Dn },
    })
    .preferredLanguage("en");
}
const Tn = ["$stateProvider", Nn];
function Nn(n) {
  n.state("queue", {
    url: "/queue?job",
    template: "<sp-queue-root></sp-queue-root>",
  });
}
const Fn = L.module("spDesktopUploader.queue", [
  "ngSanitize",
  "ui.router",
  "ui.select",
  "ui.bootstrap",
  "LocalForageModule",
  "pascalprecht.translate",
  le,
  V,
])
  .config(ce)
  .config(Tn)
  .value("electron", re)
  .value("fs", ie)
  .value("lodash", U)
  .value("path", T)
  .component("spQueueRoot", mn)
  .component("spQueueHeader", yn)
  .component("spQueueJobs", Cn)
  .component("spQueueJobDetail", In)
  .component("spQueueJobDetailGroup", En)
  .component("spQueuePause", _n)
  .component("spQueueConfirm", kn).name;
L.module(le).value("THROTTLE_MILLISECONDS", 1e3);
const Rn = { title: "Settings", saveButton: "Save", cancelButton: "Cancel" },
  Gn = {
    title: "Settings",
    form: {
      alerts: {
        title: "Alerts",
        label: "Would you like to allow alerts?",
        eventLabel: "Alert me about:",
        eventComplete: "Upload completion",
        eventError: "Upload errors",
        notificationSound: "Sound",
        notificationIcon: "Icon",
        notificationNotify: "Message",
        notificationOn: "On",
        notificationOff: "Off",
      },
      speed: {
        title: "Uploads",
        subtitle: "Bandwidth Speed",
        maximumRateLabel: "Maximum upload rate possible (Recommended)",
        limitRateLabel: "Limit upload rate to",
        limitRateUnit: "kbps",
        minimum: "Upload rate must be more than zero.",
      },
      authorization: {
        title: "Authorization",
        subtitle: "Authorized by: {{ name }}",
        deauthorize: "Deauthorize Account",
      },
      update: {
        title: "Updates",
        checkUpdates: "Check for Updates",
        lastChecked: "Last checked: {{ date | date:'medium' }}",
        checkingUpdates: "Checking for updates...",
        hasUpdates: "Click here to install and restart.",
        noUpdates: "You are on the latest version.",
        updateAvailable: "There is a new version available.",
        updateError:
          "An error occured while checking for updates. Please try again later!",
      },
      logs: {
        title: "Logging",
        sendLog: "Send diagnostic usage report to Support",
      },
    },
  },
  jn = ["$translateProvider", Mn];
function Mn(n) {
  n.useSanitizeValueStrategy("escape")
    .translations("en", { settings: { header: Rn, body: Gn } })
    .preferredLanguage("en");
}
const qn = {
    bindings: { close: "&", dismiss: "&" },
    templateUrl: "spSettings/sp-settings.nghtml",
  },
  Bn = {
    bindings: { close: "&", dismiss: "&" },
    templateUrl: "spSettings/header/sp-settings-header.nghtml",
    controller: ["$scope", "spConfig", zn],
  };
function zn(n, o) {
  (this.$onInit = s.bind(this)),
    (this.canSave = (a) => a.$valid && a.$dirty),
    (this.save = e.bind(this)),
    n.$watchCollection(
      () => o.newSettings,
      (a) => (this.settings = a),
    ),
    n.$watchCollection(
      () => o.settingsForm,
      (a) => (this.settingsForm = a),
    );
  function s() {
    this.settingsForm = { $valid: !1, $dirty: !1 };
  }
  function e(a) {
    if (this.canSave(this.settingsForm))
      return o.loadSettings(a), this.close(), o.saveSettings(a);
  }
}
const Hn = {
  bindings: { close: "&" },
  templateUrl: "spSettings/body/sp-settings-body.nghtml",
  controller: [
    "$localForage",
    "$scope",
    "$state",
    "spApi",
    "spAuth",
    "spConfig",
    "spLogger",
    "spQueue",
    "spUpdate",
    xn,
  ],
};
function xn(n, o, s, e, a, t, i, r, c) {
  (this.$onInit = g.bind(this)),
    (this.deauthorize = p.bind(this)),
    (this.checkForUpdates = u.bind(this)),
    (this.quitAndInstall = c.quitAndInstall),
    (this.statusTranslateKey = l),
    (this.sendLog = b),
    o.$watch(
      () => this.settingsForm,
      (m) => (t.settingsForm = m),
    ),
    o.$watch(
      () => this.settings,
      (m) => (t.newSettings = m),
    ),
    o.$watch(
      () => c.info,
      (m) => (this.updateInfo = m),
    ),
    o.$watch(
      () => c.status,
      (m) => (this.updateStatus = m),
    ),
    o.$watch(
      () => c.lastChecked,
      (m) => (this.lastChecked = m),
    ),
    o.$watch(
      () => i.queue,
      (m) => (this.queueEmpty = U.isEmpty(m)),
    );
  function g() {
    return (
      (this.settings = L.copy(t.settings)),
      (this.updateStatus = c.status),
      (this.lastChecked = c.lastChecked),
      e.getStudioInfo().then((m) => {
        const { first_name: v, last_name: E } = m.user;
        this.authorizationUser = `${v} ${E}`;
      })
    );
  }
  function p() {
    return (
      a.logout(),
      n.clear(),
      (r.jobs = []),
      t.restoreDefaultSettings(),
      this.close(),
      s.go("auth.check")
    );
  }
  function l(m) {
    return (
      {
        IDLE: "",
        CHECKING: "settings.body.form.update.checkingUpdates",
        NO_UPDATE: "settings.body.form.update.noUpdates",
        UPDATE_AVAILABLE: "settings.body.form.update.updateAvailable",
        UPDATE_DOWNLOADED: "settings.body.form.update.updateAvailable",
        UPDATE_ERROR: "settings.body.form.update.updateError",
      }[m] || ""
    );
  }
  function u() {
    c.checkForUpdates();
  }
  function b() {
    return i.persist().then(i.sendLog);
  }
}
const Wn = L.module("spDesktopUploader.settings", [
    "ngSanitize",
    "ui.router",
    "LocalForageModule",
    "pascalprecht.translate",
    V,
  ])
    .config(jn)
    .component("spSettings", qn)
    .component("spSettingsHeader", Bn)
    .component("spSettingsBody", Hn).name,
  Jn = {
    header: { title: "Plan limit reached" },
    body: {
      title: "Uh-oh. You’re out of space.",
      subtitle: "Upgrade your plan to upload more photos.",
      button: { retry: "Retry Upload(s)", plans: "Visit Plans Page" },
    },
    footer: { button: { cancel: "Cancel All Uploads" } },
    confirm: {
      header: { title: "Cancel All Uploads" },
      body: {
        title: "Are you sure you want to cancel all uploads in the queue?",
        button: { goBack: "Go Back", cancelAll: "Cancel Uploads" },
      },
    },
  },
  Yn = ["$translateProvider", Kn];
function Kn(n) {
  n.useSanitizeValueStrategy("escape")
    .translations("en", { limitReached: Jn })
    .preferredLanguage("en");
}
const Xn = {
  bindings: { close: "&" },
  templateUrl: "spLimitReached/sp-limit-reached.nghtml",
  controller: ["$uibModal", "spConfig", "spQueue", Zn],
};
function Zn(n, o, s) {
  (this.cancelAll = a.bind(this)), (this.$onInit = e.bind(this));
  function e() {
    this.planUrl = o.plan.url;
  }
  function a() {
    return n
      .open({ component: "spConfirmCancelAll" })
      .result.then(() => {
        s.jobs.forEach((t) => s.cancel(t)), this.close();
      })
      .catch(() => {});
  }
}
const Qn = {
    bindings: { close: "&", dismiss: "&", resolve: "<" },
    templateUrl: "spLimitReached/sp-confirm-cancel-all.nghtml",
  },
  Vn = L.module("spDesktopUploader.limitReached", [
    "ngSanitize",
    "ui.bootstrap",
    "pascalprecht.translate",
    V,
  ])
    .config(Yn)
    .component("spLimitReached", Xn)
    .component("spConfirmCancelAll", Qn).name,
  eo = {
    header: { title: "Offline" },
    body: {
      title: "It looks like we are not connected to the internet.",
      subtitle: "We will get you back as soon as we are connected again!",
    },
  },
  to = ["$translateProvider", no];
function no(n) {
  n.useSanitizeValueStrategy("escape")
    .translations("en", { offline: eo })
    .preferredLanguage("en");
}
const oo = {
  bindings: { close: "&" },
  templateUrl: "spOffline/sp-offline.nghtml",
  controller: ["$scope", so],
};
function so(n) {
  n.$on("isOnline", o.bind(this));
  function o(s, e) {
    e && this.close();
  }
}
const ro = L.module("spDesktopUploader.offline", [
    "ngSanitize",
    "pascalprecht.translate",
    V,
  ])
    .config(to)
    .component("spOffline", oo).name,
  io = {
    template: '<div ui-view class="sp-app__container"></div>',
    controller: [
      "$interval",
      "$q",
      "$rootScope",
      "$uibModalStack",
      "$uibModal",
      "$window",
      "online",
      "spApi",
      "spAlert",
      "spConfig",
      "spLogger",
      "spPhotoStatus",
      "spQueue",
      "spUpdate",
      "spUtils",
      ao,
    ],
  };
function ao(n, o, s, e, a, t, i, r, c, g, p, l, u, b, m) {
  let E = 3;
  const _ = [
    s.$on("spApi:uploadCompleted", k),
    s.$on("spQueue:uploadComplete", c.completed),
    s.$on("isOnline", O),
    s.$on("spApi:retryUpload", J),
  ];
  h();
  const M = n(h, 1e3);
  (this.$onInit = W.bind(this)), (this.$onDestroy = C.bind(this));
  function W() {
    p.append(`Initializing Desktop Uploader v${g.version}`),
      b.checkForUpdates(),
      L.element(t).on("dragover", S("sp-dropzone")),
      L.element(t).on("drop", S("sp-dropzone"));
    function S(N) {
      return function (j) {
        j.target.attributes.getNamedItem(N) === null && j.preventDefault();
      };
    }
  }
  function C() {
    _.forEach((S) => S()), n.cancel(M);
  }
  function h() {
    m.isOnline().then((S) => {
      s.$broadcast("isOnline", S);
    });
  }
  function k(S, N) {
    let j = N.photo;
    if (j.error === r.AT_PLAN_PHOTO_LIMIT_ERROR) {
      const z = e.getTop();
      let Y = U.find(u.jobs, { id: j.jobId });
      if (z && z.value.modalDomEl.find("sp-limit-reached").length) return;
      u.pause(),
        c.hasError(Y),
        a.open({ component: "spLimitReached" }).result.then(u.resume);
    }
    if (j.error === r.AT_GALLERY_PHOTO_LIMIT_ERROR) {
      const z = e.getTop();
      let Y = U.find(u.jobs, { id: j.jobId });
      if (z && z.value.modalDomEl.find("sp-queue-pause").length) return;
      u.pause(Y),
        c.hasError(Y),
        a.open({
          template: `
                    <sp-queue-pause
                        jobs="$ctrl.jobs"
                        job="$ctrl.job"
                        close="$ctrl.close()"
                        dismiss="$ctrl.dismiss()"
                        is-gallery-at-photo-count-limit="true">
                    </sp-queue-pause>`,
          controller: [
            "$uibModalInstance",
            "spQueue",
            function (A, F) {
              (this.jobs = F.jobs),
                (this.job = Y),
                (this.close = A.close),
                (this.dismiss = A.dismiss);
            },
          ],
          controllerAs: "$ctrl",
        });
    }
  }
  function O(S, N) {
    N ? (E = 0) : (E += 1),
      (i.status = N),
      E === 4 &&
        (p.append("User is offline"),
        u.pause(),
        a.open({ component: "spOffline" }).result.then(() => {
          u.resume(), p.append("User is back online");
        }));
  }
  function J(S, { photo: N }) {
    (N.status = l.PENDING), (N.transferred = 0), u.isPaused || u.resume();
  }
}
L.module("spDesktopUploader", [
  "ui.router",
  "LocalForageModule",
  "pascalprecht.translate",
  "ui.bootstrap",
  V,
  Mt,
  fn,
  Fn,
  Wn,
  Vn,
  ro,
])
  .config([
    "$compileProvider",
    (n) => {
      n.preAssignBindingsEnabled(!0);
    },
  ])
  .run(Ee)
  .run(_e)
  .run(ke)
  .run(Pe)
.component("spApp", io)
// —— nativeTheme hook (runs after module is defined) ————
// PASTE THIS CORRECT BLOCK BEFORE .name;
.run(["$rootScope", function ($rootScope) {
  console.log("Attempting to set dark mode theme directly in run block...");
  try {
    // Since nodeIntegration:true, require should work here
    const { nativeTheme } = require('electron');

    if (nativeTheme) {
       $rootScope.dark = nativeTheme.shouldUseDarkColors;
       console.log(`Dark mode initially set to: ${$rootScope.dark}`);
       // Listening for OS changes is commented out for simplicity for now
       // nativeTheme.on('updated', () => { $rootScope.$applyAsync(() => { $rootScope.dark = nativeTheme.shouldUseDarkColors; }); });
    } else {
      console.error("nativeTheme module not available via require('electron').");
      $rootScope.dark = false; // Default to light
    }
  } catch (error) {
    console.error("Error getting nativeTheme in run block:", error);
    $rootScope.dark = false; // Default to light on error
  }
}])
// This should be the last thing before .name;
.name;
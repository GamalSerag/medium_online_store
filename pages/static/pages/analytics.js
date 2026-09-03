(() => {
  const cookieName = "alserag_analytics_token";

  const getCookie = (name) => {
    return document.cookie
      .split(";")
      .map((item) => item.trim())
      .find((item) => item.startsWith(`${name}=`))
      ?.slice(name.length + 1) || "";
  };

  const token = getCookie(cookieName);
  if (!token || navigator.webdriver || document.visibilityState === "prerender") return;

  const payload = {
    token,
    path: window.location.pathname,
    full_path: `${window.location.pathname}${window.location.search}`,
    title: document.title,
    referrer: document.referrer,
    language: navigator.language || "",
    screen: `${window.screen.width}x${window.screen.height}`,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "",
  };

  const body = JSON.stringify(payload);
  const track = () => {
    if (navigator.sendBeacon) {
      navigator.sendBeacon("/analytics/track/", new Blob([body], { type: "application/json" }));
      return;
    }

    fetch("/analytics/track/", {
      method: "POST",
      body,
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      keepalive: true,
    }).catch(() => {});
  };

  window.setTimeout(track, 1200);
})();

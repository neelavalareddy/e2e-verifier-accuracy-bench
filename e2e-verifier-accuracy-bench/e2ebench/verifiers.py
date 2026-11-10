"""Two deterministic reference verifiers. No LLM, no network, no e2e code."""
from datetime import datetime, timedelta


def _res(check_id, ok, element, evidence):
    return {"check_id": check_id, "result": "pass" if ok else "fail",
            "cites": {"element": element, "check": check_id},
            "evidence": evidence}


# ---- surface checks -------------------------------------------------------
def check_loads(app, cite_element=True):
    return _res("loads", app["loads"], "document" if cite_element else None,
                "app loaded" if app["loads"] else "app failed to load")


def check_console(app):
    errs = [c["msg"] for c in app["console"] if c["level"] == "error"]
    return _res("no_console_error", not errs, "console",
                "no console errors" if not errs else "console error: " + errs[0])


def check_main_button(app, kinds=("button", "link")):
    prim = [e for e in app["elements"] if e["primary"] and e["kind"] in kinds]
    if prim:
        return _res("main_button_present", True, prim[0]["id"],
                    "primary element %s (%s) present" % (prim[0]["id"], prim[0]["kind"]))
    return _res("main_button_present", False, "document",
                "no primary element of kind %s" % "/".join(kinds))


# ---- careful feature checks ----------------------------------------------
def check_handler(app, c):
    return _res(c["id"], c["wired"], c["element"],
                "handler wired" if c["wired"] else "no handler bound to " + c["element"])


def recompute_total(items, discount_pct):
    sub = sum(p * q for p, q in items)
    return sub - sub * discount_pct // 100


def check_cart_total(app, c):
    exp = recompute_total(c["items"], c["discount_pct"])
    ok = exp == c["displayed_cents"]
    return _res(c["id"], ok, c["element"],
                "recomputed %d vs displayed %d" % (exp, c["displayed_cents"]))


def simulate_visit(c):
    """Flow trace: anonymous GET of a protected path -> final location."""
    return c["anonymous_result"]


def check_auth(app, c):
    final = simulate_visit(c)
    ok = final == "/login"
    return _res(c["id"], ok, c["element"],
                "anonymous visit to %s ended at %s" % (c["path"], final))


def check_pagination(app, c):
    n, size, pages = c["total_items"], c["page_size"], c["rendered_pages"]
    shown = sum(min(size, max(0, n - p * size)) for p in range(pages))
    exp_pages = -(-n // size)
    ok = shown == n and pages == exp_pages
    return _res(c["id"], ok, c["element"],
                "pages rendered %d expected %d; items shown %d of %d"
                % (pages, exp_pages, shown, n))


def simulate_save(c):
    """Trace: type edit, click save. Returns (stored, shown)."""
    stored = c["edit"]
    shown = c["edit"] if c["refreshes_after_save"] else c["before"]
    return stored, shown


def check_save_refresh(app, c):
    stored, shown = simulate_save(c)
    return _res(c["id"], stored == shown, c["element"],
                "after save stored=%r shown=%r" % (stored, shown))


def check_mobile_nav(app, c):
    ok = c["visible_desktop"] and c["visible_mobile"]
    return _res(c["id"], ok, c["element"],
                "visible@1280=%s visible@375=%s" % (c["visible_desktop"], c["visible_mobile"]))


def simulate_double_click(c):
    """Two clicks 80ms apart; returns number of charges created."""
    return 1 if c["debounced"] else 2


def check_double_click(app, c):
    n = simulate_double_click(c)
    return _res(c["id"], n == 1, c["element"], "2 rapid clicks -> %d charge(s)" % n)


def _local_date(utc, offset):
    return (datetime.fromisoformat(utc) + timedelta(hours=offset)).date().isoformat()


def check_tz(app, c):
    exp = _local_date(c["utc"], c["user_offset_hours"])
    got = _local_date(c["utc"], c["applied_offset_hours"])
    return _res(c["id"], exp == got, c["element"],
                "expected local date %s, displayed %s" % (exp, got))


CHECKERS = {
    "handler_wired": check_handler,
    "cart_total": check_cart_total,
    "auth_guard": check_auth,
    "pagination": check_pagination,
    "save_refresh": check_save_refresh,
    "mobile_nav": check_mobile_nav,
    "double_click": check_double_click,
    "tz_display": check_tz,
}


def _verdict(app, name, checks):
    bad = any(c["result"] == "fail" for c in checks)
    return {"app_id": app["id"], "verifier": name,
            "verdict": "fail" if bad else "pass", "checks": checks}


def verify_careful(app):
    checks = [check_loads(app), check_console(app), check_main_button(app)]
    checks += [CHECKERS[c["kind"]](app, c) for c in app["checks"]]
    return _verdict(app, "careful", checks)


def verify_sloppy(app):
    """Surface only. Looks for a <button>-kind main element; omits element
    citation on the 'loads' verdict."""
    checks = [check_loads(app, cite_element=False), check_console(app),
              check_main_button(app, kinds=("button",))]
    return _verdict(app, "sloppy", checks)


VERIFIERS = {"careful": verify_careful, "sloppy": verify_sloppy}


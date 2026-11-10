"""SYNTHETIC dataset: 12 fictional web-app specs (8 with planted defects, 4 clean).

Every product here is invented. No real e2e (e2e.com) code or data is used.
Each feature check embeds the (simulated) app behaviour as parameters, so
verifiers can run simulated click/flow traces against the spec offline.
"""

SYNTHETIC_NOTICE = (
    "SYNTHETIC DATA: all apps, defects and results are invented for "
    "benchmarking. No real e2e framework code is called or imported."
)

SURFACE_CHECKS = ("loads", "no_console_error", "main_button_present")

DEFECT_CLASSES = (
    "broken_submit_handler",
    "wrong_cart_total",
    "missing_auth_redirect",
    "off_by_one_pagination",
    "stale_data_after_save",
    "broken_mobile_nav",
    "duplicate_charge_double_click",
    "timezone_shifted_date",
)


# ---- check builders -------------------------------------------------------
def handler(el, wired=True):
    return {"id": "handler_wired:" + el, "kind": "handler_wired",
            "element": el, "wired": wired}


def total(el, items, discount_pct, displayed_cents):
    return {"id": "cart_total:" + el, "kind": "cart_total", "element": el,
            "items": items, "discount_pct": discount_pct,
            "displayed_cents": displayed_cents}


def auth(path, anon_result):
    return {"id": "auth_guard:" + path, "kind": "auth_guard",
            "element": "page:" + path, "path": path,
            "anonymous_result": anon_result}


def pagination(el, total_items, page_size, rendered_pages):
    return {"id": "pagination:" + el, "kind": "pagination", "element": el,
            "total_items": total_items, "page_size": page_size,
            "rendered_pages": rendered_pages}


def save_refresh(el, before, edit, refreshes):
    return {"id": "save_refresh:" + el, "kind": "save_refresh", "element": el,
            "before": before, "edit": edit, "refreshes_after_save": refreshes}


def mobile_nav(el, visible_mobile):
    return {"id": "mobile_nav:" + el, "kind": "mobile_nav", "element": el,
            "visible_desktop": True, "visible_mobile": visible_mobile}


def double_click(el, debounced):
    return {"id": "double_click:" + el, "kind": "double_click", "element": el,
            "debounced": debounced}


def tz(el, utc, user_offset, applied_offset):
    return {"id": "tz_display:" + el, "kind": "tz_display", "element": el,
            "utc": utc, "user_offset_hours": user_offset,
            "applied_offset_hours": applied_offset}


def _app(app_id, name, pages, elements, checks, defects=(), console=()):
    return {
        "id": app_id, "name": name, "synthetic": True,
        "pages": list(pages),
        "elements": [{"id": i, "kind": k, "primary": p} for i, k, p in elements],
        "loads": True,
        "console": [{"level": l, "msg": m} for l, m in console],
        "checks": list(checks),
        "defects": [dict(d) for d in defects],
    }


def _defect(cls, checks, desc):
    return {"class": cls, "checks": list(checks), "description": desc}


def build_apps():
    """Return the 12 synthetic apps in fixed order."""
    return [
        _app("taskly", "Taskly (todo)", ["/", "/tasks"],
             [("add_task", "button", True), ("task_list", "list", False)],
             [handler("add_task"), pagination("task_list", 25, 10, 3)],
             console=[("warn", "deprecated API used")]),
        _app("cartly", "Cartly (cart/checkout)", ["/cart", "/checkout"],
             [("checkout_btn", "button", True), ("cart_table", "table", False)],
             [total("cart_table", [[1999, 2], [500, 1]], 10, 2250),
              handler("checkout_btn")],
             [_defect("wrong_cart_total", ["cart_total:cart_table"],
                      "total ignores quantities")]),
        _app("bookit", "Bookit (booking form)", ["/book"],
             [("submit_booking", "button", True), ("date_field", "input", False)],
             [handler("submit_booking", wired=False)],
             [_defect("broken_submit_handler",
                      ["handler_wired:submit_booking", "no_console_error"],
                      "submit handler undefined, throws on click")],
             console=[("error", "TypeError: onSubmit is not a function")]),
        _app("insightboard", "Insightboard (analytics)", ["/events"],
             [("export_btn", "button", True), ("events_table", "table", False)],
             [pagination("events_table", 41, 10, 4), handler("export_btn")],
             [_defect("off_by_one_pagination", ["pagination:events_table"],
                      "last page dropped: 4 pages shown for 41 items")]),
        _app("loginly", "Loginly (auth flow)", ["/login", "/dashboard"],
             [("login_btn", "button", True)],
             [auth("/dashboard", "/dashboard"), handler("login_btn")],
             [_defect("missing_auth_redirect", ["auth_guard:/dashboard"],
                      "anonymous user not redirected to /login")]),
        _app("prefsy", "Prefsy (settings page)", ["/settings"],
             [("save_btn", "button", True), ("display_name", "input", False)],
             [save_refresh("display_name", "Ada", "Ada L.", False),
              handler("save_btn")],
             [_defect("stale_data_after_save", ["save_refresh:display_name"],
                      "old value displayed after save")]),
        _app("shopnav", "Shopnav (storefront)", ["/"],
             [("browse_btn", "button", True), ("nav_toggle", "button", False)],
             [mobile_nav("nav_toggle", False)],
             [_defect("broken_mobile_nav", ["mobile_nav:nav_toggle"],
                      "nav toggle hidden at 375px width")]),
        _app("paydesk", "Paydesk (payments)", ["/pay"],
             [("pay_btn", "button", True), ("order_summary", "table", False)],
             [double_click("pay_btn", False),
              total("order_summary", [[1200, 1]], 0, 1200)],
             [_defect("duplicate_charge_double_click", ["double_click:pay_btn"],
                      "two rapid clicks create two charges")]),
        _app("slotly", "Slotly (scheduler)", ["/slots"],
             [("book_slot", "button", True), ("event_time", "text", False)],
             [tz("event_time", "2026-03-01T02:30:00", -5, 5),
              handler("book_slot")],
             [_defect("timezone_shifted_date", ["tz_display:event_time"],
                      "offset sign flipped: date shown a day late")]),
        _app("notely", "Notely (notes) [clean]", ["/notes"],
             [("save_note", "button", True), ("note_body", "input", False),
              ("note_updated", "text", False)],
             [save_refresh("note_body", "Draft", "Final", True),
              tz("note_updated", "2026-06-15T23:45:00", -7, -7),
              handler("save_note")]),
        _app("invoicer", "Invoicer (invoices) [clean]", ["/invoices"],
             [("send_btn", "button", True), ("invoice_table", "table", False)],
             [total("invoice_table", [[2500, 3], [999, 2], [150, 10]], 20, 8799),
              double_click("send_btn", True)]),
        _app("launchpad", "Launchpad (landing) [clean]", ["/", "/app"],
             [("cta_link", "link", True), ("nav_toggle", "button", False)],
             [auth("/app", "/login"), mobile_nav("nav_toggle", True)]),
    ]


def known_elements(app):
    ids = {e["id"] for e in app["elements"]}
    ids |= {"page:" + p for p in app["pages"]}
    ids |= {"document", "console"}
    return ids


def check_ids(app):
    return list(SURFACE_CHECKS) + [c["id"] for c in app["checks"]]


def ground_truth(app):
    """Expected per-check pass/fail plus defect list for one app."""
    failing = set()
    for d in app["defects"]:
        failing |= set(d["checks"])
    return {
        "app_id": app["id"],
        "app_expected": "fail" if app["defects"] else "pass",
        "checks": {c: ("fail" if c in failing else "pass") for c in check_ids(app)},
        "defects": app["defects"],
    }


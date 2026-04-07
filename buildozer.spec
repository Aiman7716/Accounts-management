[app]
title = Accounting System
package.name = accountapp
package.domain = org.aiman
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,css
version = 0.1
requirements = python3,kivy,kivymd,flask,sqlite3,jinja2,werkzeug,itsdangerous,click
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1


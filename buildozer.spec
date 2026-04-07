[app]
title = Accounting App
package.name = accountingapp
package.domain = org.ayman
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
version = 0.1
requirements = python3,kivy==2.2.1,sqlite3
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 23b
android.private_storage = True
log_level = 2

[buildozer]
build_dir = ./.buildozer
bin_dir = ./bin

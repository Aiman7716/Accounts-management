[app]
title = Accounting App
package.name = accountingapp
package.domain = org.ayman
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
version = 0.1
# التعديل هنا: أضفنا hostpython3 لضمان استقرار البناء
requirements = python3,kivy==2.2.1,hostpython3,sqlite3
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.private_storage = True
log_level = 2

[buildozer]
build_dir = ./.buildozer
bin_dir = ./bin

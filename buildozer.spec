[app]
title = Accounting App
package.name = accountingapp
package.domain = org.ayman
source.dir = .
# الإصدار مهم جداً لبدء العملية
version = 0.1
source.include_exts = py,png,jpg,kv,atlas,db

# التعديل الجوهري هنا: أضفنا المكتبات الأساسية لضمان عدم توقف البناء
requirements = python3,kivy==2.2.1,pillow,sqlite3

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
# الإصدار المستقر والمتوافق مع GitHub حالياً
android.ndk = 25b
android.private_storage = True
log_level = 2

[buildozer]
build_dir = ./.buildozer
bin_dir = ./bin

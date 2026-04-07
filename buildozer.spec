[app]
# (str) Title of your application
title = My Accounting App

# (str) Package name
package.name = accountingapp

# (str) Package domain (needed for android packaging)
package.domain = org.ayman

# (str) Source code where the main.py is located
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db

# (list) Application requirements
# أضفنا flask و sqlite3 لضمان عمل قاعدة البيانات
requirements = python3,kivy,flask,sqlite3

# (str) Custom source folders for requirements
# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
# هذا الرقم هو السر في تجاوز خطأ الـ 5 دقائق السابق
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded)
android.ndk_path = 

# (str) Android SDK directory (if empty, it will be automatically downloaded)
android.sdk_path = 

# (str) ANT directory (if empty, it will be automatically downloaded)
android.ant_path = 

# (str) Android entry point, default is to use start.py
android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to exclude for the search
# (list) List of inclusions using pattern matching
# (list) List of exclusions using pattern matching

# (str) Full name including language for your app (optional)
# (str) Short name for your app (optional)

# (str) Log level (0 = error only, 1 = info, 2 = debug (with buildozer output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1

[buildozer]
# (str) Path to build artifacts (default is ./.buildozer)
build_dir = ./.buildozer

# (str) Path to bin directory (default is ./bin)
bin_dir = ./bin

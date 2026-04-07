[app]
# (str) Title of your application
title = Accounting App

# (str) Package name
package.name = accountingapp

# (str) Package domain
package.domain = org.ayman

# (str) Source code where the main.py is located
source.dir = .

# (str) Application version (هذا السطر الذي كان ينقصنا)
version = 0.1

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,db

# (list) Application requirements
requirements = python3,kivy,flask,sqlite3

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Use --private data storage
android.private_storage = True

# (str) Log level
log_level = 2

[buildozer]
# (str) Path to build artifacts
build_dir = ./.buildozer

# (str) Path to bin directory
bin_dir = ./bin

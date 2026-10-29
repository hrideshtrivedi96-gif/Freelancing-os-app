[app]
title = Freelancing OS
package.name = freelancingos
package.domain = org.freelancing

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,txt
source.exclude_dirs = tests, bin, .buildozer, .git, .github, venv, __pycache__

version = 0.1

requirements = python3,kivy==2.3.0,pillow,requests,certifi,urllib3,idna,charset-normalizer

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1

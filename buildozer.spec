[app]
title = Freelancing OS
package.name = freelancingos
package.domain = com.freelancing.os
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
version = 1.0
requirements = python3,kivy,pyTelegramBotAPI,requests,openai
orientation = portrait
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK,FOREGROUND_SERVICE
android.api = 33
android.minapi = 21
android.wakelock = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2

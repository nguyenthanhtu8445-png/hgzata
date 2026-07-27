[app]

# (str) Title of your application
title = Game Text Translator

# (str) Package name
package.name = gametexttranslator

# (str) Package domain (needed for android/ios packaging)
package.domain = org.kiri.translator
version = 1.0.0

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let you install dependencies)
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json

# (list) List of inclusions using pattern matching
# source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let you uninstall dependencies)
# source.exclude_exts = spec

# (list) List of directory to exclude from the tree
# source.exclude_dirs = tests, bin

# (list) List of permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Android API version to use
android.api = 34

# (int) Minimum API your application requires
android.minapi = 21

# (int) Target SDK version
android.sdk = 34

# (str) Android NDK version to use
android.ndk = 27

# (bool) Use Android NDK r27+
# android.ndk_api = 21

# (str) Android SDK directory (overrides ANDROID_HOME env var)
# android.sdk_path =

# (str) Android NDK directory (overrides ANDROID_NDK_HOME env var)
# android.ndk_path =

# (str) Android ANT directory (overrides ANDROID_ANT_HOME env var)
# android.ant_path =

# (bool) If True, then skip trying to update the Android SDK
# android.skip_update = False

# (str) The Android arch to build for (arm64-v8a, armeabi-v7a, x86, x86_64)
android.archs = arm64-v8a

# (str) Python for android branch (forks welcome)
# android.p4a_branch = master

# (str) GIT branch of python-for-android (default is 'master')
# p4a.branch = master

# (str) Local path to python-for-android source (for development)
# p4a.source_dir =

# (str) Requirements (comma separated)
requirements = python3,kivy,plyer,pyjnius

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (landscape, portrait, or both)
orientation = portrait

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY, NAME2:ENTRYPOINT2_TO_PY

# OSX specific settings

# (str) Kivy version to use
# kivy_version = 2.3.1

# (str) Full path to your application's .icns file
# icon.filename = %(source.dir)s/data/icon.icns

# (str) CFBundleIdentifier
# osx.bundle_identifier = org.kiri.translator

# (str) CFBundleURLSchemes (comma separated)
# osx.url_schemes =

# Android specific

# (list) Permissions
# android.permissions = INTERNET

# (int) Android API to use
# android.api = 31

# (int) Minimum API
# android.minapi = 21

# (int) Android SDK version to use
# android.sdk = 31

# (str) Android NDK version to use
# android.ndk = 25c

# (bool) Android - LEAN BACKUP?
# android.lean_backup = False

# (list) Android - AAR libraries to add
# android.add_aars =

# (str) Android - add a class in the java files
# android.add_src =

# (str) Android gstreamer support
# android.gstreamer =

# (list) Android - list of libraries to add
# android.add_libs =

# (str) Android - the path to a custom AndroidManifest.xml
# android.manifest =

# (str) Android - the path to a custom build.gradle
# android.gradle =

# (str) Android - the path to a custom activity
# android.activity =

# (str) Android - path to the java files that can be added to the gradle project
# android.add_src =

# (bool) Android - Use the activity itself as the default presplash
# android.presplash_as_loadingscreen = False

# (str) Android - the path to a custom themed activity
# android.themed_activity =

# (str) Android - the path to a themed activity layout
# android.themed_activity_layout =

# (str) Flask - development server host (0.0.0.0)
# flask.host = 0.0.0.0

# (str) Flask - development server port (5000)
# flask.port = 5000

# (str) Flask - development server debug mode (True/False)
# flask.debug = False

# iOS specific

# (str) iOS - path to your ios .app
# ios.appname = My App

# (str) iOS - path to your ios .app icon
# ios.icon =

# (str) iOS - path to your ios .app presplash
# ios.presplash =

# (str) iOS - path to your ios .app storyboard
# ios.storyboard =


# (str) Window icon for the X11 backend
# window_icon =

# (str) The window title for the X11 backend
# window_title =

# (s) X, Y, width, height (in pixels) for X11 window
# window_size =

# (str) X11 window type (dropdown, normal, utility, etc)
# window_type =

# (list) Arguments to pass to the app
# args =

# (bool) Indicate if the application is a presplash animation
# presplash.is_presplash = False


#
# Build configuration
#

# (str) Path to a custom build configuration file
# build_config =

# (str) Path to your application's icon
# icon.filename = icon.png

# (str) Path to your application's presplash
# presplash.filename = presplash.png

# (str) Path to your application's app store splash screen
# store_splash.filename =

# (str) Mobile - supported orientation (landscape, portrait, or both)
# orientation = portrait


#
# Windows specific
#

# (bool) Windows - Windows App enable
# windows.app = False

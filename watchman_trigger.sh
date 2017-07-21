#!/usr/bin/env sh

START_TIME=`date +"%s"`



/srv/app/watchman -j <<-EOT
["trigger", "/workspaces", {
  "name": "test_trigger",
  "expression": ["allof",
    ["match", "*.*"],
    ["since", $START_TIME, "ctime"]
  ],
  "command": ["/srv/env/bin/python", "run_watchman.py", "$DJANGO_SETTINGS_MODULE"],  
  "chdir": "`pwd`",
  "stdin": ["name", "exists"]
}]
EOT

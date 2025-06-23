Feature: Empty setup

  Scenario: Home page is alive
    When Client GET "/"
    Then web code is 200

  Scenario: Ignore Not Found
    When Client GET "/invalid-not-found"
    Then web code is 404

  Scenario: Buttons on home page
    When Client GET "/"
    Then html "button" "Wifi pass map" is visible
    And html "button" "Tools" is visible
    And html "button" "View Settings" is visible

  Scenario: wifi_pass_map page is accesible
    When Client GET "/wifi_pass_map"
    Then web code is 200

  Scenario: Tools site is accesible
    When Client GET "/tools"
    Then web code is 200

  Scenario: View settigs is accesible
    When Client GET "/view"
    Then web code is 200

#--------- TOOLS ---------

  Scenario: Tools site have global config
    When Client GET "/tools"
    Then html "button" "GLOBAL SETTINGS" is visible
    And html "button" "TABLE_V0" is visible
    And html "button" "REMOVE_DUPLICATES" is visible
    And html "button" "TABLEV0_LOCATE" is visible

  Scenario: Tools site have global config
    When Client GET "/tools"
    Then every config has label, value input, and description

  Scenario: Changing log level
    When API POST "/api/set_log_level" with data "{"log_level":"INFO"}"
    Then web code is 200
    And web response is {'message': 'Log level set to INFO', 'status': 'success'}
    And log contains "Log level changed to INFO"

  Scenario: Missing parameters for run_tool
    When API POST "/api/tools" with data "{}"
    Then web code is 404
    And web response contains "Empty plugin name or tool name"

  Scenario: Script not found for run_tool
    When API POST "/api/tools" with data "{"object_name": "notfound", "tool_name": "any"}"
    Then web code is 404
    And web response contains "The plugin notfound was not found"

  """

  Scenario: Tool not found in script
    Given tool "dummytool" exists with run_fun
    When API POST "/api/tools" with data "{"object_name": "dummytool", "tool_name": "notfound"}"
    Then web code is 404
    And web response contains "Tool not found"

  Scenario: Tool run_fun missing
    Given tool "wigle" exists with "wigle_locate"
    When API POST "/api/tools" with data "{"object_name": "dummytool", "tool_name":"tool1"}"
    Then web code is 404
    And web response contains "The tool tool1 was not found in plugin dummytool"
  """

# --------- API -------------------

  Scenario: API returns empty wifi_pass_map data
    Given delete all plugins
    When Client GET "/api/wifi_pass_map"
    Then web code is 200
    And web response is {'data': [], 'script_statuses': [], 'AP_len': 0}

  Scenario: API returns empty search data
    Given delete all plugins
    When Client GET "/api/search"
    Then web code is 200
    And web response is {"data": [], "script_statuses": [], "AP_len": 0}

# --------------- BACKUP -----------------

  Scenario:  backup save
    When tool run "globalconfig" "Create backup"
    Then root "backup" "folder" exists
    And in root "backup" is "folder" "config"
    And in root "backup/config" is "file" "globalconfig.ini"
    And in root "backup" is "folder" "plugins"
    And in root "backup/plugins" is "file" "wigle.disable.py"
    And in root "backup" is "folder" "data"
    And in root "backup/data" is "file" "wifi_pass_map.db"

  Scenario:  backup load
    #TODO

#------------- SAVE/UPDATE CONFIG ---------

  #TODO Scenario: Default base configs are valid
  #TODO Scenario: Invalid input
  #TODO Scenario: Valid input
  #TODO Scenario:
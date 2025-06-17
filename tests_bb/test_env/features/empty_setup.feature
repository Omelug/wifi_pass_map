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

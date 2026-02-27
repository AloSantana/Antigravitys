# Diagnostic Report

**Timestamp:** 2026-02-12T18:44:49.384065
**Duration:** 1.04s

## Summary

- **Total Issues:** 189
- **Critical:** 1
- **High:** 27
- **Medium:** 87
- **Low:** 6
- **Info:** 68
- **Fixed:** 0

## Issues

### CRITICAL

**quick-fix.sh:76**
- Dangerous command found: rm -rf /
- *Suggestion:* Review this command carefully before execution

### HIGH

**tests\conftest.py:210**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\test_auto_issue_finder.py:110**
- Potential hardcoded password
- *Suggestion:* Use environment variables or secure secret management

**tests\test_config.py:376**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\test_config.py:377**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\test_config.py:387**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\test_config.py:432**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\test_settings_api.py:271**
- Potential hardcoded token
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_agent.py:98**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_config.py:32**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_config.py:138**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:21**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:23**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:58**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:85**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:102**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:119**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:136**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:157**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:182**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:197**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:210**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:232**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:250**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:272**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:285**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:310**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

**tests\unit\test_gemini_client.py:331**
- Potential hardcoded API key
- *Suggestion:* Use environment variables or secure secret management

### MEDIUM

**.agent\scripts\auto_preview.py:58**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\scripts\auto_preview.py:120**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\database-design\scripts\schema_validator.py:25**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\frontend-design\scripts\accessibility_checker.py:26**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\frontend-design\scripts\ux_audit.py:109**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\frontend-design\scripts\ux_audit.py:308**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\i18n-localization\scripts\i18n_checker.py:182**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\i18n-localization\scripts\i18n_checker.py:88**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\lint-and-validate\scripts\lint_runner.py:25**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\lint-and-validate\scripts\lint_runner.py:55**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\mobile-design\scripts\mobile_audit.py:85**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\mobile-design\scripts\mobile_audit.py:450**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\mobile-design\scripts\mobile_audit.py:413**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\seo-fundamentals\scripts\seo_checker.py:29**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\testing-patterns\scripts\test_runner.py:23**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**.agent\skills\testing-patterns\scripts\test_runner.py:66**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**backend\agent\local_client.py:130**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**backend\utils\performance.py:481**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**src\sandbox\docker_exec.py:112**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**src\sandbox\local_exec.py:101**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_cache_efficiency.py:202**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_cache_efficiency.py:61**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_cache_efficiency.py:102**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_cache_efficiency.py:121**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_cache_efficiency.py:160**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_cache_efficiency.py:295**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_cache_efficiency.py:328**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_memory_usage.py:214**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**tests\performance\test_memory_usage.py:131**
- Bare except clause found - catches all exceptions
- *Suggestion:* Specify exception types: except (ValueError, KeyError):

**health-check.sh:44**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**health-check.sh:187**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**health-check.sh:188**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**health-check.sh:191**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**health-check.sh:192**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**health-check.sh:227**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**health-check.sh:230**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:99**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:157**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:227**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:229**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:230**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:231**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:232**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:233**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:240**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:242**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:243**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:244**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:245**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install-remote.sh:300**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:126**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:127**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:315**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:665**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:666**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:668**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:669**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:699**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:706**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:708**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:709**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:710**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:711**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:712**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:719**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:721**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:722**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**install.sh:723**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**quick-fix.sh:24**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**quick-fix.sh:140**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**stop.sh:106**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**stop.sh:111**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**test-fixes.sh:191**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**test-fixes.sh:197**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**test-settings-ui.sh:198**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**test-settings-ui.sh:216**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**test-setup.sh:226**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**test-setup.sh:232**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**test-setup.sh:264**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**validate-phase2.sh:210**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**validate-rotator.sh:241**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**validate-rotator.sh:253**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**validate.sh:359**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**validate.sh:365**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**validate.sh:367**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**validate.sh:378**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

**verify-phase3.sh:74**
- Unquoted variable - may cause word splitting
- *Suggestion:* Quote variables: "$VAR" instead of $VAR

### LOW

**requirements.txt:3**
- Package 'pydantic' not version-pinned
- *Suggestion:* Pin package versions for reproducibility: package==1.0.0

**requirements.txt:4**
- Package 'pydantic-settings' not version-pinned
- *Suggestion:* Pin package versions for reproducibility: package==1.0.0

**requirements.txt:5**
- Package 'python-dotenv' not version-pinned
- *Suggestion:* Pin package versions for reproducibility: package==1.0.0

**requirements.txt:6**
- Package 'pytest' not version-pinned
- *Suggestion:* Pin package versions for reproducibility: package==1.0.0

**requirements.txt:8**
- Package 'httpx' not version-pinned
- *Suggestion:* Pin package versions for reproducibility: package==1.0.0

**requirements.txt:9**
- Package 'mcp' not version-pinned
- *Suggestion:* Pin package versions for reproducibility: package==1.0.0

### INFO

**locustfile.py:246**
- Missing docstring for function 'tick'
- *Suggestion:* Add a docstring describing the purpose and parameters

**locustfile.py:263**
- Missing docstring for function 'tick'
- *Suggestion:* Add a docstring describing the purpose and parameters

**locustfile.py:289**
- Missing docstring for function 'tick'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\auto_preview.py:26**
- Missing docstring for function 'get_project_root'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\auto_preview.py:29**
- Missing docstring for function 'is_running'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\auto_preview.py:36**
- Missing docstring for function 'get_start_command'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\auto_preview.py:51**
- Missing docstring for function 'start_server'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\auto_preview.py:89**
- Missing docstring for function 'stop_server'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\auto_preview.py:108**
- Missing docstring for function 'status_server'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\auto_preview.py:133**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\checklist.py:30**
- Missing docstring for class 'Colors'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\checklist.py:40**
- Missing docstring for function 'print_header'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\checklist.py:45**
- Missing docstring for function 'print_step'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\checklist.py:48**
- Missing docstring for function 'print_success'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\checklist.py:51**
- Missing docstring for function 'print_warning'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\checklist.py:54**
- Missing docstring for function 'print_error'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\checklist.py:162**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\session_manager.py:19**
- Missing docstring for function 'get_project_root'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\session_manager.py:22**
- Missing docstring for function 'analyze_package_json'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\session_manager.py:56**
- Missing docstring for function 'count_files'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\session_manager.py:67**
- Missing docstring for function 'detect_features'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\session_manager.py:82**
- Missing docstring for function 'print_status'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\session_manager.py:106**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\verify_all.py:33**
- Missing docstring for class 'Colors'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\verify_all.py:43**
- Missing docstring for function 'print_header'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\verify_all.py:48**
- Missing docstring for function 'print_step'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\verify_all.py:51**
- Missing docstring for function 'print_success'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\verify_all.py:54**
- Missing docstring for function 'print_warning'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\verify_all.py:57**
- Missing docstring for function 'print_error'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\scripts\verify_all.py:263**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\api-patterns\scripts\api_validator.py:162**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\database-design\scripts\schema_validator.py:94**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\frontend-design\scripts\accessibility_checker.py:111**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\frontend-design\scripts\ux_audit.py:98**
- Missing docstring for class 'UXAuditor'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\frontend-design\scripts\ux_audit.py:691**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\frontend-design\scripts\ux_audit.py:105**
- Missing docstring for function 'audit_file'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\frontend-design\scripts\ux_audit.py:674**
- Missing docstring for function 'audit_directory'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\frontend-design\scripts\ux_audit.py:682**
- Missing docstring for function 'get_report'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\geo-fundamentals\scripts\geo_checker.py:222**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\i18n-localization\scripts\i18n_checker.py:199**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\lint-and-validate\scripts\lint_runner.py:116**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\lint-and-validate\scripts\type_coverage.py:128**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\mobile-design\scripts\mobile_audit.py:74**
- Missing docstring for class 'MobileAuditor'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\mobile-design\scripts\mobile_audit.py:631**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\mobile-design\scripts\mobile_audit.py:81**
- Missing docstring for function 'audit_file'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\mobile-design\scripts\mobile_audit.py:613**
- Missing docstring for function 'audit_directory'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\mobile-design\scripts\mobile_audit.py:621**
- Missing docstring for function 'get_report'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\nextjs-react-expert\scripts\react_performance_checker.py:14**
- Missing docstring for class 'PerformanceChecker'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\nextjs-react-expert\scripts\react_performance_checker.py:234**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\seo-fundamentals\scripts\seo_checker.py:148**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**.agent\skills\vulnerability-scanner\scripts\security_scan.py:421**
- Missing docstring for function 'main'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\main.py:73**
- Missing docstring for asyncfunction 'lifespan'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\main.py:1559**
- Missing docstring for class 'AgentSessionRequest'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\main.py:1564**
- Missing docstring for class 'AgentHandoffRequest'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\main.py:1570**
- Missing docstring for class 'CollaborativeRequest'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\watcher.py:14**
- Missing docstring for class 'DropHandler'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\watcher.py:183**
- Missing docstring for class 'Watcher'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\agent\gemini_client.py:7**
- Missing docstring for class 'GeminiClient'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\agent\local_client.py:7**
- Missing docstring for class 'LocalClient'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\agent\orchestrator.py:36**
- Missing docstring for class 'Orchestrator'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\rag\ingest.py:22**
- Missing docstring for class 'IngestionPipeline'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\rag\store.py:20**
- Missing docstring for class 'VectorStore'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\utils\performance.py:765**
- Missing docstring for asyncfunction 'capture_metrics_task'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\utils\performance.py:774**
- Missing docstring for asyncfunction 'startup_event'
- *Suggestion:* Add a docstring describing the purpose and parameters

**backend\utils\performance.py:779**
- Missing docstring for asyncfunction 'shutdown_event'
- *Suggestion:* Add a docstring describing the purpose and parameters

**tests\conftest.py:232**
- Missing docstring for asyncfunction 'root'
- *Suggestion:* Add a docstring describing the purpose and parameters

**tests\conftest.py:236**
- Missing docstring for asyncfunction 'health'
- *Suggestion:* Add a docstring describing the purpose and parameters

**tools\split_monolith.py:9**
- Missing docstring for function 'split_monolith'
- *Suggestion:* Add a docstring describing the purpose and parameters


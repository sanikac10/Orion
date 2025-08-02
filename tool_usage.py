tools = [
    {
        "type": "function",
        "function": {
            "name": "search_code_issues",
            "description": "Search through code issues and bug reports by keywords, status, or assignee",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term to look for in issue titles and discussions"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["in_progress", "resolved", "planned", "blocked"],
                        "description": "Filter by issue status"
                    },
                    "assignee": {
                        "type": "string",
                        "description": "Filter by person assigned to the issue"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "get_issue_by_id",
            "description": "Get detailed information about a specific issue by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_id": {
                        "type": "string",
                        "description": "The unique ID of the issue (e.g., context_001)"
                    }
                },
                "required": ["issue_id"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_issues_by_location",
            "description": "Find all issues related to a specific file or code location",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path or partial path to search for (e.g., jwt_handler.py or /src/auth/)"
                    }
                },
                "required": ["file_path"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Search through emails by subject, body content, sender, or read status",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term to look for in email subjects and body content"
                    },
                    "sender": {
                        "type": "string",
                        "description": "Filter by email sender (partial match)"
                    },
                    "read_status": {
                        "type": "boolean",
                        "description": "Filter by read status (true for read, false for unread)"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_email_by_id",
            "description": "Get detailed information about a specific email by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "The unique ID of the email (e.g., email_001)"
                    }
                },
                "required": ["email_id"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_emails_by_sender",
            "description": "Get all emails from a specific sender",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {
                        "type": "string",
                        "description": "Email address or name of the sender"
                    }
                },
                "required": ["sender"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_repo_files",
            "description": "Search repository files by path, language, or contributor",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term to look for in file paths"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "typescript", "yaml", "markdown", "json", "shell", "sql"],
                        "description": "Filter by programming language"
                    },
                    "contributor": {
                        "type": "string",
                        "description": "Filter by contributor name"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_by_path",
            "description": "Get detailed information about a specific file by its path",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File path to search for (e.g., jwt_handler.py or /src/auth/)"
                    }
                },
                "required": ["file_path"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_dependencies",
            "description": "Find dependency information by package name",
            "parameters": {
                "type": "object",
                "properties": {
                    "package_name": {
                        "type": "string",
                        "description": "Name of the package/dependency to search for"
                    }
                },
                "required": ["package_name"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_local_files",
            "description": "Search local filesystem files by path, extension, or directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term to look for in file paths"
                    },
                    "extension": {
                        "type": "string",
                        "enum": [".pdf", ".md", ".py", ".yml", ".txt", ".png", ".tar.gz", ".xlsx", ".json", ".env", ".html"],
                        "description": "Filter by file extension"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Filter by directory path (e.g., Downloads, Documents, Code)"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_local_file_by_path",
            "description": "Get detailed information about a specific local file by its path",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Local file path to search for"
                    }
                },
                "required": ["file_path"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_directory_info",
            "description": "Get information about a specific directory including file count and size",
            "parameters": {
                "type": "object",
                "properties": {
                    "dir_path": {
                        "type": "string",
                        "description": "Directory path to get information for"
                    }
                },
                "required": ["dir_path"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "Search restaurants by cuisine, area, or dietary restrictions",
            "parameters": {
                "type": "object",
                "properties": {
                    "cuisine": {
                        "type": "string",
                        "enum": ["american", "italian", "indian", "coffee", "mexican", "french", "seafood", "vegetarian", "chinese", "burmese", "fusion", "greek"],
                        "description": "Filter by cuisine type"
                    },
                    "area": {
                        "type": "string",
                        "enum": ["downtown", "berkeley", "mission", "north_beach", "marina", "castro", "sunset", "haight", "palo_alto", "chinatown"],
                        "description": "Filter by area/neighborhood"
                    },
                    "dietary": {
                        "type": "string",
                        "enum": ["vegetarian", "vegan_options", "gluten_free", "halal", "organic"],
                        "description": "Filter by dietary options"
                    }
                },
                "required": [],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_by_id",
            "description": "Get detailed information about a specific restaurant by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_id": {
                        "type": "string",
                        "description": "The unique ID of the restaurant (e.g., rest_001)"
                    }
                },
                "required": ["restaurant_id"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_restaurants_by_distance",
            "description": "Find restaurants within a specific distance, sorted by proximity",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_distance_km": {
                        "type": "number",
                        "description": "Maximum distance in kilometers"
                    }
                },
                "required": ["max_distance_km"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_system_logs",
            "description": "Search system logs by service, log level, or error code",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "enum": ["auth-service", "monitoring-service", "database", "api-gateway", "load-balancer", "redis-cache", "payment-service", "user-service"],
                        "description": "Filter by service name"
                    },
                    "level": {
                        "type": "string",
                        "enum": ["ERROR", "CRITICAL", "INFO", "WARN", "DEBUG"],
                        "description": "Filter by log level"
                    },
                    "error_code": {
                        "type": "string",
                        "description": "Filter by specific error code"
                    }
                },
                "required": [],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_metrics_by_service",
            "description": "Get performance metrics for a specific service",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name to get metrics for"
                    }
                },
                "required": ["service"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_logs_by_timeframe",
            "description": "Get logs within a specific time range",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Start timestamp in ISO format (e.g., 2024-01-15T09:00:00Z)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End timestamp in ISO format (e.g., 2024-01-15T18:00:00Z)"
                    }
                },
                "required": ["start_time", "end_time"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_transactions",
            "description": "Search financial transactions by category, employee, or card type",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["alerts", "transportation", "infrastructure", "meals", "office", "consulting", "software"],
                        "description": "Filter by transaction category"
                    },
                    "employee": {
                        "type": "string",
                        "description": "Filter by employee name"
                    },
                    "card_type": {
                        "type": "string",
                        "enum": ["corporate", "personal"],
                        "description": "Filter by card type"
                    }
                },
                "required": [],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_transaction_by_id",
            "description": "Get detailed information about a specific transaction by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The unique ID of the transaction (e.g., TXN-20240115-0001)"
                    }
                },
                "required": ["transaction_id"],
                "additionalProperties": False
            },
            "strict": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expenses_by_timeframe",
            "description": "Get all expenses within a specific time range",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": "Start timestamp in ISO format (e.g., 2024-01-15T09:00:00Z)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End timestamp in ISO format (e.g., 2024-01-15T18:00:00Z)"
                    }
                },
                "required": ["start_time", "end_time"],
                "additionalProperties": False
            },
            "strict": False
        }
    }
]

from tools import search_code_issues, get_issue_by_id, get_issues_by_location, search_emails, get_email_by_id, get_emails_by_sender, search_repo_files, get_file_by_path, search_dependencies, search_local_files, get_local_file_by_path, get_directory_info, search_restaurants, get_restaurant_by_id, find_restaurants_by_distance, search_system_logs, get_metrics_by_service, get_logs_by_timeframe, search_transactions, get_transaction_by_id, get_expenses_by_timeframe
import json

if __name__ == "__main__":
    print("Testing search_code_issues:")
    result = search_code_issues("JWT", "resolved")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_issue_by_id:")
    result = get_issue_by_id("context_001")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_issues_by_location:")
    result = get_issues_by_location("jwt_handler.py")
    print(json.dumps(result, indent=2))
    
    print("\nTesting search_emails:")
    result = search_emails("JWT", None, False)
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_email_by_id:")
    result = get_email_by_id("email_001")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_emails_by_sender:")
    result = get_emails_by_sender("sarah.johnson")
    print(json.dumps(result, indent=2))
    
    print("\nTesting search_repo_files:")
    result = search_repo_files("auth", "python")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_file_by_path:")
    result = get_file_by_path("jwt_handler.py")
    print(json.dumps(result, indent=2))
    
    print("\nTesting search_dependencies:")
    result = search_dependencies("pyjwt")
    print(json.dumps(result, indent=2))
    
    print("\nTesting search_local_files:")
    result = search_local_files("auth", ".pdf")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_local_file_by_path:")
    result = get_local_file_by_path("debug_session")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_directory_info:")
    result = get_directory_info("Downloads")
    print(json.dumps(result, indent=2))
    
    print("\nTesting search_restaurants:")
    result = search_restaurants("indian", None, "vegetarian")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_restaurant_by_id:")
    result = get_restaurant_by_id("rest_003")
    print(json.dumps(result, indent=2))
    
    print("\nTesting find_restaurants_by_distance:")
    result = find_restaurants_by_distance(2.0)
    print(json.dumps(result, indent=2))
    
    print("\nTesting search_system_logs:")
    result = search_system_logs("auth-service", "ERROR")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_metrics_by_service:")
    result = get_metrics_by_service("auth-service")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_logs_by_timeframe:")
    result = get_logs_by_timeframe("2024-01-15T09:00:00Z", "2024-01-15T16:00:00Z")
    print(json.dumps(result, indent=2))
    
    print("\nTesting search_transactions:")
    result = search_transactions("infrastructure", None, "corporate")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_transaction_by_id:")
    result = get_transaction_by_id("TXN-20240115-0001")
    print(json.dumps(result, indent=2))
    
    print("\nTesting get_expenses_by_timeframe:")
    result = get_expenses_by_timeframe("2024-01-15T09:00:00Z", "2024-01-15T18:00:00Z")
    print(json.dumps(result, indent=2))
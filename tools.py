import json
from typing import List, Dict, Any, Optional

def load_code_contexts():
    with open('data_lake/code_contexts.json', 'r') as f:
        return json.load(f)['code_context']

def load_emails():
    with open('data_lake/emails.json', 'r') as f:
        return json.load(f)['emails']

def load_github_repo():
    with open('data_lake/github_repo_alignment.json', 'r') as f:
        return json.load(f)

def load_filesystem():
    with open('data_lake/local_filesystem.json', 'r') as f:
        return json.load(f)

def load_restaurants():
    with open('data_lake/restaurant.json', 'r') as f:
        return json.load(f)['restaurants']

def load_system_logs():
    with open('data_lake/system_logs.json', 'r') as f:
        return json.load(f)

def load_transactions():
    with open('data_lake/transactions.json', 'r') as f:
        return json.load(f)['finance_transactions']

def search_code_issues(query: str, status: Optional[str] = None, assignee: Optional[str] = None) -> List[Dict[str, Any]]:
    contexts = load_code_contexts()
    results = []
    
    for context in contexts:
        if query.lower() in context['issue_title'].lower() or query.lower() in context['discussion'].lower():
            if status is None or context['status'] == status:
                if assignee is None or context['assignee'] == assignee:
                    results.append(context)
    
    return results

def get_issue_by_id(issue_id: str) -> Optional[Dict[str, Any]]:
    contexts = load_code_contexts()
    
    for context in contexts:
        if context['id'] == issue_id:
            return context
    
    return None

def get_issues_by_location(file_path: str) -> List[Dict[str, Any]]:
    contexts = load_code_contexts()
    results = []
    
    for context in contexts:
        for location in context['locations']:
            if file_path in location:
                results.append(context)
                break
    
    return results

def search_emails(query: str, sender: Optional[str] = None, read_status: Optional[bool] = None) -> List[Dict[str, Any]]:
    emails = load_emails()
    results = []
    
    for email in emails:
        if query.lower() in email['subject'].lower() or query.lower() in email['body'].lower():
            if sender is None or sender.lower() in email['from'].lower():
                if read_status is None or email.get('read') == read_status:
                    results.append(email)
    
    return results

def get_email_by_id(email_id: str) -> Optional[Dict[str, Any]]:
    emails = load_emails()
    
    for email in emails:
        if email['id'] == email_id:
            return email
    
    return None

def get_emails_by_sender(sender: str) -> List[Dict[str, Any]]:
    emails = load_emails()
    results = []
    
    for email in emails:
        if sender.lower() in email['from'].lower():
            results.append(email)
    
    return results

def search_repo_files(query: str, language: Optional[str] = None, contributor: Optional[str] = None) -> List[Dict[str, Any]]:
    repo_data = load_github_repo()
    files = repo_data['files']
    results = []
    
    for file in files:
        if query.lower() in file['path'].lower():
            if language is None or file['language'].lower() == language.lower():
                if contributor is None or contributor.lower() in [c.lower() for c in file['contributors']]:
                    results.append(file)
    
    return results

def get_file_by_path(file_path: str) -> Optional[Dict[str, Any]]:
    repo_data = load_github_repo()
    files = repo_data['files']
    
    for file in files:
        if file_path in file['path']:
            return file
    
    return None

def search_dependencies(package_name: str) -> Optional[Dict[str, Any]]:
    repo_data = load_github_repo()
    dependencies = repo_data['dependencies']
    
    for dep in dependencies:
        if package_name.lower() in dep['package'].lower():
            return dep
    
    return None

def search_local_files(query: str, extension: Optional[str] = None, directory: Optional[str] = None) -> List[Dict[str, Any]]:
    fs_data = load_filesystem()
    files = fs_data['files']
    results = []
    
    for file in files:
        if query.lower() in file['path'].lower():
            if extension is None or file['extension'].lower() == extension.lower():
                if directory is None or directory.lower() in file['path'].lower():
                    results.append(file)
    
    return results

def get_local_file_by_path(file_path: str) -> Optional[Dict[str, Any]]:
    fs_data = load_filesystem()
    files = fs_data['files']
    
    for file in files:
        if file_path in file['path']:
            return file
    
    return None

def get_directory_info(dir_path: str) -> Optional[Dict[str, Any]]:
    fs_data = load_filesystem()
    directories = fs_data['directories']
    
    for directory in directories:
        if dir_path in directory['path']:
            return directory
    
    return None

def search_restaurants(cuisine: Optional[str] = None, area: Optional[str] = None, dietary: Optional[str] = None) -> List[Dict[str, Any]]:
    restaurants = load_restaurants()
    results = []
    
    for restaurant in restaurants:
        if cuisine is None or restaurant['cuisine'].lower() == cuisine.lower():
            if area is None or restaurant['area'].lower() == area.lower():
                if dietary is None or restaurant.get(dietary, False):
                    results.append(restaurant)
    
    return results

def get_restaurant_by_id(restaurant_id: str) -> Optional[Dict[str, Any]]:
    restaurants = load_restaurants()
    
    for restaurant in restaurants:
        if restaurant['id'] == restaurant_id:
            return restaurant
    
    return None

def find_restaurants_by_distance(max_distance_km: float) -> List[Dict[str, Any]]:
    restaurants = load_restaurants()
    results = []
    
    for restaurant in restaurants:
        if restaurant['distance_km'] <= max_distance_km:
            results.append(restaurant)
    
    return sorted(results, key=lambda x: x['distance_km'])

def search_system_logs(service: Optional[str] = None, level: Optional[str] = None, error_code: Optional[str] = None) -> List[Dict[str, Any]]:
    log_data = load_system_logs()
    logs = log_data['logs']
    results = []
    
    for log in logs:
        if service is None or log['service'].lower() == service.lower():
            if level is None or log['level'].lower() == level.lower():
                if error_code is None or log.get('error_code', '').lower() == error_code.lower():
                    results.append(log)
    
    return results

def get_metrics_by_service(service: str) -> List[Dict[str, Any]]:
    log_data = load_system_logs()
    metrics = log_data['metrics']
    results = []
    
    for metric in metrics:
        if service.lower() in metric['service'].lower():
            results.append(metric)
    
    return results

def get_logs_by_timeframe(start_time: str, end_time: str) -> List[Dict[str, Any]]:
    log_data = load_system_logs()
    logs = log_data['logs']
    results = []
    
    for log in logs:
        if start_time <= log['timestamp'] <= end_time:
            results.append(log)
    
    return results

def search_transactions(category: Optional[str] = None, employee: Optional[str] = None, card_type: Optional[str] = None) -> List[Dict[str, Any]]:
    transactions = load_transactions()
    results = []
    
    for transaction in transactions:
        if category is None or transaction['category'].lower() == category.lower():
            if employee is None or employee.lower() in transaction['employee'].lower():
                if card_type is None or transaction['card_type'].lower() == card_type.lower():
                    results.append(transaction)
    
    return results

def get_transaction_by_id(transaction_id: str) -> Optional[Dict[str, Any]]:
    transactions = load_transactions()
    
    for transaction in transactions:
        if transaction['transaction_id'] == transaction_id:
            return transaction
    
    return None

def get_expenses_by_timeframe(start_time: str, end_time: str) -> List[Dict[str, Any]]:
    transactions = load_transactions()
    results = []
    
    for transaction in transactions:
        if start_time <= transaction['timestamp'] <= end_time:
            results.append(transaction)
    
    return results
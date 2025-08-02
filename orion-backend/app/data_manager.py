# app/data_manager.py
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class DataManager:
    def __init__(self, data_directory: str = None):
        if data_directory is None:
            # Point to the correct data-lake directory
            project_root = Path(__file__).parent.parent.parent  # Go up to orion/
            self.data_dir = project_root / "data-lake"
        else:
            self.data_dir = Path(data_directory)
        
        print(f"📁 Data directory: {self.data_dir}")
        
        self.data_cache = {}
        self.load_all_data()
    
    def load_all_data(self):
        """Load all JSON files into memory for fast access"""
        json_files = [
            "code_context.json",
            "emails.json", 
            "github_repo_alignment.json",
            "local_filesystem.json",
            "restaurants.json",
            "system_logs.json",
            "transactions.json"
        ]
        
        for file_name in json_files:
            file_path = self.data_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data_key = file_name.replace('.json', '')
                        self.data_cache[data_key] = json.load(f)
                        print(f"✅ Loaded {file_name}")
                except Exception as e:
                    print(f"❌ Error loading {file_name}: {e}")
                    self.data_cache[data_key] = {}
            else:
                print(f"⚠️ File not found: {file_name}")
                self.data_cache[file_name.replace('.json', '')] = {}
    
    # Conversation Persistence Methods
    def save_learning_session(self, session_id: str, learning_session: 'LearningSession'):
        """Save active learning conversation to JSON file"""
        file_path = self.conversation_dir / f"{session_id}_learning_state.json"
        try:
            with open(file_path, 'w') as f:
                json.dump(learning_session.model_dump(), f, indent=2)
            print(f"💾 Saved learning session: {session_id}")
        except Exception as e:
            print(f"❌ Error saving learning session {session_id}: {e}")
    
    def load_learning_session(self, session_id: str) -> Optional['LearningSession']:
        """Load active learning conversation from JSON file"""
        from .models import LearningSession  # Import here to avoid circular import
        
        file_path = self.conversation_dir / f"{session_id}_learning_state.json"
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return LearningSession(**data)
        except Exception as e:
            print(f"❌ Error loading learning session {session_id}: {e}")
            return None
    
    def delete_learning_session(self, session_id: str):
        """Delete learning session file (when conversation completes)"""
        file_path = self.conversation_dir / f"{session_id}_learning_state.json"
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️ Deleted learning session: {session_id}")
    
    def get_all_active_sessions(self) -> List[str]:
        """Get list of all active learning session IDs"""
        session_files = list(self.conversation_dir.glob("*_learning_state.json"))
        return [f.stem.replace("_learning_state", "") for f in session_files]
    
    # Pattern Cache Persistence Methods
    def save_task_pattern(self, pattern: 'TaskPattern'):
        """Save learned task pattern to cache"""
        from .models import TaskPattern
        
        cache_file = self.learning_cache_dir / f"{pattern.task_type}_patterns.json"
        
        # Load existing patterns
        patterns = []
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    existing_data = json.load(f)
                    patterns = existing_data.get("patterns", [])
            except Exception as e:
                print(f"❌ Error loading existing patterns: {e}")
        
        # Add or update pattern
        pattern_dict = pattern.model_dump()
        
        # Check if pattern already exists (update) or add new
        updated = False
        for i, existing_pattern in enumerate(patterns):
            if existing_pattern["pattern_id"] == pattern.pattern_id:
                patterns[i] = pattern_dict
                updated = True
                break
        
        if not updated:
            patterns.append(pattern_dict)
        
        # Save back to file
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    "task_type": pattern.task_type,
                    "last_updated": datetime.now().isoformat(),
                    "pattern_count": len(patterns),
                    "patterns": patterns
                }, f, indent=2)
            print(f"💾 Saved task pattern: {pattern.pattern_id}")
        except Exception as e:
            print(f"❌ Error saving task pattern: {e}")
    
    def load_task_patterns(self, task_type: str) -> List['TaskPattern']:
        """Load all cached patterns for a task type"""
        from .models import TaskPattern
        
        cache_file = self.learning_cache_dir / f"{task_type}_patterns.json"
        if not cache_file.exists():
            return []
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                patterns = []
                for pattern_dict in data.get("patterns", []):
                    patterns.append(TaskPattern(**pattern_dict))
                return patterns
        except Exception as e:
            print(f"❌ Error loading task patterns for {task_type}: {e}")
            return []
    
    def get_all_cached_patterns(self) -> Dict[str, List['TaskPattern']]:
        """Get all cached patterns grouped by task type"""
        all_patterns = {}
        
        cache_files = list(self.learning_cache_dir.glob("*_patterns.json"))
        for cache_file in cache_files:
            task_type = cache_file.stem.replace("_patterns", "")
            patterns = self.load_task_patterns(task_type)
            if patterns:
                all_patterns[task_type] = patterns
        
        return all_patterns

    # Calendar/Appointment Methods
    def get_user_calendar(self, date: str = None) -> List[Dict]:
        """Get user's calendar events - mock for now since no calendar in data"""
        # Mock calendar data for appointment booking demo
        mock_calendar = [
            {
                "date": "2024-01-14", 
                "time": "15:00-16:00",
                "title": "Team meeting",
                "attendees": ["sarah@company.com", "alex@company.com"]
            },
            {
                "date": "2024-01-19",  # Friday
                "time": "12:30-13:15", 
                "title": "Lunch break",
                "type": "personal"
            },
            {
                "date": "2024-01-21",  # Sunday  
                "time": "15:00-16:00",
                "title": "Team sync call",
                "type": "work"
            }
        ]
        
        if date:
            return [event for event in mock_calendar if event["date"] == date]
        return mock_calendar
    
    def get_contact_info(self, name: str) -> Optional[Dict]:
        """Get contact information from emails or mock data"""
        name_lower = name.lower()
        
        # Check emails for contact info
        emails = self.data_cache.get("emails", {}).get("emails", [])
        for email in emails:
            if name_lower in email.get("from", "").lower():
                return {
                    "name": name,
                    "email": email["from"],
                    "found_in": "emails",
                    "last_interaction": email.get("timestamp"),
                    "calendar_access": True  # Mock
                }
        
        # Mock contact data for demo
        mock_contacts = {
            "aman": {"name": "Aman", "email": "aman@company.com", "calendar_access": True},
            "supriti": {"name": "Supriti", "email": "supriti@company.com", "calendar_access": True},
            "alex": {"name": "Alex Chen", "email": "alex@company.com", "calendar_access": True},
            "sarah": {"name": "Sarah Johnson", "email": "sarah.johnson@company.com", "calendar_access": True}
        }
        
        return mock_contacts.get(name_lower)
    
    def check_availability(self, contact_name: str, date: str, time: str) -> Dict:
        """Check if contact is available at given time - mock implementation"""
        # Mock availability check - simulate realistic conflicts
        conflicts = {
            ("aman", "2024-01-21", "15:00"): False,  # Aman busy at 3PM Sunday
            ("supriti", "2024-01-19", "13:00"): False,  # Supriti busy at 1PM Friday
        }
        
        key = (contact_name.lower(), date, time)
        is_available = key not in conflicts
        
        return {
            "contact": contact_name,
            "date": date,
            "time": time,
            "available": is_available,
            "alternative_slots": ["14:00-15:00", "16:00-17:00"] if not is_available else [],
            "confidence": 0.9
        }
    
    def book_appointment(self, user: str, contact: str, date: str, time: str, title: str = None) -> Dict:
        """Mock booking an appointment - in real system would write to calendar"""
        appointment = {
            "id": f"apt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user": user,
            "contact": contact,
            "date": date,
            "time": time,
            "title": title or f"Meeting with {contact}",
            "status": "booked",
            "created_at": datetime.now().isoformat()
        }
        
        # Save to a mock appointments file
        appointments_file = self.data_dir / "appointments.json"
        appointments = []
        
        if appointments_file.exists():
            try:
                with open(appointments_file, 'r') as f:
                    appointments = json.load(f).get("appointments", [])
            except:
                pass
        
        appointments.append(appointment)
        
        try:
            with open(appointments_file, 'w') as f:
                json.dump({"appointments": appointments}, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving appointment: {e}")
        
        return appointment
    
    # Restaurant Methods
    def get_restaurants(self, **filters) -> List[Dict]:
        """Get restaurants with filtering"""
        restaurants = self.data_cache.get("restaurants", {}).get("restaurants", [])
        
        filtered = restaurants
        
        if filters.get("cuisine"):
            cuisine = filters["cuisine"].lower()
            filtered = [r for r in filtered if cuisine in r.get("cuisine", "").lower()]
        
        if filters.get("area"):
            area = filters["area"].lower()
            filtered = [r for r in filtered if area in r.get("area", "").lower()]
        
        if filters.get("vegetarian"):
            filtered = [r for r in filtered if r.get("vegetarian", False)]
        
        return filtered[:10]  # Limit results
    
    # Code Context Methods
    def search_code_context(self, query: str) -> List[Dict]:
        """Search through code context for relevant issues"""
        contexts = self.data_cache.get("code_context", [])
        query_lower = query.lower()
        
        matches = []
        for context in contexts:
            # Simple keyword matching
            if (query_lower in context.get("issue_title", "").lower() or 
                query_lower in context.get("discussion", "").lower()):
                matches.append(context)
        
        return matches
    
    # System Logs Methods  
    def get_system_logs(self, service: str = None, level: str = None) -> List[Dict]:
        """Get system logs with filtering"""
        logs = self.data_cache.get("system_logs", {}).get("logs", [])
        
        filtered = logs
        if service:
            filtered = [log for log in filtered if log.get("service") == service]
        if level:
            filtered = [log for log in filtered if log.get("level") == level]
            
        return filtered
    
    # Email Methods
    def search_emails(self, query: str = None, from_email: str = None) -> List[Dict]:
        """Search through emails"""
        emails = self.data_cache.get("emails", {}).get("emails", [])
        
        if not query and not from_email:
            return emails
            
        matches = []
        for email in emails:
            if query and query.lower() in email.get("subject", "").lower():
                matches.append(email)
            elif from_email and from_email.lower() in email.get("from", "").lower():
                matches.append(email)
                
        return matches
    
    # Generic search method for RAG
    def search_all_data(self, query: str) -> Dict[str, List]:
        """Search across all data sources for RAG-style retrieval"""
        query_lower = query.lower()
        results = {}
        
        # Search restaurants
        if any(word in query_lower for word in ["restaurant", "food", "eat", "dining"]):
            results["restaurants"] = self.get_restaurants()
        
        # Search code context
        if any(word in query_lower for word in ["bug", "error", "jwt", "auth", "code", "fix"]):
            results["code_context"] = self.search_code_context(query)
        
        # Search emails
        if any(word in query_lower for word in ["email", "message", "discuss", "meeting", "appointment"]):
            results["emails"] = self.search_emails(query)
        
        # Search logs
        if any(word in query_lower for word in ["log", "error", "system", "failure"]):
            results["logs"] = self.get_system_logs()
            
        # Search calendar for appointments
        if any(word in query_lower for word in ["appointment", "meeting", "schedule", "book", "calendar"]):
            results["calendar"] = self.get_user_calendar()
        
        return results
    
    def get_all_active_sessions(self) -> List[str]:
        """Get all active learning session IDs from files"""
        flows_dir = Path("conversation_flows")
        if not flows_dir.exists():
            return []
        
        session_ids = []
        for file_path in flows_dir.glob("*_learning_state.json"):
            session_id = file_path.stem.replace("_learning_state", "")
            session_ids.append(session_id)
        
        return session_ids

    def save_learning_session(self, session_id: str, learning_session):
        """Save learning session to file"""
        flows_dir = Path("conversation_flows")
        flows_dir.mkdir(exist_ok=True)
        
        file_path = flows_dir / f"{session_id}_learning_state.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(learning_session.model_dump(), f, indent=2)
        except Exception as e:
            print(f"❌ Error saving learning session {session_id}: {e}")

    def load_learning_session(self, session_id: str):
        """Load learning session from file"""
        flows_dir = Path("conversation_flows")
        file_path = flows_dir / f"{session_id}_learning_state.json"
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Convert back to LearningSession object
                    from .models import LearningSession
                    return LearningSession(**data)
            except Exception as e:
                print(f"❌ Error loading learning session {session_id}: {e}")
        
        return None

    def delete_learning_session(self, session_id: str):
        """Delete learning session file"""
        flows_dir = Path("conversation_flows")
        file_path = flows_dir / f"{session_id}_learning_state.json"
        
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"❌ Error deleting learning session {session_id}: {e}")

# Global instance
data_manager = DataManager()
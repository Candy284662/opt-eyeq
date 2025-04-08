curl -X POST -H "Content-Type: application/json" -d '{
    "hostname": "W11-TEST-HOST",
    "ip_address": "192.168.1.1",
    "os": "Windows 11",
    "disk_usage": 95,
    "memory_usage": 60,
    "process_count": 180,
    "logged_in_users": 3
}' http://localhost:5000/submit

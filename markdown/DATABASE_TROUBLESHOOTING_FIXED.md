# Database Connection Troubleshooting Guide

## 🚨 MySQL "Server has gone away" Error Resolution

This guide helps resolve the common MySQL OperationalError that you encountered:
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2006, "MySQL server has gone away (BrokenPipeError(32, 'Broken pipe'))")
```

---

## 🔧 Immediate Solutions Implemented

### 1. **Enhanced Connection Pooling**
- ✅ Added `SQLALCHEMY_POOL_PRE_PING = True` - Tests connections before use
- ✅ Set `SQLALCHEMY_POOL_RECYCLE = 280` - Recycles connections every 280 seconds
- ✅ Configured connection pool size and overflow limits
- ✅ Added connection timeouts and charset settings

### 2. **Automatic Connection Recovery**
- ✅ Created `app/database.py` with retry logic and error handling
- ✅ Added `@handle_db_connection_error` decorator for database operations
- ✅ Implemented `recover_db_connection()` function
- ✅ Updated user loader to handle connection errors gracefully

### 3. **Error Handlers & Monitoring**
- ✅ Added database-specific error handlers in Flask app
- ✅ Created health check endpoints (`/api/health/db`)
- ✅ Added CLI commands for database testing and recovery
- ✅ Created monitoring script (`monitor_db.py`)

---

## 🛠️ Usage Instructions

### Test Database Connection
```bash
# Single test
python -m flask test-db

# Or using the monitoring script
python monitor_db.py check
```

### Recover Connection
```bash
# Using Flask CLI
python -m flask recover-db

# Or using the monitoring script
python monitor_db.py monitor
```

### Check Database Status
```bash
# Detailed status report
python -m flask db-status

# Via web endpoint
curl http://localhost:5000/api/health/db
```

### Continuous Monitoring
```bash
# Monitor every 30 seconds (default)
python monitor_db.py monitor

# Monitor every 60 seconds
python monitor_db.py monitor 60
```

---

## 🔍 Root Causes & Prevention

### Common Causes:
1. **MySQL timeout settings** - Default wait_timeout is 28800s (8 hours)
2. **Idle connections** - Connections unused for extended periods
3. **Network interruptions** - Temporary network issues
4. **Load balancer timeouts** - Infrastructure-level timeouts
5. **MySQL server restarts** - Server maintenance or crashes

### Prevention Strategies:
1. **Connection recycling** - Automatically refresh connections before timeout
2. **Pre-ping testing** - Test connections before using them  
3. **Retry logic** - Automatic retry with exponential backoff
4. **Connection pooling** - Maintain healthy pool of connections
5. **Monitoring** - Continuous health checks and alerting

---

## 🚀 How The Solution Works

### Connection Pool Configuration:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,        # Test before use
    'pool_recycle': 280,          # Recycle every 280s (< 300s timeout)
    'pool_size': 10,              # Base pool size
    'max_overflow': 20,           # Extra connections
    'pool_timeout': 30,           # Wait timeout
    'connect_args': {
        'connect_timeout': 60,    # Connection timeout
        'read_timeout': 60,       # Read timeout
        'write_timeout': 60,      # Write timeout
        'charset': 'utf8mb4'      # Character set
    }
}
```

### Error Handling Decorator:
```python
@handle_db_connection_error
def safe_get_user_by_id(user_id):
    return Account.query.get(user_id)
```

### Automatic Recovery:
```python
def recover_db_connection():
    # Dispose old connections
    db.engine.dispose()
    
    # Test new connection
    with db.engine.connect() as connection:
        result = connection.execute(text('SELECT 1'))
```

---

## 📊 Monitoring & Alerting

### Health Check Endpoints:
- `GET /api/health` - Basic health status
- `GET /api/health/db` - Database-specific health
- `GET /api/health/detailed` - Comprehensive health report

### Monitoring Commands:
```bash
# Test connection
flask test-db

# Get detailed status  
flask db-status

# Recover connection
flask recover-db

# Continuous monitoring
./monitor_db.py monitor
```

### Log Monitoring:
```bash
# Watch application logs
tail -f /var/log/supervisor/screenshot-to-code.log

# Watch database recovery logs
grep "Database" /var/log/supervisor/screenshot-to-code.log
```

---

## 🆘 Emergency Procedures

### If Error Persists:

1. **Check MySQL Server Status:**
   ```bash
   sudo systemctl status mysql
   ```

2. **Restart MySQL (if needed):**
   ```bash
   sudo systemctl restart mysql
   ```

3. **Check MySQL Configuration:**
   ```bash
   mysql -u root -p -e "SHOW VARIABLES LIKE 'wait_timeout';"
   ```

4. **Force Connection Recovery:**
   ```bash
   python -m flask recover-db
   ```

5. **Restart Application:**
   ```bash
   sudo supervisorctl restart screenshot-to-code
   ```

### MySQL Configuration Tweaks:
Add to `/etc/mysql/mysql.conf.d/mysqld.cnf`:
```ini
[mysqld]
wait_timeout = 28800
interactive_timeout = 28800
max_connections = 200
connect_timeout = 60
```

---

## 📈 Performance Optimization

### Connection Pool Tuning:
```python
# For high-traffic sites
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40

# For low-traffic sites  
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_MAX_OVERFLOW = 10
```

### MySQL Optimization:
```sql
-- Check current connections
SHOW PROCESSLIST;

-- Check connection stats
SHOW STATUS LIKE 'Connections';
SHOW STATUS LIKE 'Max_used_connections';

-- Optimize timeouts
SET GLOBAL wait_timeout = 28800;
SET GLOBAL interactive_timeout = 28800;
```

---

## 🔄 Deployment Integration

The deployment script now includes:
- Pre-deployment database health checks
- Post-deployment verification  
- Automatic recovery attempts
- Health monitoring setup

```bash
# Deploy with health checks
./deploy.sh deploy

# Monitor after deployment
./monitor_db.py monitor
```

---

## 📝 Summary

The MySQL "server has gone away" error has been resolved through:

✅ **Enhanced connection pooling** with pre-ping and recycling
✅ **Automatic retry logic** with exponential backoff  
✅ **Connection recovery mechanisms** with graceful fallbacks
✅ **Comprehensive monitoring** with health checks and CLI tools
✅ **Error handling** with user-friendly messages and recovery
✅ **Production deployment** with integrated health checks

The application will now:
- Automatically detect connection issues
- Attempt recovery before failing
- Provide detailed health information
- Continue serving users during temporary database issues
- Log all connection events for debugging

**Next Steps:**
1. Monitor the application with the new tools
2. Adjust connection pool settings based on usage patterns  
3. Set up automated alerts for connection issues
4. Regular health check monitoring in production

The database connection is now robust and production-ready! 🚀

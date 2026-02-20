"""
E.V.E. Master Controller - DATABASE SCHEMA (Production-Ready)
Auto-creates database and tables on startup if they don't exist
Includes: Users, Profiles, AI_Agents, Tasks, Assignments, Results, Context, Performance, Logs
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json
import os
from core.config import DB_CONFIG

# =============================================================================
# CONNECTION MANAGEMENT
# =============================================================================

def get_connection():
    """Get database connection with improved SSL handling"""
    try:
        db_config = DB_CONFIG.copy()

        if 'sslrootcert' in db_config and db_config['sslrootcert']:
            if db_config.get('sslmode') != 'disable':
                if not os.path.isabs(db_config['sslrootcert']):
                    db_config['sslrootcert'] = os.path.join(
                        os.path.dirname(__file__),
                        db_config['sslrootcert']
                    )

        if db_config.get('sslmode') == 'disable':
            db_config.pop('sslrootcert', None)

        conn = psycopg2.connect(
            cursor_factory=RealDictCursor,
            **db_config
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Config: {db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}")
        print(f"   SSL Mode: {db_config.get('sslmode', 'default')}")
        raise

# =============================================================================
# DATABASE INITIALIZATION - PRODUCTION READY
# =============================================================================

def init_database():
    """
    Initialize database schema - ensures all tables exist on startup.
    Fully idempotent - safe to run multiple times.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        print("\n" + "="*70)
        print("🔄 INITIALIZING DATABASE SCHEMA")
        print("="*70)
        print("\n📊 Ensuring all tables exist...")

        # 1. Users (Authentication only — no profile columns here)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       SERIAL PRIMARY KEY,
            email         VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role          VARCHAR(10)  DEFAULT 'user',
            status        VARCHAR(10)  DEFAULT 'active',
            is_verified   BOOLEAN      DEFAULT FALSE,
            created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ users")

        # 2. Profiles (Extended user info — separate table, post-login only)
        #    user_id is both PK and FK → one profile per user.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id    INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
            full_name  VARCHAR(100),
            bio        TEXT,
            pfp_url    TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ profiles")

        # 3. Auth_Logs (Security)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_logs (
            log_id      SERIAL PRIMARY KEY,
            user_id     INTEGER REFERENCES users(user_id),
            login_time  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            auth_status VARCHAR(10) NOT NULL,
            ip_address  VARCHAR(45)
        )
        """)
        print("   ✓ auth_logs")

        # 4. AI_Agents (Registry)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_agents (
            agent_id           SERIAL PRIMARY KEY,
            agent_name         VARCHAR(50) NOT NULL UNIQUE,
            capability         VARCHAR(100) NOT NULL,
            status             VARCHAR(10) DEFAULT 'idle',
            last_heartbeat     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            host               VARCHAR(100),
            port               INTEGER,
            cpu_usage          FLOAT DEFAULT 0.0,
            memory_usage       FLOAT DEFAULT 0.0,
            temperature        FLOAT DEFAULT 0.0,
            total_tasks        INTEGER DEFAULT 0,
            successful_tasks   INTEGER DEFAULT 0,
            failed_tasks       INTEGER DEFAULT 0,
            avg_execution_time FLOAT DEFAULT 0.0,
            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ ai_agents")

        # 5. User_Tasks (Requests)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_tasks (
            task_id     SERIAL PRIMARY KEY,
            user_id     INTEGER REFERENCES users(user_id) DEFAULT 1,
            task_desc   TEXT NOT NULL,
            task_status VARCHAR(10) DEFAULT 'pending',
            task_type   VARCHAR(50),
            priority    INTEGER DEFAULT 1,
            retry_count INTEGER DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ user_tasks")

        # 6. Task_Assignments (Controller)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_assignments (
            task_id          INTEGER PRIMARY KEY REFERENCES user_tasks(task_id) ON DELETE CASCADE,
            agent_id         INTEGER REFERENCES ai_agents(agent_id),
            assigned_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            assignment_order INTEGER DEFAULT 1
        )
        """)
        print("   ✓ task_assignments")

        # 7. Execution_Results (Output)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_results (
            result_id      SERIAL PRIMARY KEY,
            task_id        INTEGER REFERENCES user_tasks(task_id) ON DELETE CASCADE,
            agent_id       INTEGER REFERENCES ai_agents(agent_id),
            output_data    TEXT NOT NULL,
            success        BOOLEAN DEFAULT TRUE,
            error_message  TEXT,
            execution_time FLOAT,
            completed_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ execution_results")

        # 8. Context_Data (Content DB)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS context_data (
            context_id   SERIAL PRIMARY KEY,
            task_id      INTEGER REFERENCES user_tasks(task_id) ON DELETE CASCADE,
            context_data TEXT NOT NULL,
            context_type VARCHAR(50),
            updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ context_data")

        # 9. Performance_Metrics
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_metrics (
            task_id             INTEGER PRIMARY KEY REFERENCES user_tasks(task_id),
            agent_id            INTEGER REFERENCES ai_agents(agent_id),
            exec_time_ms        INTEGER NOT NULL,
            success_rate        FLOAT,
            cpu_at_execution    FLOAT,
            memory_at_execution FLOAT,
            recorded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ performance_metrics")

        # 10. System_Logs — standalone, NOT linked to auth_logs.
        # Auto-repair: drop and recreate if old broken FK schema detected.
        cursor.execute("""
        SELECT column_default
        FROM information_schema.columns
        WHERE table_name = 'system_logs' AND column_name = 'log_id'
        """)
        row = cursor.fetchone()
        if row is not None and (row['column_default'] is None or 'nextval' not in str(row['column_default'])):
            print("   ⚠️  system_logs has broken FK schema — dropping and recreating...")
            cursor.execute("DROP TABLE IF EXISTS system_logs CASCADE")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            log_id     SERIAL PRIMARY KEY,
            log_type   VARCHAR(10) NOT NULL,
            message    TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ system_logs")

        # 11. Task_Queue
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_queue (
            queue_id  SERIAL PRIMARY KEY,
            task_id   INTEGER REFERENCES user_tasks(task_id) UNIQUE,
            priority  INTEGER DEFAULT 1,
            queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            attempts  INTEGER DEFAULT 0
        )
        """)
        print("   ✓ task_queue")

        # 12. Conversations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id VARCHAR(100) PRIMARY KEY,
            user_id         INTEGER REFERENCES users(user_id),
            started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active       BOOLEAN DEFAULT TRUE
        )
        """)
        print("   ✓ conversations")

        # 13. Messages
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id      SERIAL PRIMARY KEY,
            conversation_id VARCHAR(100) REFERENCES conversations(conversation_id),
            role            VARCHAR(20) NOT NULL,
            content         TEXT NOT NULL,
            timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✓ messages")

        # Register Master Controller as the default agent
        cursor.execute("""
        INSERT INTO ai_agents
        (agent_name, capability, status, host, port, last_heartbeat)
        VALUES ('Master-Controller', 'general', 'active', 'localhost', 8000, CURRENT_TIMESTAMP)
        ON CONFLICT (agent_name) DO NOTHING
        """)
        print("   ✓ Master Controller registered")

        conn.commit()

        print("\n✅ Database schema ready!")
        print("="*70 + "\n")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Database initialization failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# PROFILE MANAGEMENT
# =============================================================================

def get_profile(user_id: int) -> Optional[Dict]:
    """Get profile for a user. Returns None if no profile row yet."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT user_id, full_name, bio, pfp_url, updated_at FROM profiles WHERE user_id = %s",
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def upsert_profile(user_id: int, full_name: str = None, bio: str = None) -> Dict:
    """
    Create or update a user's profile row (full_name, bio).
    pfp_url is handled separately via update_profile_avatar.
    Returns the updated profile row.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO profiles (user_id, full_name, bio, updated_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE SET
            full_name  = COALESCE(EXCLUDED.full_name, profiles.full_name),
            bio        = COALESCE(EXCLUDED.bio,        profiles.bio),
            updated_at = CURRENT_TIMESTAMP
        RETURNING user_id, full_name, bio, pfp_url, updated_at
        """, (user_id, full_name, bio))
        result = cursor.fetchone()
        conn.commit()
        return result
    finally:
        cursor.close()
        conn.close()


def update_profile_avatar(user_id: int, pfp_url: str) -> Dict:
    """
    Set / replace the avatar URL for a user's profile.
    Creates the profile row if it doesn't exist yet.
    Returns the updated profile row.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO profiles (user_id, pfp_url, updated_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE SET
            pfp_url    = EXCLUDED.pfp_url,
            updated_at = CURRENT_TIMESTAMP
        RETURNING user_id, full_name, bio, pfp_url, updated_at
        """, (user_id, pfp_url))
        result = cursor.fetchone()
        conn.commit()
        return result
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# AI AGENT MANAGEMENT
# =============================================================================

def register_agent(
    agent_name: str,
    capability: str,
    host: str = "localhost",
    port: int = 5000,
    hardware_stats: Dict = None
) -> int:
    """Register or update AI agent in registry"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hw = hardware_stats or {}
        cursor.execute("""
        INSERT INTO ai_agents
        (agent_name, capability, status, host, port, cpu_usage, memory_usage, temperature, last_heartbeat)
        VALUES (%s, %s, 'idle', %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (agent_name)
        DO UPDATE SET
            last_heartbeat = CURRENT_TIMESTAMP,
            status = 'idle',
            cpu_usage = EXCLUDED.cpu_usage,
            memory_usage = EXCLUDED.memory_usage,
            temperature = EXCLUDED.temperature
        RETURNING agent_id
        """, (
            agent_name, capability, host, port,
            hw.get('cpu', 0.0),
            hw.get('memory', 0.0),
            hw.get('temperature', 0.0)
        ))
        result = cursor.fetchone()
        conn.commit()
        return result['agent_id']
    finally:
        cursor.close()
        conn.close()


def update_agent_heartbeat(agent_name: str, status: str = 'idle', hardware_stats: Dict = None):
    """Update agent heartbeat and hardware stats"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hw = hardware_stats or {}
        cursor.execute("""
        UPDATE ai_agents
        SET last_heartbeat = CURRENT_TIMESTAMP,
            status = %s,
            cpu_usage = %s,
            memory_usage = %s,
            temperature = %s
        WHERE agent_name = %s
        """, (
            status,
            hw.get('cpu', 0.0),
            hw.get('memory', 0.0),
            hw.get('temperature', 0.0),
            agent_name
        ))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_available_agents(task_type: str = None) -> List[Dict]:
    """Get available agents, optionally filtered by task type"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if task_type and task_type not in ['general', 'image_generation']:
            cursor.execute("""
            SELECT * FROM ai_agents
            WHERE last_heartbeat > NOW() - INTERVAL '30 seconds'
              AND (capability LIKE %s OR capability = 'general')
              AND status != 'failed'
            ORDER BY
                CASE status WHEN 'idle' THEN 1 WHEN 'busy' THEN 2 ELSE 3 END,
                cpu_usage ASC, memory_usage ASC
            """, (f'%{task_type}%',))
        else:
            cursor.execute("""
            SELECT * FROM ai_agents
            WHERE last_heartbeat > NOW() - INTERVAL '30 seconds'
              AND status != 'failed'
            ORDER BY
                CASE status WHEN 'idle' THEN 1 WHEN 'busy' THEN 2 ELSE 3 END,
                cpu_usage ASC, memory_usage ASC
            """)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_agent_performance(agent_id: int) -> Dict:
    """Get agent performance metrics"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT
            agent_name, capability, total_tasks, successful_tasks, failed_tasks,
            avg_execution_time, cpu_usage, memory_usage, temperature,
            CASE WHEN total_tasks > 0
                 THEN (successful_tasks::float / total_tasks * 100)
                 ELSE 0
            END as success_rate
        FROM ai_agents WHERE agent_id = %s
        """, (agent_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# TASK MANAGEMENT
# =============================================================================

def create_task(user_id: int, task_desc: str, task_type: str = 'general', priority: int = 1) -> int:
    """Create new user task"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO user_tasks (user_id, task_desc, task_type, priority, task_status)
        VALUES (%s, %s, %s, %s, 'pending') RETURNING task_id
        """, (user_id, task_desc, task_type, priority))
        task_id = cursor.fetchone()['task_id']
        conn.commit()
        return task_id
    finally:
        cursor.close()
        conn.close()


def assign_task_to_agent(task_id: int, agent_id: int, order: int = 1):
    """Assign task to agent"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO task_assignments (task_id, agent_id, assignment_order) VALUES (%s, %s, %s)",
            (task_id, agent_id, order)
        )
        cursor.execute("UPDATE ai_agents SET status = 'busy' WHERE agent_id = %s", (agent_id,))
        cursor.execute(
            "UPDATE user_tasks SET task_status = 'assigned', updated_at = CURRENT_TIMESTAMP WHERE task_id = %s",
            (task_id,)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def store_execution_result(
    task_id: int,
    agent_id: int,
    output_data: str,
    success: bool = True,
    execution_time: float = 0.0,
    error_message: str = None
):
    """Store task execution result"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO execution_results (task_id, agent_id, output_data, success, error_message, execution_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (task_id, agent_id, output_data, success, error_message, execution_time))

        status = 'completed' if success else 'failed'
        cursor.execute(
            "UPDATE user_tasks SET task_status = %s, updated_at = CURRENT_TIMESTAMP WHERE task_id = %s",
            (status, task_id)
        )

        if success:
            cursor.execute("""
            UPDATE ai_agents
            SET total_tasks = total_tasks + 1,
                successful_tasks = successful_tasks + 1,
                avg_execution_time = (avg_execution_time * total_tasks + %s) / (total_tasks + 1),
                status = 'idle'
            WHERE agent_id = %s
            """, (execution_time, agent_id))
        else:
            cursor.execute(
                "UPDATE ai_agents SET total_tasks = total_tasks + 1, failed_tasks = failed_tasks + 1, status = 'idle' WHERE agent_id = %s",
                (agent_id,)
            )

        exec_time_ms = int(execution_time * 1000)
        cursor.execute("""
        SELECT CASE WHEN total_tasks > 0 THEN (successful_tasks::float / total_tasks) ELSE 1.0 END as success_rate,
               cpu_usage, memory_usage FROM ai_agents WHERE agent_id = %s
        """, (agent_id,))
        perf = cursor.fetchone()

        cursor.execute("""
        INSERT INTO performance_metrics (agent_id, task_id, exec_time_ms, success_rate, cpu_at_execution, memory_at_execution)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (agent_id, task_id, exec_time_ms, perf['success_rate'], perf['cpu_usage'], perf['memory_usage']))

        conn.commit()
    finally:
        cursor.close()
        conn.close()


def queue_task(task_id: int, priority: int = 1):
    """Add task to queue"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO task_queue (task_id, priority) VALUES (%s, %s) ON CONFLICT (task_id) DO UPDATE SET priority = EXCLUDED.priority",
            (task_id, priority)
        )
        cursor.execute("UPDATE user_tasks SET task_status = 'queued' WHERE task_id = %s", (task_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_next_queued_task() -> Optional[Dict]:
    """Get next task from queue"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT ut.*, tq.priority, tq.attempts FROM user_tasks ut
        JOIN task_queue tq ON ut.task_id = tq.task_id
        WHERE ut.task_status = 'queued'
        ORDER BY tq.priority DESC, tq.queued_at ASC LIMIT 1
        """)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# CONTEXT MANAGEMENT
# =============================================================================

def store_context(task_id: int, context_data: str, context_type: str = 'conversation'):
    """Store context data for task"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO context_data (task_id, context_data, context_type) VALUES (%s, %s, %s)",
            (task_id, context_data, context_type)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_recent_contexts(limit: int = 10) -> List[Dict]:
    """Get recent context data"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT cd.*, ut.task_desc, ut.task_type FROM context_data cd
        JOIN user_tasks ut ON cd.task_id = ut.task_id
        ORDER BY cd.updated_at DESC LIMIT %s
        """, (limit,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_last_n_messages(conversation_id: str, n: int = 10) -> List[Dict]:
    """
    Get last N messages from a conversation for context.
    Returns messages in chronological order (oldest first).
    """
    if not conversation_id:
        return []
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT message_id, role, content, timestamp FROM messages
        WHERE conversation_id = %s ORDER BY timestamp DESC LIMIT %s
        """, (conversation_id, n))
        messages = cursor.fetchall()
        return list(reversed(messages))
    except Exception as e:
        print(f"⚠️ get_last_n_messages error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def create_or_get_conversation(conversation_id: str, user_id: int = 1) -> str:
    """Create a new conversation or get existing one. Returns conversation_id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO conversations (conversation_id, user_id, started_at, last_updated, is_active)
        VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE)
        ON CONFLICT (conversation_id)
        DO UPDATE SET last_updated = CURRENT_TIMESTAMP, is_active = TRUE
        RETURNING conversation_id
        """, (conversation_id, user_id))
        result = cursor.fetchone()
        conn.commit()
        return result['conversation_id']
    except Exception as e:
        conn.rollback()
        print(f"⚠️ create_or_get_conversation error: {e}")
        return conversation_id
    finally:
        cursor.close()
        conn.close()


def store_message(conversation_id: str, role: str, content: str) -> Optional[int]:
    """
    Store a message in the conversation.
    role: 'user' or 'assistant'
    Returns message_id or None on failure.
    """
    if not conversation_id or not role or not content:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    try:
        create_or_get_conversation(conversation_id)
        cursor.execute("""
        INSERT INTO messages (conversation_id, role, content, timestamp)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP) RETURNING message_id
        """, (conversation_id, role, content))
        result = cursor.fetchone()
        conn.commit()
        return result['message_id']
    except Exception as e:
        conn.rollback()
        print(f"⚠️ store_message error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# LOGGING
# =============================================================================

def log_system_event(log_type: str, message: str, **kwargs):
    """
    Log a system event.
    **kwargs absorbs any legacy keyword arguments so old call sites don't crash.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO system_logs (log_type, message) VALUES (%s, %s)", (log_type, message))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"⚠️ log_system_event error: {e}")
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# STATISTICS
# =============================================================================

def get_system_stats() -> Dict:
    """Get overall system statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        stats = {}
        cursor.execute("""
        SELECT COUNT(*) as total_agents,
               COUNT(CASE WHEN status = 'idle' THEN 1 END) as idle_agents,
               COUNT(CASE WHEN status = 'busy' THEN 1 END) as busy_agents,
               AVG(cpu_usage) as avg_cpu, AVG(memory_usage) as avg_memory
        FROM ai_agents WHERE last_heartbeat > NOW() - INTERVAL '30 seconds'
        """)
        stats['agents'] = dict(cursor.fetchone())

        cursor.execute("""
        SELECT COUNT(*) as total_tasks,
               COUNT(CASE WHEN task_status = 'completed' THEN 1 END) as completed,
               COUNT(CASE WHEN task_status = 'failed' THEN 1 END) as failed,
               COUNT(CASE WHEN task_status = 'queued' THEN 1 END) as queued
        FROM user_tasks
        """)
        stats['tasks'] = dict(cursor.fetchone())

        cursor.execute("""
        SELECT AVG(exec_time_ms) as avg_exec_time_ms, AVG(success_rate) as avg_success_rate
        FROM performance_metrics WHERE recorded_at > NOW() - INTERVAL '1 hour'
        """)
        perf = cursor.fetchone()
        stats['performance'] = dict(perf) if perf else {}

        return stats
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# MASTER FAILOVER COMPATIBILITY
# =============================================================================

def register_master(master_id: str, host: str = "localhost", port: int = 8000):
    print(f"⚠️  Master registration skipped (new schema doesn't use master_states)")
    return True

def update_master_heartbeat(master_id: str, status: str = "active"):
    pass

def set_active_master(master_id: str):
    pass

def get_active_master() -> Optional[Dict]:
    return {"master_id": "master-1", "status": "active", "active": True, "last_heartbeat": datetime.now(timezone.utc).isoformat()}

def get_all_masters() -> List[Dict]:
    return [{"master_id": "master-1", "status": "active", "active": True, "last_heartbeat": datetime.now(timezone.utc).isoformat()}]

# =============================================================================
# AUTO-INITIALIZATION ON MODULE IMPORT
# =============================================================================

try:
    init_database()
except Exception as e:
    print(f"⚠️  Warning: Could not auto-initialize database: {e}")
    print("   Database will be initialized on first connection attempt")

if __name__ == "__main__":
    print("Running database initialization manually...")
    init_database()
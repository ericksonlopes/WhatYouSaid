#!/bin/bash
set -e

EXTRAS=""

SQL_VAL=$(echo "${VECTOR__SQL__TYPE:-$SQL__TYPE}" | tr '[:upper:]' '[:lower:]')

case "$SQL_VAL" in
  "postgres") EXTRAS="$EXTRAS --extra postgres" ;;
  "mysql")    EXTRAS="$EXTRAS --extra mysql"    ;;
  "mariadb")  EXTRAS="$EXTRAS --extra mariadb"  ;;
  "mssql")    EXTRAS="$EXTRAS --extra mssql"    ;;
esac

VEC_VAL=$(echo "$VECTOR__STORE_TYPE" | tr '[:upper:]' '[:lower:]')

case "$VEC_VAL" in
  "weaviate") EXTRAS="$EXTRAS --extra weaviate" ;;
  "faiss")    EXTRAS="$EXTRAS --extra faiss"    ;;
  "chroma")   EXTRAS="$EXTRAS --extra chroma"   ;;
  "qdrant")   EXTRAS="$EXTRAS --extra qdrant"   ;;
esac

if [ "$INSTALL_GPU" = "true" ]; then
    EXTRAS="$EXTRAS --extra gpu"
fi

echo "🚀 Automating environment for SQL:$SQL_VAL and Vector:$VECTOR__STORE_TYPE"
echo "📂 UV Cache Dir: $UV_CACHE_DIR"

# Function to wait for a port to be open
wait_for_port() {
    local host="$1"
    local port="$2"
    local name="$3"
    if [ -z "$host" ] || [ -z "$port" ]; then
        return
    fi
    echo "⏳ Waiting for $name ($host:$port)..."
    local max_retries=30
    local count=0
    while ! python3 -c "import socket; s = socket.socket(); s.connect(('$host', int('$port')))" 2>/dev/null; do
        sleep 2
        count=$((count + 1))
        if [ $count -ge $max_retries ]; then
            echo "⚠️ Warning: $name ($host:$port) still not reachable after $max_retries retries. Proceeding anyway..."
            break
        fi
    done
    echo "✅ $name is reachable!"
}

# Wait for Redis (always required)
wait_for_port "${REDIS__HOST:-redis}" "${REDIS__PORT:-6379}" "Redis"

# Wait for SQL if not sqlite
if [ "$SQL_VAL" != "sqlite" ] && [ -n "$SQL__HOST" ]; then
    wait_for_port "$SQL__HOST" "${SQL__PORT:-5432}" "Database ($SQL_VAL)"
fi

if [ -n "$EXTRAS" ]; then
    echo "📦 Installing: $EXTRAS"
    uv sync --frozen --no-dev $EXTRAS || { echo "⚠️ Warning: uv sync with EXTRAS failed. Attempting to continue with pre-installed dependencies..."; }
else
    echo "✅ No extras needed, ensuring core dependencies are synchronized."
    uv sync --frozen --no-dev || { echo "⚠️ Warning: uv sync failed. Attempting to continue with pre-installed dependencies..."; }
fi

echo "🔄 Running migrations..."
if uv run --no-dev alembic upgrade head; then
    echo "✅ Migrations completed successfully."
else
    echo "❌ Migration failed! Check your database connection settings."
    # We exit here because the app won't work without migrations
    exit 1
fi

echo "🎬 Starting application on port ${PORT:-5000}..."
exec uv run --no-dev uvicorn main:app --host 0.0.0.0 --port ${PORT:-5000}

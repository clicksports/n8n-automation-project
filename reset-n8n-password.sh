#!/bin/bash

# Reset n8n Password Script
echo "🔐 Resetting n8n Password..."

# Check if n8n is running
if ! docker ps | grep -q "n8n-production"; then
    echo "❌ n8n container is not running. Please start it first with: docker-compose up -d"
    exit 1
fi

# Prompt for new password
echo "Enter new password for admin@n8n.local:"
read -s NEW_PASSWORD

if [ -z "$NEW_PASSWORD" ]; then
    echo "❌ Password cannot be empty"
    exit 1
fi

echo "Confirm password:"
read -s CONFIRM_PASSWORD

if [ "$NEW_PASSWORD" != "$CONFIRM_PASSWORD" ]; then
    echo "❌ Passwords do not match"
    exit 1
fi

echo "🔄 Stopping n8n container..."
docker-compose down

echo "🔄 Generating password hash..."
# Generate bcrypt hash for the password
PASSWORD_HASH=$(node -e "
const bcrypt = require('bcrypt');
const hash = bcrypt.hashSync('$NEW_PASSWORD', 10);
console.log(hash);
" 2>/dev/null)

if [ -z "$PASSWORD_HASH" ]; then
    echo "❌ Failed to generate password hash. Installing bcrypt..."
    # Try with Docker if bcrypt is not available locally
    PASSWORD_HASH=$(docker run --rm node:18-alpine sh -c "
        npm install bcrypt --silent && 
        node -e \"
            const bcrypt = require('bcrypt');
            console.log(bcrypt.hashSync('$NEW_PASSWORD', 10));
        \"
    ")
fi

if [ -z "$PASSWORD_HASH" ]; then
    echo "❌ Failed to generate password hash"
    exit 1
fi

echo "🔄 Updating password in database..."
docker-compose exec postgres psql -U n8n_user -d n8n -c "
UPDATE user_entity
SET password = '$PASSWORD_HASH' 
WHERE email = 'admin@n8n.local';
"

if [ $? -eq 0 ]; then
    echo "✅ Password updated successfully!"
else
    echo "❌ Failed to update password in database"
    exit 1
fi

echo "🚀 Starting n8n container..."
docker-compose up -d

echo ""
echo "🎉 Password reset complete!"
echo "📋 Login credentials:"
echo "   Email: admin@n8n.local"
echo "   Password: [your new password]"
echo "   URL: http://localhost:5678"
echo ""
echo "⏳ Waiting for n8n to start..."
sleep 5

# Check if n8n is healthy
if curl -s http://localhost:5678/healthz | grep -q "ok"; then
    echo "✅ n8n is running and healthy!"
    echo "🌐 You can now login at: http://localhost:5678"
else
    echo "⚠️  n8n is starting up, please wait a moment and try accessing: http://localhost:5678"
fi
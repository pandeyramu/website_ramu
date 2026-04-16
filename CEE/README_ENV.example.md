# Environment Variables Example

Set these in Render or your production host:

- SECRET_KEY=change-this-to-a-long-random-secret
- DJANGO_SECRET_KEY=change-this-to-a-long-random-secret (optional alias if SECRET_KEY is not used)
- DEBUG=False
- DATABASE_URL=postgresql://postgres:password@host:5432/postgres
- EMAIL_HOST=smtp.gmail.com
- EMAIL_PORT=587
- EMAIL_USE_TLS=True
- EMAIL_HOST_USER=your-sender@gmail.com
- EMAIL_HOST_PASSWORD=your-gmail-app-password
- DEFAULT_FROM_EMAIL=your-sender@gmail.com
- USE_MANIFEST_STATICFILES=True

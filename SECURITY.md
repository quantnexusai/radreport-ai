# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in RadReport AI, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email the maintainers directly with details of the vulnerability
3. Include steps to reproduce the issue if possible
4. Allow reasonable time for the issue to be addressed before public disclosure

## Security Best Practices

When deploying RadReport AI:

- Never commit `.env` files or expose API keys
- Use strong, unique passwords for admin access
- Keep dependencies up to date
- Run the application behind a reverse proxy with HTTPS in production
- Regularly review access logs for suspicious activity

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Known Security Considerations

- This application handles medical data; ensure compliance with relevant regulations (HIPAA, etc.)
- API keys for Claude and Supabase should be treated as sensitive credentials
- Admin functionality should be restricted to authorized personnel only

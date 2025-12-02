   - **Recipient Email**: Where submissions should be sent
   - **Description**: Optional notes
4. Copy the generated API key

### Integrating with Your Form

**Simple HTML Form:**
```html
<form action="https://your-app.onrender.com/api/v1/submit/YOUR_API_KEY" 
      method="POST" 
      enctype="multipart/form-data">
  
  <input type="text" name="name" placeholder="Your Name" required>
  <input type="email" name="email" placeholder="Your Email" required>
  <textarea name="message" placeholder="Your Message" required></textarea>
  <input type="file" name="attachment">
  
  <button type="submit">Submit</button>
</form>
```

**With JavaScript (AJAX):**
```javascript
const formData = new FormData();
formData.append('name', 'John Doe');
formData.append('email', 'john@example.com');
formData.append('message', 'Hello!');
formData.append('file', fileInput.files[0]);

fetch('https://your-app.onrender.com/api/v1/submit/YOUR_API_KEY', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    alert('Form submitted successfully!');
  }
});
```

**React Example:**
```jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  
  const response = await fetch(
    'https://your-app.onrender.com/api/v1/submit/YOUR_API_KEY',
    {
      method: 'POST',
      body: formData
    }
  );
  
  const data = await response.json();
  if (data.success) {
    alert('Thank you for your submission!');
  }
};

return (
  <form onSubmit={handleSubmit}>
    <input name="name" required />
    <input name="email" type="email" required />
    <textarea name="message" required />
    <button type="submit">Submit</button>
  </form>
);
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | `production` |
| `SECRET_KEY` | Flask secret key | Required |
| `JWT_SECRET_KEY` | JWT secret key | Required |
| `ADMIN_EMAIL` | Admin user email | `admin@example.com` |
| `ADMIN_PASSWORD` | Admin user password | `changeme123` |
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP username | Required |
| `SMTP_PASSWORD` | SMTP password/app password | Required |
| `SMTP_FROM_EMAIL` | From email address | Required |
| `MAX_FILE_SIZE` | Max file size in bytes | `10485760` (10MB) |
| `ALLOWED_EXTENSIONS` | Allowed file extensions | `pdf,doc,docx,txt,png,jpg,jpeg,gif,zip` |
| `APP_URL` | Application URL | `http://localhost:5000` |

### Email Configuration

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password in `SMTP_PASSWORD`

**SendGrid (Alternative):**
```env
SENDGRID_API_KEY=your-sendgrid-api-key
```

## 🗄️ Database

The application uses SQLite for data persistence:

- **Local Development**: `database.db` in project folder
- **Render (Production)**: `/data/database.db` on persistent disk

### Database Schema

- **users** - Admin users for dashboard access
- **api_keys** - API keys with metadata and usage stats
- **form_submissions** - Submitted form data
- **file_uploads** - Uploaded file metadata and paths

### Backup

To backup your database:
```bash
# Local
cp database.db database_backup.db

# Render (via SSH)
# Download /data/database.db from your persistent disk
```

## 🔒 Security

- JWT-based authentication for dashboard
- Secure password hashing with bcrypt
- API key validation for submissions
- File type and size validation
- SQL injection protection via SQLAlchemy
- XSS protection in templates
- CORS configuration
- Rate limiting ready (configure as needed)

## 📊 API Endpoints

### Public Endpoints

- `POST /api/v1/submit/<api_key>` - Submit form data

### Protected Endpoints (Require JWT)

- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `GET /api/keys` - List API keys
- `POST /api/keys` - Create API key
- `PUT /api/keys/<id>` - Update API key
- `DELETE /api/keys/<id>` - Delete API key
- `GET /api/submissions` - List submissions
- `GET /api/submissions/<id>` - Get submission
- `DELETE /api/submissions/<id>` - Delete submission
- `GET /api/files/<id>/download` - Download file
- `GET /api/stats` - Get statistics

## 🛠️ Troubleshooting

### Database not persisting on Render
- Ensure persistent disk is mounted at `/data`
- Check that `DATABASE_URL` is not set (app auto-detects)

### Emails not sending
- Verify SMTP credentials
- Check spam folder
- Enable "Less secure app access" or use app passwords
- Check application logs for errors

### File uploads failing
- Check `MAX_FILE_SIZE` setting
- Verify file extension is in `ALLOWED_EXTENSIONS`
- Ensure upload directory has write permissions

### Dashboard not loading
- Clear browser cache and localStorage
- Check browser console for errors
- Verify API endpoints are accessible

## 📝 License

MIT License - feel free to use this in your projects!

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Check environment variables
4. Verify database connectivity

## 🎯 Roadmap

- [ ] Email templates customization
- [ ] Webhook support
- [ ] Rate limiting per API key
- [ ] Export submissions to CSV
- [ ] Multi-user support
- [ ] Custom domains for API endpoints
- [ ] Spam protection (reCAPTCHA integration)

---

Built with ❤️ using Flask, SQLite, and modern web technologies.
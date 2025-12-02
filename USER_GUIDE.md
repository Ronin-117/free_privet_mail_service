# 📘 Form Service API - User Guide

Complete guide for using the Form Service API dashboard and integrating it into your projects.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing API Keys](#managing-api-keys)
4. [Viewing Submissions](#viewing-submissions)
5. [Integration Examples](#integration-examples)
6. [Best Practices](#best-practices)
7. [FAQ](#faq)

---

## Getting Started

### Accessing the Dashboard

1. **Navigate to your application URL**
   - Local: `http://localhost:5000`
   - Production: `https://your-app.onrender.com`

2. **Login**
   - Enter your admin email
   - Enter your admin password
   - Click "Sign In"

3. **First Time Setup**
   - You'll see an empty dashboard
   - Create your first API key to get started

---

## Dashboard Overview

### Statistics Cards

The dashboard displays four key metrics:

- **Total API Keys**: Number of API keys you've created
- **Active Keys**: Number of currently active API keys
- **Total Submissions**: All-time form submissions
- **Last 7 Days**: Recent submissions in the past week

### Navigation

- **Dashboard**: Main page with statistics and API key management
- **Submissions**: View all form submissions with filtering options
- **Logout**: Sign out of your account

---

## Managing API Keys

### Creating a New API Key

1. **Click "New API Key"** button on the dashboard

2. **Fill in the form:**
   - **Name** (Required): Give your API key a descriptive name
     - Example: "Contact Form", "Newsletter Signup", "Support Tickets"
   - **Recipient Email** (Required): Email address where submissions will be sent
     - This is where you'll receive form notifications
   - **Description** (Optional): Add notes about this API key
     - Example: "Used on homepage contact form"

3. **Click "Create API Key"**

4. **Copy your API key**
   - The key will be displayed in the table
   - Click "View" to see integration instructions
   - **Important**: Save this key securely!

### Viewing API Key Details

1. **Click "View"** next to any API key

2. **You'll see:**
   - **API Endpoint**: The full URL for form submissions
   - **Example HTML Form**: Ready-to-use code snippet

3. **Copy the endpoint or example code** for your project

### Managing Existing Keys

**Activate/Deactivate:**
- Click "Deactivate" to temporarily disable an API key
- Deactivated keys won't accept new submissions
- Click "Activate" to re-enable it

**Delete:**
- Click "Delete" to permanently remove an API key
- ⚠️ **Warning**: This will also delete all associated submissions!
- You'll be asked to confirm before deletion

---

## Viewing Submissions

### Accessing Submissions

1. Click **"Submissions"** in the navigation menu

2. **Filter submissions:**
   - Use the dropdown to filter by specific API key
   - Select "All API Keys" to see everything

3. **Refresh:**
   - Click the refresh button to reload submissions

### Submission Details

Each submission shows:

- **Date**: When the form was submitted
- **API Key**: Which API key was used
- **Data Preview**: First few fields from the form
- **Files**: Number of attached files (if any)
- **Email Status**: Whether the notification email was sent successfully

### Viewing Full Submission

1. **Click "View"** on any submission

2. **Modal displays:**
   - API key name
   - Submission timestamp
   - IP address of submitter
   - Email delivery status
   - All form fields and values
   - Attached files (with download buttons)

3. **Download files:**
   - Click "Download" next to any file
   - Files are securely stored on the server

4. **Delete submission:**
   - Click "Delete Submission" to remove it
   - This action cannot be undone

### Pagination

- Navigate through pages using the pagination controls
- 20 submissions per page
- Jump to specific pages or use Previous/Next buttons

---

## Integration Examples

### 1. Simple HTML Form

Perfect for static websites:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Contact Us</title>
</head>
<body>
    <h1>Contact Form</h1>
    
    <form action="https://your-app.onrender.com/api/v1/submit/YOUR_API_KEY" 
          method="POST" 
          enctype="multipart/form-data">
        
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required>
        
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required>
        
        <label for="message">Message:</label>
        <textarea id="message" name="message" required></textarea>
        
        <label for="file">Attachment (optional):</label>
        <input type="file" id="file" name="attachment">
        
        <button type="submit">Send Message</button>
    </form>
</body>
</html>
```

**After submission:**
- User will see a success/error page
- You'll receive an email with the form data

### 2. AJAX Form (Better UX)

Stay on the same page after submission:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Contact Us</title>
    <style>
        .success { color: green; }
        .error { color: red; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <h1>Contact Form</h1>
    
    <div id="message" class="hidden"></div>
    
    <form id="contactForm">
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required>
        
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required>
        
        <label for="message">Message:</label>
        <textarea id="message" name="message" required></textarea>
        
        <label for="file">Attachment:</label>
        <input type="file" id="file" name="attachment">
        
        <button type="submit" id="submitBtn">Send Message</button>
    </form>

    <script>
        document.getElementById('contactForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const form = e.target;
            const submitBtn = document.getElementById('submitBtn');
            const messageDiv = document.getElementById('message');
            
            // Disable submit button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
            
            // Prepare form data
            const formData = new FormData(form);
            
            try {
                const response = await fetch(
                    'https://your-app.onrender.com/api/v1/submit/YOUR_API_KEY',
                    {
                        method: 'POST',
                        body: formData
                    }
                );
                
                const data = await response.json();
                
                if (data.success) {
                    messageDiv.className = 'success';
                    messageDiv.textContent = 'Thank you! Your message has been sent.';
                    form.reset();
                } else {
                    messageDiv.className = 'error';
                    messageDiv.textContent = 'Error: ' + data.message;
                }
            } catch (error) {
                messageDiv.className = 'error';
                messageDiv.textContent = 'An error occurred. Please try again.';
            } finally {
                messageDiv.classList.remove('hidden');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Message';
            }
        });
    </script>
</body>
</html>
```

### 3. React Integration

For React applications:

```jsx
import React, { useState } from 'react';

function ContactForm() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: ''
    });
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState({ type: '', message: '' });
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setStatus({ type: '', message: '' });

        const data = new FormData();
        data.append('name', formData.name);
        data.append('email', formData.email);
        data.append('message', formData.message);
        if (file) {
            data.append('attachment', file);
        }

        try {
            const response = await fetch(
                'https://your-app.onrender.com/api/v1/submit/YOUR_API_KEY',
                {
                    method: 'POST',
                    body: data
                }
            );

            const result = await response.json();

            if (result.success) {
                setStatus({
                    type: 'success',
                    message: 'Thank you! Your message has been sent.'
                });
                setFormData({ name: '', email: '', message: '' });
                setFile(null);
            } else {
                setStatus({
                    type: 'error',
                    message: result.message || 'Something went wrong'
                });
            }
        } catch (error) {
            setStatus({
                type: 'error',
                message: 'Failed to send message. Please try again.'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="contact-form">
            <h2>Contact Us</h2>
            
            {status.message && (
                <div className={`alert alert-${status.type}`}>
                    {status.message}
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="name">Name</label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="message">Message</label>
                    <textarea
                        id="message"
                        name="message"
                        value={formData.message}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="file">Attachment (optional)</label>
                    <input
                        type="file"
                        id="file"
                        onChange={handleFileChange}
                    />
                </div>

                <button type="submit" disabled={loading}>
                    {loading ? 'Sending...' : 'Send Message'}
                </button>
            </form>
        </div>
    );
}

export default ContactForm;
```

### 4. WordPress Integration

Add to your WordPress theme:

```php
<?php
// In your theme's functions.php or a custom plugin

function custom_contact_form_shortcode() {
    ob_start();
    ?>
    <form id="custom-contact-form" method="POST">
        <p>
            <label for="name">Name:</label>
            <input type="text" name="name" id="name" required>
        </p>
        <p>
            <label for="email">Email:</label>
            <input type="email" name="email" id="email" required>
        </p>
        <p>
            <label for="message">Message:</label>
            <textarea name="message" id="message" required></textarea>
        </p>
        <p>
            <button type="submit">Send</button>
        </p>
        <div id="form-message"></div>
    </form>

    <script>
    document.getElementById('custom-contact-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const messageDiv = document.getElementById('form-message');
        
        try {
            const response = await fetch(
                'https://your-app.onrender.com/api/v1/submit/YOUR_API_KEY',
                {
                    method: 'POST',
                    body: formData
                }
            );
            
            const data = await response.json();
            
            if (data.success) {
                messageDiv.innerHTML = '<p style="color: green;">Thank you! Message sent.</p>';
                this.reset();
            } else {
                messageDiv.innerHTML = '<p style="color: red;">Error: ' + data.message + '</p>';
            }
        } catch (error) {
            messageDiv.innerHTML = '<p style="color: red;">Failed to send message.</p>';
        }
    });
    </script>
    <?php
    return ob_get_clean();
}
add_shortcode('contact_form', 'custom_contact_form_shortcode');

// Use in posts/pages with: [contact_form]
?>
```

---

## Best Practices

### Security

1. **Keep API keys private**
   - Don't commit API keys to public repositories
   - Use environment variables in your projects
   - Regenerate keys if exposed

2. **Validate on the frontend**
   - Add client-side validation for better UX
   - Server still validates everything

3. **Use HTTPS**
   - Always use HTTPS in production
   - Protects data in transit

### Performance

1. **File size limits**
   - Default: 10MB per file
   - Inform users of file size limits
   - Consider compressing large files

2. **Rate limiting**
   - Don't spam the API
   - Implement debouncing on submit buttons
   - Add loading states

### User Experience

1. **Provide feedback**
   - Show loading states during submission
   - Display success/error messages clearly
   - Reset form after successful submission

2. **Error handling**
   - Catch and display errors gracefully
   - Provide helpful error messages
   - Allow users to retry

3. **Accessibility**
   - Use proper labels for all inputs
   - Add ARIA attributes where needed
   - Ensure keyboard navigation works

---

## FAQ

### Q: Can I use multiple API keys?
**A:** Yes! Create separate API keys for different forms or projects. Each can have its own recipient email.

### Q: What happens if email sending fails?
**A:** The submission is still saved in the database. You can view it in the dashboard, and the error is logged.

### Q: Can I customize the email template?
**A:** Currently, the email template is fixed. Customization is on the roadmap.

### Q: How do I handle spam?
**A:** Consider adding:
- reCAPTCHA to your forms
- Honeypot fields
- Rate limiting on your frontend

### Q: Can I export submissions?
**A:** CSV export is planned for a future update. Currently, you can view and download individual submissions.

### Q: What file types are allowed?
**A:** By default: PDF, DOC, DOCX, TXT, PNG, JPG, JPEG, GIF, ZIP. You can configure this in the `.env` file.

### Q: How long are submissions stored?
**A:** Indefinitely, until you manually delete them. Make sure to backup your database regularly.

### Q: Can I use this for a high-traffic website?
**A:** The free tier on Render has limitations. For high traffic, consider:
- Upgrading to a paid plan
- Implementing rate limiting
- Using a CDN

### Q: How do I change my admin password?
**A:** Currently, update the `ADMIN_PASSWORD` in your environment variables and restart the application. User management features are planned.

### Q: Can I have multiple admin users?
**A:** Not yet. Multi-user support is on the roadmap.

---

## Need Help?

- Check the [README.md](README.md) for setup instructions
- Review the troubleshooting section
- Check application logs for errors
- Ensure all environment variables are set correctly

---

**Happy form building! 🚀**

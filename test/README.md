# Job Application Form - Test Example

This is a professional job application form that demonstrates how to integrate with the Form Service API.

## 🚀 Quick Start

### 1. Get Your API Key
1. Login to your dashboard at `https://nj-mail-services.onrender.com`
2. Click "New API Key"
3. Fill in:
   - **Name**: "Job Applications"
   - **Recipient Email**: Your HR email address
   - **Description**: "Receive job applications from career page"
4. Copy the generated API key

### 2. Update the Form
1. Open `script.js`
2. Find line 7: `const API_KEY = 'YOUR_API_KEY_HERE';`
3. Replace `YOUR_API_KEY_HERE` with your actual API key
4. Save the file

### 3. Test the Form
1. Open `job-application.html` in your browser
2. Fill out the form
3. Submit!
4. Check your email for the application

## 📋 Features

### Form Fields
- **Personal Information**: Name, email, phone, location
- **Position Details**: Role, experience, salary expectations, availability
- **Professional Background**: LinkedIn, portfolio, skills, cover letter
- **Documents**: Resume/CV upload (required), additional documents (optional)
- **Additional Info**: Remote work preference, relocation willingness, referral source

### Technical Features
- ✅ Client-side validation
- ✅ File upload support (PDF, DOC, DOCX)
- ✅ Drag & drop file upload
- ✅ Responsive design (mobile-friendly)
- ✅ Real-time error messages
- ✅ Loading states
- ✅ Success/error notifications
- ✅ Modern, professional UI

## 🎨 Customization

### Change Colors
Edit `style.css` and modify the CSS variables:
```css
:root {
    --primary-color: #2563eb;  /* Main brand color */
    --primary-dark: #1d4ed8;   /* Darker shade */
    --secondary-color: #10b981; /* Accent color */
}
```

### Change Company Name
Edit `job-application.html`:
- Line 17: `<div class="logo">🚀 TechCorp</div>`
- Line 22: `<h1 class="hero-title">Join Our Team</h1>`

### Add/Remove Fields
Edit the form sections in `job-application.html` and ensure the `name` attributes match what you want to receive in the email.

### Change Positions
Edit the position dropdown (lines 73-83 in `job-application.html`):
```html
<option value="Your Position">Your Position</option>
```

## 📧 Email Notifications

When someone submits the form, you'll receive an email with:
- All form field data
- Attached resume/CV
- Additional documents (if provided)
- Submission timestamp
- Applicant's IP address

## 🔒 Security

- File size limited to 5MB
- Only PDF, DOC, DOCX files allowed
- Email validation
- Phone number validation
- XSS protection via FormData API
- HTTPS encryption (when deployed)

## 🌐 Deployment

### Option 1: Static Hosting
Upload these files to any static hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3

### Option 2: Add to Existing Website
Copy the three files to your website:
- `job-application.html` → Add to your careers page
- `style.css` → Include in your CSS
- `script.js` → Include in your JS (remember to update API_KEY!)

### Option 3: Embed in WordPress
1. Create a new page
2. Add a Custom HTML block
3. Paste the HTML from `job-application.html`
4. Add the CSS to your theme's custom CSS
5. Add the JS to your theme's custom JS

## 📊 Viewing Submissions

1. Login to dashboard: `https://nj-mail-services.onrender.com`
2. Click "Submissions" in the navigation
3. View all applications with:
   - Applicant details
   - Submission date
   - Download attachments
   - Email delivery status

## 🐛 Troubleshooting

### "Please update the API_KEY" error
- You forgot to replace `YOUR_API_KEY_HERE` in `script.js`
- Get your API key from the dashboard

### Form submits but no email received
- Check spam folder
- Verify SMTP settings in dashboard
- Check submission in dashboard to see email status

### File upload fails
- File might be too large (max 5MB)
- Wrong file type (only PDF, DOC, DOCX allowed)
- Check browser console for errors

### CORS errors
- Make sure you're using the correct API endpoint
- API should be `https://nj-mail-services.onrender.com/api/v1/submit/YOUR_API_KEY`

## 💡 Tips

1. **Test First**: Submit a test application to verify everything works
2. **Check Email**: Make sure you receive the notification email
3. **Mobile Test**: Test on mobile devices for responsive design
4. **Customize**: Adjust colors, fields, and text to match your brand
5. **Monitor**: Check dashboard regularly for new applications

## 🎯 Next Steps

- Customize the form fields for your needs
- Update branding (logo, colors, company name)
- Add Google Analytics tracking
- Integrate with your ATS (Applicant Tracking System)
- Set up auto-responder emails

---

**Need Help?** Check the main [USER_GUIDE.md](../USER_GUIDE.md) for more integration examples and best practices.

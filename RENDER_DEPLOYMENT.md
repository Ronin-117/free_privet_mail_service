# 🚀 Render Deployment Guide (Free Tier with PostgreSQL)

Complete step-by-step guide to deploy your Form Service API to Render using their **free PostgreSQL database**.

## 📋 Prerequisites

- GitHub account
- Render account (sign up at [render.com](https://render.com))
- Your code pushed to GitHub: `https://github.com/Ronin-117/free_privet_mail_service`
- Gmail account for SMTP (or other email service)

---

## Step 1: Generate Secret Keys

Before deploying, generate two secret keys. Run these commands locally:

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY  
python -c "import secrets; print(secrets.token_hex(32))"
```

**Save these keys** - you'll need them in Step 5!

---

## Step 2: Setup Gmail App Password

1. Go to your [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Factor Authentication** (if not already enabled)
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select app: **Mail**
5. Select device: **Other** (type "Render Form Service")
6. Click **Generate**
7. **Copy the 16-character password** (no spaces)

---

## Step 3: Create PostgreSQL Database on Render

1. **Login to Render Dashboard**
   - Go to [dashboard.render.com](https://dashboard.render.com)

2. **Create New PostgreSQL Database**
   - Click **"New +"** → **"PostgreSQL"**

3. **Configure Database:**
   - **Name**: `formservice-db` (or your preferred name)
   - **Database**: `formservice` (auto-filled)
   - **User**: `formservice` (auto-filled)
   - **Region**: Choose same as your web service will be
   - **PostgreSQL Version**: 16 (latest)
   - **Instance Type**: **Free**

4. **Click "Create Database"**
   - Wait 1-2 minutes for database to be created
   - Database will show as "Available"

5. **Copy Database URL**
   - On the database page, find **"Internal Database URL"**
   - Click the **copy icon** to copy the full URL
   - It looks like: `postgres://user:password@host/database`
   - **Save this URL** - you'll need it in Step 5!

---

## Step 4: Create Web Service on Render

1. **From Render Dashboard:**
   - Click **"New +"** → **"Web Service"**

2. **Connect Repository:**
   - Click **"Connect a repository"**
   - If first time: Authorize Render to access GitHub
   - Find: `Ronin-117/free_privet_mail_service`
   - Click **"Connect"**

3. **Configure Web Service:**

   | Setting | Value |
   |---------|-------|
   | **Name** | `form-service-api` (or your choice) |
   | **Region** | **Same as database** (important!) |
   | **Branch** | `main` |
   | **Root Directory** | Leave empty |
   | **Environment** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn app:app` |
   | **Instance Type** | **Free** |

4. **Don't click "Create Web Service" yet!** - Continue to Step 5

---

## Step 5: Set Environment Variables

**BEFORE deploying**, scroll to **"Environment Variables"** section and add these:

### Required Variables:

```env
FLASK_ENV=production
SECRET_KEY=<paste-your-secret-key-from-step-1>
JWT_SECRET_KEY=<paste-your-jwt-secret-from-step-1>
DATABASE_URL=<paste-internal-database-url-from-step-3>
ADMIN_EMAIL=your-email@example.com
ADMIN_PASSWORD=YourStrongPassword123!
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<paste-gmail-app-password-from-step-2>
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Form Service
APP_URL=https://form-service-api.onrender.com
```

### How to Add Each Variable:

1. Click **"Add Environment Variable"**
2. Enter **Key** (e.g., `FLASK_ENV`)
3. Enter **Value** (e.g., `production`)
4. Repeat for all variables above

### Important Notes:

- **DATABASE_URL**: Use the **Internal Database URL** from Step 3
- **SECRET_KEY**: From Step 1 (first command)
- **JWT_SECRET_KEY**: From Step 1 (second command)
- **SMTP_PASSWORD**: Gmail App Password from Step 2 (16 characters, no spaces)
- **APP_URL**: Replace `form-service-api` with your actual service name

---

## Step 6: Deploy!

1. **Click "Create Web Service"** at the bottom

2. **Watch the deployment:**
   - Render will clone your repo
   - Install dependencies (including PostgreSQL driver)
   - Start the application
   - Takes 2-3 minutes

3. **Check the logs** for:
   ```
   ==> Building...
   ==> Installing dependencies...
   ==> Starting service...
   * Running on http://0.0.0.0:10000
   ```

4. **Wait for "Your service is live!"**

---

## Step 7: Verify Deployment

1. **Click your service URL** at the top:
   - `https://your-service-name.onrender.com`

2. **You should see:**
   - Login page with clean design
   - No errors

3. **Login:**
   - Email: Your `ADMIN_EMAIL`
   - Password: Your `ADMIN_PASSWORD`

4. **Dashboard should show:**
   - Statistics (all zeros initially)
   - "New API Key" button
   - Clean interface

---

## Step 8: Create Your First API Key

1. Click **"New API Key"**
2. Fill in:
   - **Name**: "Test Contact Form"
   - **Recipient Email**: Your email
   - **Description**: "Testing deployment"
3. Click **"Create API Key"**
4. **Copy the generated API key**

---

## Step 9: Test Form Submission

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Form</title>
</head>
<body>
    <h1>Test Form Submission</h1>
    <form action="https://YOUR-SERVICE-NAME.onrender.com/api/v1/submit/YOUR-API-KEY" 
          method="POST">
        <label>Name:</label>
        <input type="text" name="name" required><br><br>
        
        <label>Email:</label>
        <input type="email" name="email" required><br><br>
        
        <label>Message:</label>
        <textarea name="message" required></textarea><br><br>
        
        <button type="submit">Submit</button>
    </form>
</body>
</html>
```

Replace:
- `YOUR-SERVICE-NAME` with your actual Render service name
- `YOUR-API-KEY` with the key from Step 8

**Submit the form** and check:
- ✅ Form submits successfully
- ✅ You receive an email
- ✅ Submission appears in dashboard

---

## 🎉 Success!

Your Form Service API is now:
- ✅ Running on Render (free tier)
- ✅ Using PostgreSQL database (free tier)
- ✅ Sending emails via Gmail
- ✅ Fully functional and persistent
- ✅ Accessible via HTTPS

---

## 📊 Managing Your Deployment

### View Logs
1. Render Dashboard → Your Service
2. Click **"Logs"** tab
3. See real-time application logs

### Restart Service
1. Go to **"Manual Deploy"**
2. Click **"Deploy latest commit"**

### Update Environment Variables
1. Go to **"Environment"** tab
2. Edit any variable
3. Service auto-restarts

### Monitor Database
1. Render Dashboard → Your Database
2. View **"Metrics"** for usage
3. Check **"Info"** for connection details

---

## ⚠️ Important Notes

### File Uploads
- Files are stored in `/tmp/uploads` on Render
- **Files are ephemeral** - they're deleted when service restarts
- For permanent file storage, consider:
  - AWS S3 (free tier available)
  - Cloudinary (free tier)
  - Or just rely on email attachments

### Database Backups
- Free PostgreSQL includes automatic backups
- Download backups from database dashboard
- Backups retained for 7 days

### Service Limitations (Free Tier)
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- 750 hours/month (enough for one service)
- Upgrade to paid plan for always-on service

---

## 🔧 Troubleshooting

### "Application failed to start"
**Check:**
- All environment variables are set
- DATABASE_URL is correct
- No typos in variable names

**Solution:** Review logs for specific error

### "Database connection failed"
**Check:**
- Web service and database are in same region
- DATABASE_URL is the **Internal** URL (not External)
- Database status is "Available"

**Solution:** Copy DATABASE_URL again from database page

### "Emails not sending"
**Check:**
- Gmail App Password is correct (16 chars, no spaces)
- SMTP_USERNAME and SMTP_FROM_EMAIL match
- Check spam folder

**Solution:** Review logs for SMTP errors

### "Can't login to dashboard"
**Check:**
- ADMIN_EMAIL and ADMIN_PASSWORD are set correctly
- No extra spaces in values

**Solution:** Update environment variables and redeploy

---

## 💡 Pro Tips

1. **Same Region**: Always create database and web service in same region for best performance

2. **Auto-Deploy**: Render auto-deploys when you push to GitHub main branch

3. **Custom Domain**: Add custom domain in service settings (free on paid plans)

4. **Monitoring**: Set up email alerts in Render for service failures

5. **Database Scaling**: Upgrade database plan if you exceed free tier limits

---

## 📈 Next Steps

1. ✅ Test thoroughly with different forms
2. ✅ Integrate into your projects
3. ✅ Monitor submissions in dashboard
4. ✅ Share USER_GUIDE.md with your team
5. ✅ Consider upgrading for production use

---

## 🆘 Need Help?

- Check [Render Documentation](https://render.com/docs)
- Review application logs
- Check database metrics
- Verify all environment variables

---

**Congratulations! Your Form Service API is live! 🚀**

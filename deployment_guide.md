# 🚀 Deployment Guide: Bill Genius Operations

This guide provides the technical blueprint for deploying the Bill Genius production environment. It follows the **Principle of Least Privilege** using Google Cloud Service Account Impersonation.

---

## 🔐 1. Service Account & IAM Protocol

The system uses **Keyless Authentication**. The Cloud Run service identity "impersonates" a highly-privileged worker account only when needed for Sheet operations.

### Step A: Create the Worker Service Account
This account handles the actual data writes.
1. Go to **IAM & Admin > Service Accounts**.
2. Create: `prince-worker@soulmate-tours.iam.gserviceaccount.com`.
3. Do **NOT** download a JSON key.

### Step B: Enable Google APIs
Ensure the following are enabled in the [API Library](https://console.cloud.google.com/apis/library):
- [x] Google Sheets API
- [x] Google Drive API (required for gspread)
- [x] Cloud Run Admin API

### Step C: Configure Impersonation Roles
1. Identify the **Default Compute Service Account** (e.g., `123456789-compute@developer.gserviceaccount.com`). This is the identity Cloud Run uses by default.
2. Go to the worker service account (`prince-worker`) created in Step A.
3. Click **Permissions** > **Grant Access**.
4. Add the Default Compute Service Account as the principal.
5. Grant the role: **Service Account Token Creator**.

### Step D: Share the Google Sheet
1. Open your Google Sheet.
2. Click **Share**.
3. Add `prince-worker@soulmate-tours.iam.gserviceaccount.com` as **Editor**.

---

## 🐳 2. Backend Deployment (Cloud Run)

The backend is built as a container and deployed to Cloud Run.

### Build and Push Image
```powershell
# Navigate to backend-extraction/
gcloud builds submit --tag asia-south1-docker.pkg.dev/soulmate-tours/prince-images/bill-extraction-backend:latest .
```

### Deploy Service
```powershell
gcloud run deploy bill-extraction-backend `
    --image asia-south1-docker.pkg.dev/soulmate-tours/prince-images/bill-extraction-backend:latest `
    --platform managed `
    --region asia-south1 `
    --allow-unauthenticated `
    --memory 4Gi `
    --cpu 2 `
    --timeout 300 `
    --set-env-vars="GOOGLE_SHEET_ID=1ESpXPrhesyxgD9WELxtf0es9WU742iZXPlnXrg-YuE0,IMPERSONATED_SERVICE_ACCOUNT=prince-worker@soulmate-tours.iam.gserviceaccount.com"
```

> [!TIP]
> **Performance**: 4GiB RAM is recommended to handle the `Docling` parsing engine which performs heavy layout analysis.

---

## 🌐 3. Frontend Deployment (Firebase)

The frontend is a static Next.js application.

### Build Process
1. Update `frontend/.env.local`:
   ```text
   NEXT_PUBLIC_BACKEND_URL=https://your-cloud-run-url-here.a.run.app
   ```
2. Build the static site:
   ```bash
   cd frontend
   npm run build
   ```

### Firebase Deploy
```bash
npx firebase-tools deploy --project soulmate-tours --only hosting
```

---

## 🛠️ 4. Verification & Maintenance

### Connectivity Checklist
- [ ] Backend is reachable (check `/docs` for Swagger).
- [ ] Service Account has `Service Account Token Creator` on the target.
- [ ] Sheet ID is correct and shared with the worker email.

### Log Monitoring
To view live production logs:
```bash
gcloud logs read --service bill-extraction-backend --region asia-south1 --limit 50
```

---

> [!CAUTION]
> **Security Audit**: Regularly review the "Service Account Token Creator" permissions. Never hardcode keys in the Dockerfile.


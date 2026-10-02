# AWS S3 Static Website Hosting Guide

This guide walks you through deploying the **AWS Certified Solutions Architect – Associate (SAA-C03) Exam Practice Application** to **Amazon S3** as a 100% serverless, zero-maintenance static website.

---

## 🏛️ Architecture Overview

```
                      +-----------------------------------+
                      |   Amazon S3 (Static Web Hosting)  |
                      |   - index.html                    |
                      |   - assets/*.js, *.css            |
                      |   - questions.json (684 questions)|
                      +-----------------+-----------------+
                                        | HTTP GET
                                        v
                            +-----------------------+
                            | User's Web Browser    |
                            |  - React SPA Engine   |
                            |  - Local JSON Cache   |
                            +-----------+-----------+
                                        |
                             Read/Write | (Offline & Persistent)
                                        v
                            +-----------------------+
                            | Browser LocalStorage  |
                            |  - Last Left-Off      |
                            |  - Question Attempts  |
                            |  - Highlights / Flags |
                            |  - Performance Stats  |
                            +-----------------------+
```

### Key Highlights
- **100% Serverless**: No EC2 instances, containers, or Node.js servers to manage.
- **Client-Side JSON Database**: All 684 questions with option-by-option architectural evaluations are loaded from `questions.json`.
- **Persistent User Progress**: Checklist attempts, scores, bookmarks/highlights, and your last left-off position are saved directly in browser `localStorage`.
- **Near-Zero Cost**: S3 storage and data transfer for this app costs less than **$0.01 - $0.05 / month** (well within the AWS Free Tier).

---

## 📋 Prerequisites

1. **AWS CLI** installed and configured:
   ```bash
   aws configure
   ```
2. **Node.js** (v18+) and **npm**:
   ```bash
   node -v
   npm -v
   ```

---

## 🚀 Step-by-Step Deployment to S3

### Step 1: Build the Static Application Bundle

Navigate to the `client/` directory and run the production build:

```bash
cd client
npm install
npm run build
```

This compiles the React application and bundles `questions.json` into the `client/dist/` directory:
```
client/dist/
├── assets/
│   ├── index-*.js
│   └── index-*.css
├── index.html
└── questions.json
```

---

### Step 2: Choose a Unique S3 Bucket Name

Choose a globally unique name for your S3 bucket (e.g., `aws-saa-c03-exam-practice-<your-name>`).

Set an environment variable for convenience:
```bash
export BUCKET_NAME="aws-saa-c03-exam-practice-$(whoami)"
export AWS_REGION="us-east-1"
```

---

### Step 3: Create the S3 Bucket

Create the bucket in your desired AWS region:

```bash
aws s3 mb s3://$BUCKET_NAME --region $AWS_REGION
```

---

### Step 4: Disable "Block Public Access"

By default, Amazon S3 blocks public access. Since this is a public static website, disable these blocks:

```bash
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

---

### Step 5: Enable Static Website Hosting

Configure the bucket to serve `index.html` as the index and error document (required for Single Page Application routing):

```bash
aws s3 website s3://$BUCKET_NAME \
  --index-document index.html \
  --error-document index.html
```

---

### Step 6: Attach a Public Read Bucket Policy

Create a bucket policy allowing anonymous users to read website objects:

```bash
cat <<EOF > /tmp/s3-website-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket $BUCKET_NAME \
  --policy file:///tmp/s3-website-policy.json
```

---

### Step 7: Upload the Built Application to S3

Sync the contents of `client/dist/` to the root of your S3 bucket:

```bash
aws s3 sync client/dist/ s3://$BUCKET_NAME/ --delete
```

---

### Step 8: Access Your Website

Your website is now live! The website endpoint follows this format:

```
http://<BUCKET_NAME>.s3-website-<AWS_REGION>.amazonaws.com
```

Example:
```
http://aws-saa-c03-exam-practice-student.s3-website-us-east-1.amazonaws.com
```

---

## 🔒 Production Enhancement: HTTPS & Global Caching with CloudFront

Standard S3 website endpoints only support plain HTTP. For an AWS Certified Solutions Architect best-practice deployment, distribute it via **Amazon CloudFront**:

1. **Create CloudFront Distribution**:
   - Origin Domain: `<BUCKET_NAME>.s3-website-<AWS_REGION>.amazonaws.com` (or S3 REST endpoint with Origin Access Control).
   - Viewer Protocol Policy: `Redirect HTTP to HTTPS`.
   - Default Root Object: `index.html`.
2. **Benefits**:
   - ⚡ **Global Edge Caching**: Fast loading times worldwide via AWS CloudFront Point of Presence (PoP) edge locations.
   - 🔐 **SSL / TLS Encryption**: Secure HTTPS connection using AWS Certificate Manager (ACM).
   - 🛡️ **DDoS Protection**: Free protection via AWS Shield Standard.

---

## 💾 How Updates & State Persistence Work on S3

- **Attempts & Checklists**: When you submit an answer, the attempt record (`selected`, `isCorrect`, `timestamp`) is written immediately to your browser's `localStorage`.
- **Highlights & Bookmarks**: Toggling highlights updates the `highlights` array in `localStorage`.
- **Resume Left-Off**: When you reopen or refresh the website on your browser, it automatically reads your `lastLeftOff` question ID and resumes where you stopped.
- **Data Safety**: Your progress persists across tab closures, browser restarts, and device reboots.

---

## 🔄 Updating Questions or Code in the Future

Whenever you modify code or update questions:

```bash
# 1. Rebuild the frontend
cd client && npm run build && cd ..

# 2. Sync changes to S3
aws s3 sync client/dist/ s3://$BUCKET_NAME/ --delete

# 3. (Optional if using CloudFront) Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id <DISTRIBUTION_ID> --paths "/*"
```

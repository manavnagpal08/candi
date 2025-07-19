<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ScreenerPro Certificate (Landscape)</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');

    body {
      margin: 0;
      padding: 0;
      background: #f4f6f8;
      font-family: 'Inter', sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }

    .certificate {
      background-color: #ffffff;
      width: 1120px;
      height: 790px;
      padding: 50px 70px;
      border: 10px solid #00bcd4;
      box-shadow: 0 0 20px rgba(0,0,0,0.1);
      box-sizing: border-box;
      text-align: center;
      position: relative;
    }

    .certificate img.logo {
      width: 200px;
      margin-bottom: 20px;
    }

    h1 {
      font-family: 'Playfair Display', serif;
      font-size: 36px;
      color: #003049;
      margin: 10px 0;
    }

    h2 {
      font-size: 20px;
      margin-bottom: 25px;
      color: #007c91;
    }

    .subtext {
      font-size: 18px;
      color: #333;
      margin-bottom: 10px;
    }

    .candidate-name {
      font-family: 'Playfair Display', serif;
      font-size: 32px;
      color: #00bcd4;
      font-weight: bold;
      margin: 10px 0;
      text-decoration: underline;
    }

    .score-rank {
      display: inline-block;
      font-size: 18px;
      font-weight: 600;
      background: #e0f7fa;
      color: #2e7d32;
      padding: 8px 24px;
      border-radius: 8px;
      margin: 20px 0;
    }

    .description {
      font-size: 16px;
      color: #555;
      margin: 20px auto;
      line-height: 1.5;
      max-width: 900px;
    }

    .footer-details {
      font-size: 13px;
      color: #666;
      margin-top: 20px;
    }

    .signature-block {
      margin-top: 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .signature img {
      width: 150px;
      border-bottom: 1px solid #ccc;
      padding-bottom: 5px;
    }

    .signature .title {
      font-size: 13px;
      color: #777;
      margin-top: 5px;
      text-align: left;
    }

    .stamp {
      font-size: 42px;
      color: #4caf50;
      margin-right: 10px;
    }

    @media print {
      @page {
        size: landscape;
        margin: 0;
      }

      body {
        background: #ffffff;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }

      .certificate {
        box-shadow: none;
      }
    }
  </style>
</head>
<body>
  <div class="certificate">
    <img class="logo" src="https://raw.githubusercontent.com/manavnagpal08/yg/main/logo.png" alt="ScreenerPro Logo" />

    <h1>CERTIFICATE OF EXCELLENCE</h1>
    <h2>Presented by ScreenerPro</h2>

    <div class="subtext">This is to certify that</div>
    <div class="candidate-name">{{CANDIDATE_NAME}}</div>

    <div class="subtext">has successfully completed the AI-powered resume screening process</div>

    <div class="score-rank">Score: {{SCORE}}% | Rank: {{CERTIFICATE_RANK}}</div>

    <div class="description">
      This certificate acknowledges the candidate’s exceptional qualifications, industry-aligned skills, and readiness to contribute effectively in challenging roles. Evaluated and validated by ScreenerPro’s advanced screening engine.
    </div>

    <div class="footer-details">
      Awarded on: {{DATE_SCREENED}}<br>
      Certificate ID: {{CERTIFICATE_ID}}
    </div>

    <div class="signature-block">
      <div class="signature">
        <img src="https://see.fontimg.com/api/rf5/DOLnW/ZTAyODAyZDM3MWUyNDVjNjg0ZWRmYTRjMjNlOTE3ODUub3Rm/U2NyZWVuZXJQcm8/autography.png?r=fs&h=81&w=1250&fg=000000&bg=FFFFFF&tb=1&s=65" alt="Signature" />
        <div class="title">Founder & Product Head, ScreenerPro</div>
      </div>
      <div class="stamp">✔️</div>
    </div>
  </div>
</body>
</html>


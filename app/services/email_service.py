from app.core.config import settings
import resend
from datetime import datetime, timezone

async def send_otp_email(email: str, otp: str) -> None:
    resend.api_key = settings.resend_api_key
    params: resend.Emails.SendParams = {
        "from": settings.resend_from_email,
        "to": email,
        "subject": f"Login Verification - {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}",
        "html": f"""<!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            </head>
                            <body style="margin:0;padding:0;background-color:#f4f6f9;font-family:Arial,sans-serif;">
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9;padding:40px 0;">
                                <tr>
                                    <td align="center">
                                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;">

                                        <!-- Logo -->
                                        <tr>
                                        <td align="center" style="padding:32px 40px 16px;">
                                            <img src="https://res.cloudinary.com/dn7rtpgku/image/upload/v1782319119/astrynox-logo_w8unlo.png" alt="Astrynox AI" height="40" />
                                        </td>
                                        </tr>

                                        <!-- Heading -->
                                        <tr>
                                        <td align="center" style="padding:0 40px 8px;">
                                            <h1 style="margin:0;font-size:24px;color:#1a1a2e;font-weight:700;">Login Verification</h1>
                                        </td>
                                        </tr>

                                        <!-- Subtext -->
                                        <tr>
                                        <td align="center" style="padding:8px 40px 24px;">
                                            <p style="margin:0;font-size:15px;color:#555555;">Your verification code</p>
                                        </td>
                                        </tr>

                                        <!-- OTP Code -->
                                        <tr>
                                        <td align="center" style="padding:0 40px 24px;">
                                            <h2 style="margin:0;font-size:42px;font-weight:800;letter-spacing:12px;color:#2563eb;">{otp}</h2>
                                        </td>
                                        </tr>

                                        <!-- Info text -->
                                        <tr>
                                        <td style="padding:0 40px 32px;">
                                            <p style="margin:0 0 12px;font-size:14px;color:#555555;line-height:1.6;">
                                            The verification code will be valid for <strong>5 minutes</strong>. Please do not share this code with anyone.
                                            </p>
                                            <p style="margin:0;font-size:14px;color:#555555;line-height:1.6;">
                                            Don't recognize this activity? Please <a href="#" style="color:#2563eb;">reset your password</a> and contact
                            customer support immediately.
                                            </p>
                                        </td>
                                        </tr>

                                        <!-- Divider -->
                                        <tr>
                                        <td style="padding:0 40px;">
                                            <hr style="border:none;border-top:2px solid #2563eb;margin:0;" />
                                        </td>
                                        </tr>

                                        <!-- Disclaimer -->
                                        <tr>
                                        <td style="padding:20px 40px 8px;">
                                            <p style="margin:0;font-size:11px;color:#999999;line-height:1.6;">
                                            This is an automated message — please do not reply. This email was sent because a login attempt was made on your
                            Astrynox AI account. If you did not request this, you can safely ignore this email.
                                            </p>
                                        </td>
                                        </tr>

                                        <!-- Footer -->
                                        <tr>
                                        <td align="center" style="padding:8px 40px 32px;">
                                            <p style="margin:0;font-size:11px;color:#bbbbbb;">
                                            &copy; 2026 Astrynox AI. All rights reserved.
                                            </p>
                                        </td>
                                        </tr>

                                    </table>
                                    </td>
                                </tr>
                                </table>
                            </body>
                            </html>

                        """,
    }
    resend.Emails.send(params)
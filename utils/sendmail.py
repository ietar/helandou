# from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

__time__ = "2025年2月23日15:25:30"


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send(_from=r'ietarmailtest@163.com',
         password=r'WDd3EFqK7CyCND8c',
         to=r'410473517@qq.com',
         message=r'nothing',
         title=r'来自smtp的问候......',
         yourname=r'ietar',
         addressee=r'hello?',
         subtype="plain",
         debuglv=0):
    """
     directly send an email
    :param _from:
    :param password:
    :param to:
    :param message:
    :param title:
    :param yourname:
    :param addressee:
    :param subtype: "plain", "html"
    :param debuglv:
    :return:
    """

    if not isinstance(debuglv, int):
        raise ValueError('debuglv should be 0 or 1')

    smtp_server = r'smtp.' + _from.split(r'@')[1]

    msg = MIMEText(message, subtype, 'utf-8')
    msg['From'] = _format_addr('{} <{}>'.format(yourname, _from))
    msg['To'] = _format_addr('{} <{}>'.format(addressee, to))
    msg['Subject'] = Header(title, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(debuglv)
    server.login(_from, password)
    server.sendmail(_from, [to], msg.as_string())
    server.quit()


def send_email_code_for_register(to: str, code: str):
    content = f"""
<html>
  <head>
    <meta charset="utf-8">
    <style>
      /* 移动端优化 */
      @media screen and (max-width: 600px) {{
        .container {{ width: 95% !important; }}
        .logo {{ width: 120px !important; }}
      }}
    </style>
  </head>
  <body style="margin:0; padding:20px 0; background:#f5f7fa;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
      <tr>
        <td align="center">
          <!-- 主容器 -->
          <div class="container" style="width:580px; margin:0 auto; background:#fff; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1);">
            <!-- 头部 -->
            <table width="100%" border="0" cellspacing="0" cellpadding="20">
              <tr>
                <td align="center" style="border-bottom:1px solid #eee;">
                  <img src="LOGO_URL" class="logo" alt="荷兰豆" style="width:160px; height:auto;">
                </td>
              </tr>
            </table>

            <!-- 内容区 -->
            <div style="padding:30px 40px;">
              <h1 style="color:#2d3748; font-size:24px; margin:0 0 25px;">🛡️ 您的安全验证码</h1>
              
              <p style="color:#4a5568; line-height:1.6; margin:0 0 20px;">
                感谢您注册荷兰豆！请使用以下验证码完成邮箱验证：
              </p>

              <div style="background:#f8fafc; padding:20px; border-radius:6px; text-align:center; margin:25px 0;">
                <div style="font-size:32px; letter-spacing:2px; color:#3b82f6; font-weight:600;">
                  {code}
                </div>
                <div style="color:#718096; font-size:14px; margin-top:10px;">
                  （10分钟内有效）
                </div>
              </div>

              <p style="color:#718096; font-size:14px; line-height:1.6;">
                ⚠️ 安全提示：该验证码仅用于荷兰豆账号验证，请勿向任何人提供此代码。<br>
                🌱 如非本人操作，请忽略本邮件或联系客服：support@helandou.com
              </p>
            </div>

            <!-- 页脚 -->
            <div style="background:#f8fafc; padding:20px; text-align:center; border-radius:0 0 8px 8px;">
              <p style="color:#718096; font-size:12px; margin:5px 0;">
                荷兰豆 | 让知识生根发芽 🌱
                <br>
                <a href="#" style="color:#3b82f6; text-decoration:none;">隐私政策</a> | 
                <a href="#" style="color:#3b82f6; text-decoration:none;">用户协议</a>
              </p>
            </div>
          </div>
        </td>
      </tr>
    </table>
  </body>
</html>

"""
    # send(to=to, message=con2, subtype="html", title="注册验证码")
    send(to=to, message=content, subtype="html", title="【荷兰豆】邮箱验证通知 - 请完成注册", yourname="荷兰豆")


def send_email_code_for_reset_password(to: str, username: str, url: str, ip: str, ttl: int):
    content = f"""
<html>
  <head>
    <meta charset="utf-8">
    <style>
      /* 移动端优化 */
      @media screen and (max-width: 600px) {{
        .container {{ width: 95% !important; }}
        .logo {{ width: 120px !important; }}
      }}
    </style>
  </head>
  <body style="margin:0; padding:20px 0; background:#f5f7fa;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
      <tr>
        <td align="center">
          <!-- 主容器 -->
          <div class="container" style="width:580px; margin:0 auto; background:#fff; border-radius:8px; box-shadow:0 2px 10px rgba(0,0,0,0.1);">
            <!-- 头部 -->
            <table width="100%" border="0" cellspacing="0" cellpadding="20">
              <tr>
                <td align="center" style="border-bottom:1px solid #eee;">
                  <img src="LOGO_URL" class="logo" alt="荷兰豆" style="width:160px; height:auto;">
                </td>
              </tr>
            </table>

            <!-- 内容区 -->
            <div style="padding:30px 40px;">
            <h1 style="color:#2d3748; font-size:24px; margin:0 0 25px;">🛡️ [重要] 您的荷兰豆账户密码重置指引</h1>

            <p style="color:#4a5568; line-height:1.6; margin:0 0 20px;">
            尊敬的{username}：
            
            您好！本邮件由【荷兰豆】账户安全系统自动发出，为保障您的账户安全，请仔细阅读以下内容。</p>
            <p style="color:#4a5568; line-height:1.6; margin:0 0 20px;">安全提示
            ⚠️ 若非本人操作：
               • 您近期未申请过密码重置？请立即忽略本邮件
               • 怀疑账户存在异常？请联系客服：support@helandou.com</p
        
            <p style="color:#4a5568; line-height:1.6; margin:0 0 20px;">
            ✅ 安全操作保障：
               • 本链接有效期：{ttl}分钟（北京时间）
               • 请求来源IP：{ip}（如非您常用设备，请提高警惕）</p>
            
            ><h2>密码重置指引</h2>
            <p style="color:#4a5568; line-height:1.6; margin:0 0 20px;">
            1. 点击下方安全链接进入重置页面：
               🔗 <a href="{url}" style="word-break: break-all;">{url}</a></p>
        
            <p style="color:#4a5568; line-height:1.6; margin:0 0 20px;">
            2. 在打开的页面中输入新密码（建议组合使用字母+数字+符号）</p>
        
            <p style="color:#4a5568; line-height:1.6; margin:0 0 20px;">
            3. 完成验证后，即可使用新密码登录</p>
        
            <p style="color:#4a5568; line-height:1.6; margin:0 0 20px;">
            无法点击链接？
            请手动复制以下地址到浏览器地址栏：
            {url}
            </p> 
            <p style="color:#718096; font-size:14px; line-height:1.6;">
            ⚠️ 安全提示：该链接仅用于荷兰豆账号密码重置，请勿向任何人提供此链接。<br>
            🌱 如非本人操作，请忽略本邮件或联系客服：support@helandou.com
            </p>
            </div>

            <!-- 页脚 -->
            <div style="background:#f8fafc; padding:20px; text-align:center; border-radius:0 0 8px 8px;">
              <p style="color:#718096; font-size:12px; margin:5px 0;">
                荷兰豆 | 让知识生根发芽 🌱
                <br>
                <a href="#" style="color:#3b82f6; text-decoration:none;">隐私政策</a> | 
                <a href="#" style="color:#3b82f6; text-decoration:none;">用户协议</a>
              </p>
            </div>
          </div>
        </td>
      </tr>
    </table>
  </body>
</html>

"""
    # send(to=to, message=con2, subtype="html", title="注册验证码")
    send(to=to, message=content, subtype="html", title="【荷兰豆】- 重置密码", yourname="荷兰豆")


if __name__ == '__main__':
    # send_email_code_password(to="410473517@qq.com", code="122223")
    pass


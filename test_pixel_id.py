from app import create_app
from models import db, SiteSetting
from flask import url_for

app = create_app()
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
client = app.test_client()

with app.app_context():
    from models import User
    # create test user
    u = User(username='admin_test', email='admin@test.com', role='admin')
    u.set_password('test')
    db.session.add(u)
    db.session.commit()

    # login
    client.post('/admin/login', data={'username': 'admin_test', 'password': 'test'})

    # try posting full snippet
    snippet = """<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '1626031432043896');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=1626031432043896&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->"""

    resp = client.post('/admin/settings/home', data={'meta_pixel_id': snippet}, follow_redirects=True)

    # check db
    setting = SiteSetting.query.filter_by(key='meta_pixel_id').first()
    assert setting.value == '1626031432043896', f"Failed! Got: {setting.value}"

    # try posting just id
    client.post('/admin/settings/home', data={'meta_pixel_id': '123456789'}, follow_redirects=True)
    setting = SiteSetting.query.filter_by(key='meta_pixel_id').first()
    assert setting.value == '123456789', f"Failed! Got: {setting.value}"

    # try empty
    client.post('/admin/settings/home', data={'meta_pixel_id': ''}, follow_redirects=True)
    setting = SiteSetting.query.filter_by(key='meta_pixel_id').first()
    assert setting.value == '', f"Failed! Got: {setting.value}"

    print("All Meta Pixel tests passed successfully!")

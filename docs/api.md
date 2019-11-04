## URLS (routes)

<table>
<tr><td colspan="2">/classic</td><td rowspan="8">/data (JSON API)</td></tr>
<tr><td colspan="2">/captcha</td></tr>
<tr><td colspan="2">/tutorial</td></tr>
<tr><td colspan="2">/highscore</td></tr>
<tr><td colspan="2">/login</td></tr>
<tr><td colspan="2">/usersettings</td></tr>
<tr><td>/home</td><td>/</td></tr>
<tr><td colspan="2">/documentation</td></tr>
</table>

## GET

JSON
- images
- timelimit
- accepted tags
- joker (captcha)
- score
- user

Response
- 200
- 404

## POST

JSON
- tags (classic)
- skip
- joker (captcha)
- captcha (captcha)
- skip

Response
- 200
- 401 (user not playing or hasn't done tutorial/entry quiz)
- 400
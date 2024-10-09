## Installation
~~~bash
pip install git+https://github.com/adw3r/helpers
~~~


## Usage
~~~pycon
>>> from helpers import fake_mails
>>> response = await fake_mails.OneSecMail.gen_random_mailboxes(1)
<Response [200 OK]>
>>>response.json()
['9jpj02@dpptd.com']
~~~

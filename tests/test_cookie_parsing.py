import sys

sys.path.insert(0, '.')

from checkin import parse_cookies


def test_parse_cookies_from_string():
	"""Test parsing cookies from a cookie string"""
	cookie_string = "session=abc123; acw_tc=xyz789; cdn_sec_tc=def456; acw_sc__v2=ghi012"
	result = parse_cookies(cookie_string)

	assert isinstance(result, dict)
	assert result['session'] == 'abc123'
	assert result['acw_tc'] == 'xyz789'
	assert result['cdn_sec_tc'] == 'def456'
	assert result['acw_sc__v2'] == 'ghi012'


def test_parse_cookies_from_dict():
	"""Test parsing cookies from a dict"""
	cookies_dict = {
		'session': 'abc123',
		'acw_tc': 'xyz789',
	}
	result = parse_cookies(cookies_dict)

	assert isinstance(result, dict)
	assert result == cookies_dict


def test_parse_cookies_empty_string():
	"""Test parsing empty cookie string"""
	result = parse_cookies("")
	assert result == {}


def test_parse_cookies_single_cookie():
	"""Test parsing a single cookie"""
	result = parse_cookies("session=abc123")
	assert result == {'session': 'abc123'}


def test_parse_cookies_with_spaces():
	"""Test parsing cookies with spaces"""
	cookie_string = "session = abc123 ; acw_tc = xyz789"
	result = parse_cookies(cookie_string)

	assert result['session'] == 'abc123'
	assert result['acw_tc'] == 'xyz789'


def test_parse_cookies_with_special_characters():
	"""Test parsing cookies with special characters in values"""
	# Base64-encoded value
	cookie_string = "session=MTc4MzY1MDI2N3xEWDhFQVFMX2dBQUJFQVFRQUFEX3hfLUFBQVlHYzNSeWFXNW5EQWdBQm5OMFlYUjFjd05wYm5RRUFnQUNCbk4wY21sdVp3d0hBQVZuY201MWNBWnpkSEpwYm1jTUNRQVhaR1ZtWVhWc2RBWnpkSEpwYm1jTURRQUxiMkYxZEdoZmMzUmhkR1VHYzNSeWFXNW5EQTRBRERWSGFXNVpTRmg2WmtSMGFBWnpkSEpwYm1jTUJBQUNhV1FEYVc1MEJBVUFfUVpMTmdaemRISnBibWNNQ2dBSWRYTmxjbTVoYldVR2MzUnlhVzVuREJBQURteHBiblY0Wkc5Zk1qQTJNak0wQm5OMGNtbHVad3dHQUFSeWIyeGxBMmx1ZEFRQ0FBST04or0NyyuaiIvecxI6iai9zQU2XkFpvIgDQh6R2UmzY=; acw_tc=9b66b4aa17836021"
	result = parse_cookies(cookie_string)

	assert 'session' in result
	assert 'acw_tc' in result
	assert result['session'].startswith('MTc4MzY1MDI2N3x')


def test_parse_cookies_invalid_input():
	"""Test parsing invalid input"""
	result = parse_cookies(None)
	assert result == {}

	result = parse_cookies(123)
	assert result == {}


if __name__ == '__main__':
	test_parse_cookies_from_string()
	print("[PASS] test_parse_cookies_from_string")

	test_parse_cookies_from_dict()
	print("[PASS] test_parse_cookies_from_dict")

	test_parse_cookies_empty_string()
	print("[PASS] test_parse_cookies_empty_string")

	test_parse_cookies_single_cookie()
	print("[PASS] test_parse_cookies_single_cookie")

	test_parse_cookies_with_spaces()
	print("[PASS] test_parse_cookies_with_spaces")

	test_parse_cookies_with_special_characters()
	print("[PASS] test_parse_cookies_with_special_characters")

	test_parse_cookies_invalid_input()
	print("[PASS] test_parse_cookies_invalid_input")

	print("\nAll tests passed!")

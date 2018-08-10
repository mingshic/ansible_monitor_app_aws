
def test(test, test1):
	print test
	print test1

test('hostgroup.get',
                                {"output": "extend","filter": {'name': '1name'}})


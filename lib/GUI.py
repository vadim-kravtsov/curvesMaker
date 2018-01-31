import sys
def progressBar(value, endvalue, bar_length=20):
	if endvalue != 0:
		percent = float(value) / endvalue
		arrow = '-' * int(round(percent * bar_length)-1) + '>'
		spaces = ' ' * (bar_length - len(arrow))
		sys.stdout.write("\rProgress: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
		sys.stdout.flush()
	else:
		percent = 1
		arrow = '-' * int(round(percent * bar_length)-1) + '>'
		spaces = ' ' * (bar_length - len(arrow))
		sys.stdout.write("\rProgress: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
		sys.stdout.flush()
